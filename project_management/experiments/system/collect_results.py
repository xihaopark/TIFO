#!/usr/bin/env python3
"""Collect final-test metrics from experiment records and aggregate seeds."""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
METRIC_PATTERN = re.compile(
    r"mse:(?P<mse>[-+0-9.eE]+),\s*mae:(?P<mae>[-+0-9.eE]+)"
)
EPOCH_PATTERN = re.compile(r"Epoch:\s*(?P<epoch>\d+),\s*Steps:")


def method_label(record: dict) -> str:
    config = record["resolved_config"]
    if record["engine"] == "native":
        return f"{config['backbone']}+{config['method'].upper()}"
    return "TimeEmb" if record["engine"] == "timeemb" else "TFPS"


def parse_record(record_path: Path) -> dict | None:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("status") != "completed" or record.get("returncode") != 0:
        return None
    log_path = Path(record["log_file"])
    text = log_path.read_text(encoding="utf-8", errors="replace")
    metrics = list(METRIC_PATTERN.finditer(text))
    if not metrics:
        raise ValueError(f"completed run has no final metric: {record_path}")
    epochs = [int(match.group("epoch")) for match in EPOCH_PATTERN.finditer(text)]
    final = metrics[-1]
    config = record["resolved_config"]
    return {
        "protocol_id": record["protocol_id"],
        "run_id": record["run_id"],
        "engine": record["engine"],
        "method": method_label(record),
        "dataset": config["dataset"],
        "pred_len": int(config["pred_len"]),
        "seed": int(config["seed"]),
        "epochs_ran": max(epochs) if epochs else None,
        "mse": float(final.group("mse")),
        "mae": float(final.group("mae")),
        "physical_gpu": record.get("physical_gpu"),
        "dataset_sha256": record["dataset_sha256"],
        "log_file": str(log_path),
    }


def mean_std(values: list[float]) -> str:
    if len(values) == 1:
        return f"{values[0]:.6f}"
    return f"{statistics.mean(values):.6f} ± {statistics.stdev(values):.6f}"


def build_markdown(rows: list[dict]) -> str:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["pred_len"], row["method"])].append(row)

    lines = [
        "# Experiment result summary",
        "",
        "| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for (dataset, pred_len, method), group in sorted(grouped.items()):
        mse = [row["mse"] for row in group]
        mae = [row["mae"] for row in group]
        lines.append(
            f"| {dataset} | {pred_len} | {method} | {len(group)} | "
            f"{mean_std(mse)} | {mean_std(mae)} |"
        )

    ori = {row["seed"]: row for row in rows if row["method"].endswith("+ORI")}
    tifo = {row["seed"]: row for row in rows if row["method"].endswith("+TIFO")}
    paired_seeds = sorted(ori.keys() & tifo.keys())
    if paired_seeds:
        mse_delta = [tifo[seed]["mse"] - ori[seed]["mse"] for seed in paired_seeds]
        mae_delta = [tifo[seed]["mae"] - ori[seed]["mae"] for seed in paired_seeds]
        wins = sum(delta < 0 for delta in mse_delta)
        lines.extend(
            [
                "",
                "## Paired TIFO effect",
                "",
                f"Matched seeds: {', '.join(map(str, paired_seeds))}",
                "",
                f"- MSE delta (TIFO - Ori): {mean_std(mse_delta)}; wins: {wins}/{len(paired_seeds)}",
                f"- MAE delta (TIFO - Ori): {mean_std(mae_delta)}",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, help="protocol_id to collect")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "project_management/experiments/results",
    )
    args = parser.parse_args()

    rows = []
    for record_path in sorted((REPO_ROOT / "experiment_records").glob("*/launch.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("protocol_id") != args.protocol:
            continue
        row = parse_record(record_path)
        if row is not None:
            rows.append(row)
    if not rows:
        raise ValueError(f"no completed records found for protocol {args.protocol}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.protocol
    json_path = args.output_dir / f"{stem}.json"
    csv_path = args.output_dir / f"{stem}.csv"
    markdown_path = args.output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    markdown_path.write_text(build_markdown(rows), encoding="utf-8")
    print(f"collected {len(rows)} runs")
    print(markdown_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
