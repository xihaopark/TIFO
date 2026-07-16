#!/usr/bin/env python3
"""Validate and launch a reproducible experiment matrix.

Dry-run is the default. Pass ``--execute`` to start jobs sequentially.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_SPECS = {
    "native": (REPO_ROOT, REPO_ROOT / "run.py"),
    "timeemb": (
        REPO_ROOT / "third_party/TimeEmb-official/TimeEmb-main",
        REPO_ROOT / "third_party/TimeEmb-official/TimeEmb-main/run.py",
    ),
    "tfps": (
        REPO_ROOT / "third_party/TFPS-official",
        REPO_ROOT / "third_party/TFPS-official/run_longExp.py",
    ),
}

COMMON_FLAGS = (
    "root_path",
    "data_path",
    "features",
    "seq_len",
    "label_len",
    "pred_len",
    "enc_in",
    "dec_in",
    "c_out",
    "train_epochs",
    "patience",
    "batch_size",
    "learning_rate",
    "num_workers",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cli_value(value: Any) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def append_flag(command: list[str], name: str, value: Any) -> None:
    if value is None:
        return
    flag = f"--{name}"
    if value is True:
        command.append(flag)
    elif value is not False:
        command.extend((flag, cli_value(value)))


def merged_config(defaults: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    config = dict(defaults)
    config.update({key: value for key, value in run.items() if key != "model_args"})
    config["model_args"] = dict(run.get("model_args", {}))
    return config


def validate(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    protocol_id = matrix.get("protocol_id")
    defaults = matrix.get("defaults")
    runs = matrix.get("runs")
    if not isinstance(protocol_id, str) or not protocol_id.strip():
        raise ValueError("protocol_id must be a non-empty string")
    if not isinstance(defaults, dict) or not isinstance(runs, list) or not runs:
        raise ValueError("matrix requires a defaults object and a non-empty runs list")

    resolved: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    for run in runs:
        if not isinstance(run, dict):
            raise ValueError("each run must be an object")
        config = merged_config(defaults, run)
        run_id = config.get("run_id")
        engine = config.get("engine")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("each run requires a non-empty run_id")
        if run_id in run_ids:
            raise ValueError(f"duplicate run_id: {run_id}")
        run_ids.add(run_id)
        if engine not in ENGINE_SPECS:
            raise ValueError(f"{run_id}: unsupported engine {engine!r}")
        if not isinstance(config.get("seed"), int):
            raise ValueError(f"{run_id}: seed must be an integer")
        if engine == "native" and config.get("method") not in {"ori", "tifo"}:
            raise ValueError(f"{run_id}: native method must be ori or tifo")

        root_path = Path(str(config.get("root_path", ""))).expanduser()
        data_path = root_path / str(config.get("data_path", ""))
        if not data_path.is_file():
            raise FileNotFoundError(f"{run_id}: dataset not found: {data_path}")
        workdir, entrypoint = ENGINE_SPECS[engine]
        if not entrypoint.is_file():
            raise FileNotFoundError(f"{run_id}: entrypoint not found: {entrypoint}")
        config["dataset_file"] = str(data_path.resolve())
        config["dataset_sha256"] = sha256(data_path)
        config["workdir"] = str(workdir)
        config["entrypoint"] = str(entrypoint)
        resolved.append(config)
    return resolved


def build_command(config: dict[str, Any], protocol_id: str) -> list[str]:
    engine = config["engine"]
    command = [sys.executable, config["entrypoint"]]
    command.extend(("--is_training", "1", "--model_id", config["run_id"]))
    command.extend(("--data", str(config.get("data_type", config["dataset"]))))
    command.extend(("--random_seed", str(config["seed"]), "--itr", "1"))
    command.extend(("--gpu", "0", "--des", protocol_id))

    if engine == "native":
        command.extend(("--task_name", "long_term_forecast"))
        command.extend(("--model", str(config["backbone"])))
        command.extend(("--method", str(config["method"])))
    else:
        default_model = "TimeEmb" if engine == "timeemb" else "PatchTST_MoE_cluster"
        command.extend(("--model", str(config["model_args"].get("model", default_model))))

    for name in COMMON_FLAGS:
        append_flag(command, name, config.get(name))
    for name, value in sorted(config["model_args"].items()):
        if name != "model":
            append_flag(command, name, value)
    return command


def preflight_entrypoints(resolved_runs: list[dict[str, Any]]) -> None:
    """Fail early when an upstream checkout cannot import in this environment."""
    checked: set[str] = set()
    for config in resolved_runs:
        engine = config["engine"]
        if engine in checked:
            continue
        checked.add(engine)
        completed = subprocess.run(
            [sys.executable, config["entrypoint"], "--help"],
            cwd=config["workdir"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip().splitlines()[-1] if completed.stderr else "unknown error"
            raise RuntimeError(f"{engine} entrypoint preflight failed: {detail}")
        print(f"entrypoint preflight: {engine} ok")


def launch_record(
    config: dict[str, Any], protocol_id: str, command: list[str], status: str
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "protocol_id": protocol_id,
        "run_id": config["run_id"],
        "engine": config["engine"],
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": config["workdir"],
        "command": command,
        "physical_gpu": config.get("gpu", 0),
        "dataset_file": config["dataset_file"],
        "dataset_sha256": config["dataset_sha256"],
        "resolved_config": {
            key: value
            for key, value in config.items()
            if key not in {"workdir", "entrypoint", "dataset_file", "dataset_sha256"}
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="JSON experiment matrix")
    parser.add_argument("--execute", action="store_true", help="run jobs sequentially")
    parser.add_argument(
        "--skip-entrypoint-check",
        action="store_true",
        help="skip the per-engine import/argument-parser preflight",
    )
    args = parser.parse_args()

    matrix_path = args.matrix.resolve()
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    resolved_runs = validate(matrix)
    protocol_id = matrix["protocol_id"]
    print(f"validated {len(resolved_runs)} runs for protocol {protocol_id}")
    if not args.skip_entrypoint_check:
        preflight_entrypoints(resolved_runs)

    records_root = REPO_ROOT / "experiment_records"
    for config in resolved_runs:
        command = build_command(config, protocol_id)
        print(f"\n[{config['run_id']}] cwd={config['workdir']}")
        print(shlex.join(command))
        if not args.execute:
            continue

        run_dir = records_root / config["run_id"]
        run_dir.mkdir(parents=True, exist_ok=True)
        record_path = run_dir / "launch.json"
        record = launch_record(config, protocol_id, command, "running")
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = str(config.get("gpu", 0))
        log_path = run_dir / "run.log"
        with log_path.open("w", encoding="utf-8") as log_handle:
            completed = subprocess.run(
                command,
                cwd=config["workdir"],
                env=environment,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                check=False,
            )
        record["status"] = "completed" if completed.returncode == 0 else "failed"
        record["returncode"] = completed.returncode
        record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        record["log_file"] = str(log_path)
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if completed.returncode != 0:
            print(f"run failed; see {log_path}", file=sys.stderr)
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
