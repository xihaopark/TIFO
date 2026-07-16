#!/usr/bin/env python3
"""Inspect TIFO result directories without modifying experiment artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np


DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "ECL", "traffic", "weather")
MODELS = ("DLinear", "PatchTST", "iTransformer")
SETTING_RE = re.compile(
    r"^long_term_forecast_(?:r1stat_)?"
    r"(?P<dataset>ETTh1|ETTh2|ETTm1|ETTm2|ECL|traffic|weather)_"
    r"(?P<advertised_seq>\d+)_(?P<advertised_pred>\d+)_"
)
LENGTH_RE = re.compile(r"_sl(?P<seq>\d+)_ll(?P<label>\d+)_pl(?P<pred>\d+)_")
MODEL_DATA_RE = re.compile(r"_(?P<model>DLinear|PatchTST|iTransformer)_(?P<data_type>[A-Za-z0-9]+)_ft")
SEED_RE = re.compile(r"_seed(?P<seed>\d+)_")


def parse_result(metrics_path: Path) -> dict[str, object]:
    setting = metrics_path.parent.name
    setting_match = SETTING_RE.search(setting)
    length_match = LENGTH_RE.search(setting)
    model_matches = list(MODEL_DATA_RE.finditer(setting))
    seed_match = SEED_RE.search(setting)
    metrics = np.load(metrics_path)

    errors: list[str] = []
    if not setting_match:
        errors.append("unparsed_dataset_or_advertised_lengths")
    if not length_match:
        errors.append("unparsed_effective_lengths")
    if not model_matches:
        errors.append("unparsed_model")
    if metrics.shape != (5,):
        errors.append(f"unexpected_metrics_shape={list(metrics.shape)}")

    row: dict[str, object] = {
        "setting": setting,
        "metrics_path": str(metrics_path),
        "dataset": setting_match.group("dataset") if setting_match else "unknown",
        "model": model_matches[-1].group("model") if model_matches else "unknown",
        "data_type": model_matches[-1].group("data_type") if model_matches else "unknown",
        "advertised_seq_len": int(setting_match.group("advertised_seq")) if setting_match else None,
        "advertised_pred_len": int(setting_match.group("advertised_pred")) if setting_match else None,
        "seq_len": int(length_match.group("seq")) if length_match else None,
        "label_len": int(length_match.group("label")) if length_match else None,
        "pred_len": int(length_match.group("pred")) if length_match else None,
        "seed": int(seed_match.group("seed")) if seed_match else None,
        "run_class": "r1stat" if "_r1stat_" in setting else "base",
        "mae": float(metrics[0]) if metrics.size >= 1 else None,
        "mse": float(metrics[1]) if metrics.size >= 2 else None,
        "rmse": float(metrics[2]) if metrics.size >= 3 else None,
        "mape": float(metrics[3]) if metrics.size >= 4 else None,
        "mspe": float(metrics[4]) if metrics.size >= 5 else None,
        "errors": errors,
    }

    if row["advertised_seq_len"] != row["seq_len"]:
        errors.append("advertised_seq_len_mismatch")
    if row["advertised_pred_len"] != row["pred_len"]:
        errors.append("advertised_pred_len_mismatch")
    return row


def build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    base_rows = [row for row in rows if row["run_class"] == "base"]
    seed_rows = [row for row in rows if row["run_class"] == "r1stat"]
    base_keys = Counter(
        (row["dataset"], row["model"], row["pred_len"]) for row in base_rows
    )
    expected = {
        (dataset, model, pred)
        for dataset in DATASETS
        for model in MODELS
        for pred in (96, 192, 336, 720)
    }
    observed = set(base_keys)
    duplicated = [list(key) + [count] for key, count in base_keys.items() if count != 1]
    anomaly_rows = [row["setting"] for row in rows if row["errors"]]

    return {
        "metrics_files": len(rows),
        "base_rows": len(base_rows),
        "explicit_seed_rows": len(seed_rows),
        "models": dict(sorted(Counter(str(row["model"]) for row in rows).items())),
        "datasets": dict(sorted(Counter(str(row["dataset"]) for row in rows).items())),
        "base_expected_cells": len(expected),
        "base_observed_cells": len(observed),
        "base_missing_cells": [list(key) for key in sorted(expected - observed)],
        "base_unexpected_cells": [list(key) for key in sorted(observed - expected)],
        "base_duplicate_cells": sorted(duplicated),
        "rows_with_naming_anomalies": anomaly_rows,
        "readiness": "historical_single_run_inventory_with_partial_seed_repeats",
    }


def emit_csv(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "dataset", "model", "run_class", "seed", "seq_len", "label_len",
        "pred_len", "advertised_seq_len", "advertised_pred_len", "mae", "mse",
        "rmse", "mape", "mspe", "data_type", "errors", "setting", "metrics_path",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        output = dict(row)
        output["errors"] = ";".join(str(value) for value in row["errors"])
        writer.writerow({key: output[key] for key in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--format", choices=("summary", "json", "csv"), default="summary")
    args = parser.parse_args()

    rows = [parse_result(path) for path in sorted(args.results.glob("*/metrics.npy"))]
    if not rows:
        print(f"No metrics.npy files found under {args.results}", file=sys.stderr)
        return 2

    if args.format == "csv":
        emit_csv(rows)
    elif args.format == "json":
        print(json.dumps({"summary": build_summary(rows), "rows": rows}, indent=2))
    else:
        print(json.dumps(build_summary(rows), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
