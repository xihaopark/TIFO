#!/usr/bin/env python3
"""Validate and launch a reproducible experiment matrix.

Dry-run is the default. Pass ``--execute`` to start jobs. Multiple physical
GPUs can be scheduled with ``--gpus`` and ``--max-parallel``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    "cpu_threads",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_snapshot(workdir: Path) -> dict[str, Any]:
    """Record the exact source state used by an experiment engine."""

    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return completed.stdout.strip()

    status = git("status", "--porcelain=v1", "--untracked-files=all")
    diff = git("diff", "--binary", "HEAD")
    return {
        "head": git("rev-parse", "HEAD"),
        "dirty": bool(status),
        "status": status.splitlines(),
        "tracked_diff_sha256": hashlib.sha256(diff.encode("utf-8")).hexdigest(),
    }


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

        python = Path(str(config.get("python", sys.executable))).expanduser()
        if not python.is_file() or not os.access(python, os.X_OK):
            raise FileNotFoundError(f"{run_id}: Python executable not found: {python}")

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
        # Do not resolve a venv's python symlink: invoking its resolved system
        # target bypasses the virtual environment and its installed packages.
        config["python"] = str(python.absolute())
        resolved.append(config)
    return resolved


def build_command(config: dict[str, Any], protocol_id: str) -> list[str]:
    engine = config["engine"]
    command = [config["python"], config["entrypoint"]]
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


def preflight_environment(resolved_runs: list[dict[str, Any]], physical_gpu: int) -> None:
    """Fail early on imports or an incompatible CUDA/PyTorch build."""
    checked: set[tuple[str, str]] = set()
    for config in resolved_runs:
        engine = config["engine"]
        key = (engine, config["python"])
        if key in checked:
            continue
        checked.add(key)
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = str(physical_gpu)
        completed = subprocess.run(
            [config["python"], config["entrypoint"], "--help"],
            cwd=config["workdir"],
            env=environment,
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

    checked_python: set[str] = set()
    cuda_probe = (
        "import torch; "
        "assert torch.cuda.is_available(); "
        "x=torch.randn(32,32,device='cuda',requires_grad=True); "
        "x.square().mean().backward(); "
        "print(torch.__version__, torch.cuda.get_device_name(0), "
        "torch.cuda.get_device_capability(0))"
    )
    for config in resolved_runs:
        python = config["python"]
        if python in checked_python:
            continue
        checked_python.add(python)
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = str(physical_gpu)
        completed = subprocess.run(
            [python, "-c", cuda_probe],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip().splitlines()[-1] if completed.stderr else "unknown error"
            raise RuntimeError(f"CUDA preflight failed for {python}: {detail}")
        print(f"CUDA preflight: {completed.stdout.strip()}")


def launch_record(
    config: dict[str, Any], protocol_id: str, command: list[str], status: str
) -> dict[str, Any]:
    engine_workdir = Path(config["workdir"])
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
        "orchestrator_source": git_snapshot(REPO_ROOT),
        "engine_source": git_snapshot(engine_workdir),
        "resolved_config": {
            key: value
            for key, value in config.items()
            if key not in {"workdir", "entrypoint", "dataset_file", "dataset_sha256"}
        },
    }


def execute_run(
    config: dict[str, Any], protocol_id: str, command: list[str], physical_gpu: int
) -> int:
    run_dir = REPO_ROOT / "experiment_records" / config["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    effective_config = dict(config)
    effective_config["gpu"] = physical_gpu
    record_path = run_dir / "launch.json"
    record = launch_record(effective_config, protocol_id, command, "running")
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["CUDA_VISIBLE_DEVICES"] = str(physical_gpu)
    cpu_threads = str(config.get("cpu_threads", 4))
    environment["OMP_NUM_THREADS"] = cpu_threads
    environment["MKL_NUM_THREADS"] = cpu_threads
    environment["OPENBLAS_NUM_THREADS"] = cpu_threads
    environment["PYTHONUNBUFFERED"] = "1"
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
    return completed.returncode


def execute_gpu_queue(
    physical_gpu: int,
    jobs: list[tuple[dict[str, Any], list[str]]],
    protocol_id: str,
) -> list[tuple[str, int]]:
    """Run one FIFO queue per GPU so two jobs never share a physical device."""

    results = []
    for config, command in jobs:
        returncode = execute_run(config, protocol_id, command, physical_gpu)
        print(f"finished {config['run_id']} on GPU {physical_gpu}: returncode={returncode}")
        results.append((config["run_id"], returncode))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="JSON experiment matrix")
    parser.add_argument("--execute", action="store_true", help="run jobs")
    parser.add_argument(
        "--gpus",
        default=None,
        help="comma-separated physical GPUs assigned round-robin (for example 0,1,2,3)",
    )
    parser.add_argument("--max-parallel", type=int, default=1, help="maximum concurrent jobs")
    parser.add_argument(
        "--only",
        default=None,
        help="comma-separated run_ids to select from the matrix",
    )
    parser.add_argument(
        "--skip-entrypoint-check",
        action="store_true",
        help="skip the per-engine import/argument-parser preflight",
    )
    args = parser.parse_args()

    matrix_path = args.matrix.resolve()
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    resolved_runs = validate(matrix)
    if args.only:
        selected_ids = {item.strip() for item in args.only.split(",") if item.strip()}
        known_ids = {config["run_id"] for config in resolved_runs}
        missing_ids = selected_ids - known_ids
        if missing_ids:
            raise ValueError(f"unknown --only run_ids: {sorted(missing_ids)}")
        resolved_runs = [config for config in resolved_runs if config["run_id"] in selected_ids]
        if not resolved_runs:
            raise ValueError("--only selected no runs")
    protocol_id = matrix["protocol_id"]
    if args.max_parallel < 1:
        raise ValueError("--max-parallel must be at least 1")
    if args.gpus:
        gpu_pool = [int(item.strip()) for item in args.gpus.split(",") if item.strip()]
        if not gpu_pool:
            raise ValueError("--gpus did not contain a GPU id")
    else:
        gpu_pool = [int(config.get("gpu", 0)) for config in resolved_runs]
    print(f"validated {len(resolved_runs)} runs for protocol {protocol_id}")
    if not args.skip_entrypoint_check:
        preflight_environment(resolved_runs, gpu_pool[0])

    jobs = []
    for index, config in enumerate(resolved_runs):
        command = build_command(config, protocol_id)
        physical_gpu = gpu_pool[index % len(gpu_pool)]
        print(f"\n[{config['run_id']}] gpu={physical_gpu} cwd={config['workdir']}")
        print(shlex.join(command))
        jobs.append((config, command, physical_gpu))
        if not args.execute:
            continue
    if not args.execute:
        return 0

    gpu_queues: dict[int, list[tuple[dict[str, Any], list[str]]]] = {}
    for config, command, gpu in jobs:
        gpu_queues.setdefault(gpu, []).append((config, command))

    failures = []
    with ThreadPoolExecutor(max_workers=min(args.max_parallel, len(gpu_queues))) as executor:
        futures = {
            executor.submit(execute_gpu_queue, gpu, gpu_jobs, protocol_id): gpu
            for gpu, gpu_jobs in gpu_queues.items()
        }
        for future in as_completed(futures):
            for run_id, returncode in future.result():
                if returncode != 0:
                    failures.append((run_id, returncode))
    if failures:
        for run_id, returncode in failures:
            print(
                f"run failed ({returncode}); see {REPO_ROOT / 'experiment_records' / run_id / 'run.log'}",
                file=sys.stderr,
            )
        return failures[0][1]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
