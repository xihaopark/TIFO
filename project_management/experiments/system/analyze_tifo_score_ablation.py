#!/usr/bin/env python3
"""Summarize paired data/permuted/ones TIFO score controls."""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
SOURCE = RESULTS / "tifo_score_ablation.json"
OUTPUT = RESULTS / "tifo_score_ablation_paired.md"


def fmt(values):
    return f"{statistics.mean(values):.6f} ± {statistics.stdev(values):.6f}"


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    grouped = defaultdict(dict)
    for row in rows:
        marker = "score="
        method = row["method"]
        if marker not in method:
            raise ValueError(f"score mode missing from method label: {method}")
        mode = method.split(marker, 1)[1].split("]", 1)[0].split(",", 1)[0]
        grouped[row["dataset"]][(mode, row["seed"])] = row

    lines = [
        "# Paired TIFO score-conditioning ablation",
        "",
        "All configurations are frozen; the permuted control preserves each channel's score marginals while breaking frequency alignment.",
        "",
        "| Dataset | Mode | MSE mean ± std | Data-score paired wins | ΔMSE vs data |",
        "|---|---|---:|---:|---:|",
    ]
    for dataset, values in sorted(grouped.items()):
        seeds = sorted(seed for mode, seed in values if mode == "data")
        data = [values[("data", seed)]["mse"] for seed in seeds]
        for mode in ("data", "permuted", "ones"):
            current = [values[(mode, seed)]["mse"] for seed in seeds]
            delta = [current[i] - data[i] for i in range(len(seeds))]
            wins = "--" if mode == "data" else f"{sum(item > 0 for item in delta)}/{len(delta)}"
            lines.append(
                f"| {dataset} | {mode} | {fmt(current)} | {wins} | {fmt(delta) if mode != 'data' else '--'} |"
            )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
