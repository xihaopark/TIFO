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
WDAN_METRIC_PATTERN = re.compile(
    r"Horizon Average:\s*MSE\s*(?P<mse>[-+0-9.eE]+),\s*MAE\s*(?P<mae>[-+0-9.eE]+)"
)
EPOCH_PATTERN = re.compile(r"Epoch:\s*(?P<epoch>\d+),\s*Steps:")


def method_label(record: dict) -> str:
    config = record["resolved_config"]
    if record["engine"] == "native":
        if config["method"] == "wdan_tifo":
            return f"{config['backbone']}+WDAN+TIFO"
        label = f"{config['backbone']}+{config['method'].upper()}"
        variant = config.get("model_args", {}).get("tifo_variant")
        if (
            config.get("method") == "tifo"
            and not variant
            and record.get("protocol_id") == "kdd_resubmit_gate_v1"
        ):
            variant = "identity_unregularized"
        if config.get("method") == "tifo" and variant:
            model_args = config.get("model_args", {})
            qualifiers = [variant]
            lr_scale = float(model_args.get("tifo_lr_scale", 1.0))
            residual_alpha = float(model_args.get("tifo_residual_alpha", 1.0))
            if lr_scale != 1.0:
                qualifiers.append(f"lr={lr_scale:g}")
            if residual_alpha != 1.0:
                qualifiers.append(f"alpha={residual_alpha:g}")
            score_mode = model_args.get("tifo_score_mode")
            if score_mode is not None:
                qualifiers.append(f"score={score_mode}")
            label += f"[{','.join(qualifiers)}]"
        return label
    labels = {"timeemb": "TimeEmb", "tfps": "TFPS", "acn": "ACN", "wdan": "WDAN"}
    label = labels[record["engine"]]
    if (
        record["engine"] == "acn"
        and config.get("model_args", {}).get("model", "iTransformer_ACN") == "iTransformer_ACN"
        and bool(config.get("model_args", {}).get("tifo_enabled", 0))
    ):
        return "ACN+TIFO"
    if (
        record["engine"] in {"acn", "wdan"}
        and config.get("model_args", {}).get("model") == "iTransformer"
    ):
        return f"{label}-engine Ori"
    return label


def parse_record(record_path: Path) -> dict | None:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("status") != "completed" or record.get("returncode") != 0:
        return None
    log_path = Path(record["log_file"])
    text = log_path.read_text(encoding="utf-8", errors="replace")
    pattern = WDAN_METRIC_PATTERN if record["engine"] == "wdan" else METRIC_PATTERN
    metrics = list(pattern.finditer(text))
    if not metrics:
        raise ValueError(f"completed run has no final metric: {record_path}")
    epochs = [int(match.group("epoch")) for match in EPOCH_PATTERN.finditer(text)]
    final = metrics[-1]
    config = record["resolved_config"]
    model_args = config.get("model_args", {})
    return {
        "protocol_id": record["protocol_id"],
        "run_id": record["run_id"],
        "engine": record["engine"],
        "method": method_label(record),
        "dataset": config["dataset"],
        "pred_len": int(config["pred_len"]),
        "seed": int(config["seed"]),
        "tifo_lr_scale": model_args.get("tifo_lr_scale"),
        "tifo_residual_alpha": model_args.get("tifo_residual_alpha"),
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

    pair_keys = sorted(
        {
            (row["dataset"], row["pred_len"], row["method"])
            for row in rows
            if "+TIFO" in row["method"]
        }
    )
    for dataset, pred_len, tifo_method in pair_keys:
        backbone = tifo_method.split("+TIFO", 1)[0]
        ori_method = f"{backbone}+ORI"
        ori = {
            row["seed"]: row
            for row in rows
            if row["dataset"] == dataset
            and row["pred_len"] == pred_len
            and row["method"] == ori_method
        }
        tifo = {
            row["seed"]: row
            for row in rows
            if row["dataset"] == dataset
            and row["pred_len"] == pred_len
            and row["method"] == tifo_method
        }
        paired_seeds = sorted(ori.keys() & tifo.keys())
        if not paired_seeds:
            continue
        mse_delta = [tifo[seed]["mse"] - ori[seed]["mse"] for seed in paired_seeds]
        mae_delta = [tifo[seed]["mae"] - ori[seed]["mae"] for seed in paired_seeds]
        wins = sum(delta < 0 for delta in mse_delta)
        relative = [
            (ori[seed]["mse"] - tifo[seed]["mse"]) / ori[seed]["mse"] * 100
            for seed in paired_seeds
        ]
        lines.extend(
            [
                "",
                f"## Paired effect: {dataset}/H{pred_len}/{tifo_method}",
                "",
                f"Matched seeds: {', '.join(map(str, paired_seeds))}",
                "",
                f"- MSE delta (TIFO - Ori): {mean_std(mse_delta)}; wins: {wins}/{len(paired_seeds)}",
                f"- Relative MSE reduction: {mean_std(relative)}%",
                f"- MAE delta (TIFO - Ori): {mean_std(mae_delta)}",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol",
        required=True,
        help="one protocol_id or a comma-separated set to combine",
    )
    parser.add_argument("--name", default=None, help="output stem for a combined report")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "project_management/experiments/results",
    )
    args = parser.parse_args()

    protocols = {item.strip() for item in args.protocol.split(",") if item.strip()}
    rows = []
    for record_path in sorted((REPO_ROOT / "experiment_records").glob("*/launch.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("protocol_id") not in protocols:
            continue
        row = parse_record(record_path)
        if row is not None:
            rows.append(row)
    if not rows:
        raise ValueError(f"no completed records found for protocols {sorted(protocols)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = args.name or (next(iter(protocols)) if len(protocols) == 1 else "combined_results")
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
