#!/usr/bin/env python3
"""Normalize frozen ACN, WDAN, and per-dataset TIFO finals for the strict table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "Electricity", "Traffic", "Weather")
SEEDS = {2021, 2022, 2023}


def load(path: Path) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit(f"expected a JSON list: {path}")
    return rows


def normalize(rows: list[dict], dataset: str, method: str, host: str) -> list[dict]:
    chosen = [
        row
        for row in rows
        if row.get("dataset") == dataset and int(row.get("pred_len", -1)) == 96
    ]
    seeds = {int(row["seed"]) for row in chosen}
    if len(chosen) != 3 or seeds != SEEDS:
        raise SystemExit(
            f"{dataset}/{method}: expected seeds {sorted(SEEDS)}, got {sorted(seeds)}"
        )
    return [
        {
            "dataset": dataset,
            "pred_len": 96,
            "method": method,
            "seed": int(row["seed"]),
            "mse": float(row["mse"]),
            "mae": float(row["mae"]),
            "host": host,
            "source_protocol": row.get("protocol_id", "unknown"),
            "source_run_id": row.get("run_id", "unknown"),
        }
        for row in chosen
    ]


def parse_tifo_source(spec: str) -> tuple[str, str, Path]:
    parts = spec.split("=", 2)
    if len(parts) != 3:
        raise SystemExit("--tifo-source must be DATASET=HOST=PATH")
    dataset, host, path = parts
    if dataset not in DATASETS:
        raise SystemExit(f"unexpected TIFO dataset: {dataset}")
    return dataset, host, Path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acn", type=Path, required=True)
    parser.add_argument("--wdan", type=Path, required=True)
    parser.add_argument("--tifo-source", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    acn_rows = load(args.acn)
    wdan_rows = load(args.wdan)
    evidence = []
    for dataset in DATASETS:
        evidence.extend(normalize(acn_rows, dataset, "ACN", "iTransformer"))
        evidence.extend(normalize(wdan_rows, dataset, "WDAN", "iTransformer"))

    seen = set()
    for spec in args.tifo_source:
        dataset, host, path = parse_tifo_source(spec)
        if dataset in seen:
            raise SystemExit(f"duplicate TIFO source for {dataset}")
        seen.add(dataset)
        evidence.extend(normalize(load(path), dataset, "TIFO", host))
    if seen != set(DATASETS):
        raise SystemExit(f"missing TIFO sources: {sorted(set(DATASETS) - seen)}")

    method_order = {"TIFO": 0, "ACN": 1, "WDAN": 2}
    dataset_order = {dataset: index for index, dataset in enumerate(DATASETS)}
    evidence.sort(
        key=lambda row: (
            dataset_order[row["dataset"]],
            method_order[row["method"]],
            row["seed"],
        )
    )
    if len(evidence) != 63:
        raise SystemExit(f"expected 63 normalized records, got {len(evidence)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(evidence)} records to {args.output}")


if __name__ == "__main__":
    main()
