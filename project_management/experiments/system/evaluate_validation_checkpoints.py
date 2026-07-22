#!/usr/bin/env python3
"""Evaluate frozen validation checkpoints with both MSE and MAE."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SETTING_PATTERN = re.compile(r">+start training : (.+?)>+")
METRIC_PATTERN = re.compile(
    r"VALIDATION_METRICS mse=(?P<mse>[0-9.]+) mae=(?P<mae>[0-9.]+) n=(?P<n>\d+)"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-root", type=Path, required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu", type=int, default=0)
    args = parser.parse_args()

    records = []
    for record_path in sorted(args.records_root.glob("*/launch.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        config = record.get("resolved_config", {})
        if (
            record.get("protocol_id") != args.protocol
            or record.get("status") != "completed"
            or record.get("returncode") != 0
            or config.get("dataset") != args.dataset
        ):
            continue
        log_path = Path(record["log_file"])
        match = SETTING_PATTERN.search(log_path.read_text(encoding="utf-8", errors="replace"))
        if match is None:
            raise ValueError(f"cannot locate checkpoint setting in {log_path}")
        checkpoint = Path(record["cwd"]) / "checkpoints" / match.group(1) / "checkpoint.pth"
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)

        command = list(record["command"])
        command[1] = str(REPO_ROOT / "run.py")
        training_index = command.index("--is_training") + 1
        command[training_index] = "0"
        command.extend(("--validation_metrics_checkpoint", str(checkpoint)))
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"validation evaluation failed for {record['run_id']}:\n{completed.stdout}"
            )
        metric = METRIC_PATTERN.search(completed.stdout)
        if metric is None:
            raise ValueError(f"validation metric marker missing for {record['run_id']}")
        records.append(
            {
                "protocol_id": args.protocol,
                "run_id": record["run_id"],
                "dataset": args.dataset,
                "pred_len": int(config["pred_len"]),
                "validation_mse": float(metric.group("mse")),
                "validation_mae": float(metric.group("mae")),
                "elements": int(metric.group("n")),
                "checkpoint": str(checkpoint),
            }
        )
        print(
            record["run_id"],
            records[-1]["validation_mse"],
            records[-1]["validation_mae"],
            flush=True,
        )

    if not records:
        raise SystemExit("no matching completed checkpoints")
    args.output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} rows to {args.output}")


if __name__ == "__main__":
    main()
