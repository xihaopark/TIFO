#!/usr/bin/env python3
"""Launch the runs of one or more config files in ``configs/``.

Each config file holds a list of fully specified runs (dataset, backbone,
method, lengths, seed and ``model_args``). This script turns each run into a
``python run.py ...`` command, prints it (dry run, the default) or executes it
with ``--execute``, and writes a launch record and log under
``experiment_records/<run_id>/``. Jobs are scheduled over the GPUs given with
``--gpus``; ``--jobs-per-gpu`` runs several jobs per GPU.

Examples::

    # list the commands of the main TIFO table
    python scripts/run_configs.py configs/main/tifo_final.json

    # run the three ETTh1/H96 iTransformer seeds on GPUs 0 and 1
    python scripts/run_configs.py configs/main/tifo_final.json \
        --filter backbone=iTransformer dataset=ETTh1 pred_len=96 --execute --gpus 0,1
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METRIC = re.compile(r"mse:([-+0-9.eE]+),\s*mae:([-+0-9.eE]+)")
COMMON_FLAGS = (
    "root_path", "data_path", "features", "seq_len", "label_len", "pred_len",
    "enc_in", "dec_in", "c_out", "train_epochs", "patience", "batch_size",
    "learning_rate", "num_workers",
)


def append_flag(command: list[str], name: str, value: Any) -> None:
    if value is None or value is False:
        return
    if value is True:
        command.append(f"--{name}")
    else:
        command.extend((f"--{name}", str(value)))


def build_command(run: dict[str, Any], protocol_id: str, python: str) -> list[str]:
    command = [python, str(ROOT / "run.py"),
               "--is_training", "1", "--model_id", run["run_id"],
               "--data", str(run.get("data_type", run["dataset"])),
               "--random_seed", str(run["seed"]), "--itr", "1",
               "--gpu", "0", "--des", protocol_id,
               "--task_name", "long_term_forecast",
               "--model", str(run["backbone"]), "--method", str(run["method"])]
    for name in COMMON_FLAGS:
        append_flag(command, name, run.get(name))
    append_flag(command, "cpu_threads", run.get("cpu_threads", 4))
    for name, value in sorted(run.get("model_args", {}).items()):
        append_flag(command, name, value)
    return command


def load_runs(paths: list[Path], filters: list[str]) -> list[tuple[str, dict[str, Any]]]:
    wanted = dict(f.split("=", 1) for f in filters)
    selected = []
    for path in paths:
        config = json.loads(path.read_text())
        for run in config["runs"]:
            if all(str(run.get(k, run.get("model_args", {}).get(k))) == v for k, v in wanted.items()):
                selected.append((run.get("protocol_id", config["protocol_id"]), run))
    ids = [run["run_id"] for _, run in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate run_id across the selected config files")
    return selected


def completed(run_id: str) -> bool:
    launch = ROOT / "experiment_records" / run_id / "launch.json"
    return launch.is_file() and json.loads(launch.read_text()).get("status") == "completed"


def execute(protocol_id: str, run: dict[str, Any], gpu: str, python: str) -> str:
    record_dir = ROOT / "experiment_records" / run["run_id"]
    record_dir.mkdir(parents=True, exist_ok=True)
    log_file = record_dir / "run.log"
    command = build_command(run, protocol_id, python)
    record = {"protocol_id": protocol_id, "run_id": run["run_id"], "status": "running",
              "cwd": str(ROOT), "command": command, "resolved_config": run,
              "log_file": str(log_file), "started_at_utc": datetime.now(timezone.utc).isoformat()}
    (record_dir / "launch.json").write_text(json.dumps(record, indent=1))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu, PYTHONHASHSEED="0")
    with log_file.open("w") as handle:
        rc = subprocess.run(command, cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT).returncode
    found = METRIC.findall(log_file.read_text(errors="replace"))
    record.update(status="completed" if rc == 0 else "failed", returncode=rc,
                  finished_at_utc=datetime.now(timezone.utc).isoformat())
    if found:
        record["test_mse"], record["test_mae"] = map(float, found[-1])
    (record_dir / "launch.json").write_text(json.dumps(record, indent=1))
    return f"{run['run_id']}: rc={rc}" + (f" mse={record['test_mse']:.6f} mae={record['test_mae']:.6f}" if found else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("configs", nargs="+", type=Path, help="config JSON files under configs/")
    parser.add_argument("--filter", nargs="*", default=[], metavar="KEY=VALUE",
                        help="keep runs whose field (or model_args field) equals VALUE, e.g. dataset=ETTh1 seed=2021")
    parser.add_argument("--execute", action="store_true", help="run the jobs (default: print commands only)")
    parser.add_argument("--gpus", default="0", help="comma-separated GPU ids")
    parser.add_argument("--jobs-per-gpu", type=int, default=1)
    parser.add_argument("--skip-completed", action="store_true", help="skip runs with a completed launch record")
    parser.add_argument("--python", default=sys.executable, help="interpreter used for run.py")
    args = parser.parse_args()

    runs = load_runs(args.configs, args.filter)
    if args.skip_completed:
        runs = [(p, r) for p, r in runs if not completed(r["run_id"])]
    print(f"{len(runs)} runs selected", flush=True)
    if not args.execute:
        for protocol_id, run in runs:
            print(" ".join(build_command(run, protocol_id, args.python)))
        return 0

    jobs: queue.Queue = queue.Queue()
    for item in runs:
        jobs.put(item)

    def worker(gpu: str) -> None:
        while True:
            try:
                protocol_id, run = jobs.get_nowait()
            except queue.Empty:
                return
            print(execute(protocol_id, run, gpu, args.python), flush=True)

    threads = [threading.Thread(target=worker, args=(g.strip(),))
               for g in args.gpus.split(",") for _ in range(args.jobs_per_gpu)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
