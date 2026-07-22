#!/usr/bin/env python3
"""Collect and summarize the frozen spectral-shift stress-test metrics."""

from __future__ import annotations

import csv
import glob
import json
import statistics
from pathlib import Path

import numpy as np

from run_spectral_shift_stress import ROOT, RUN_SPECS


STRENGTHS = (0.0, 0.25, 0.5, 1.0)
SEEDS = (2021, 2022, 2023)
OUTPUT_DIR = ROOT / "project_management/experiments/results"


def metrics_for(run_id: str, strength: float) -> tuple[float, float, str]:
    tag = str(strength).replace(".", "p")
    pattern = str(
        ROOT
        / "results"
        / f"long_term_forecast_{run_id}_*__spectral_high_s{tag}"
        / "metrics.npy"
    )
    matches = glob.glob(pattern)
    if len(matches) != 1:
        raise ValueError(f"expected one metrics file for {pattern}, found {matches}")
    metrics = np.load(matches[0])
    return float(metrics[1]), float(metrics[0]), matches[0]


def main() -> None:
    rows = []
    for dataset, methods in RUN_SPECS.items():
        for method, template in methods.items():
            for seed in SEEDS:
                run_id = template.format(seed=seed)
                for strength in STRENGTHS:
                    mse, mae, source = metrics_for(run_id, strength)
                    rows.append(
                        {
                            "dataset": dataset,
                            "method": method,
                            "seed": seed,
                            "strength": strength,
                            "mse": mse,
                            "mae": mae,
                            "source": source,
                        }
                    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "spectral_shift_stress.json").write_text(
        json.dumps(rows, indent=2) + "\n", encoding="utf-8"
    )
    with (OUTPUT_DIR / "spectral_shift_stress.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Controlled high-frequency shift stress test",
        "",
        "Upper-half non-DC rFFT bins are scaled coherently over each input/future window.",
        "",
        "| Dataset | Strength | Ori MSE | TIFO MSE | TIFO vs Ori |",
        "|---|---:|---:|---:|---:|",
    ]
    for dataset in RUN_SPECS:
        for strength in STRENGTHS:
            grouped = {
                method: [
                    row["mse"]
                    for row in rows
                    if row["dataset"] == dataset
                    and row["method"] == method
                    and row["strength"] == strength
                ]
                for method in ("ori", "tifo")
            }
            ori_mean = statistics.mean(grouped["ori"])
            tifo_mean = statistics.mean(grouped["tifo"])
            effect = (ori_mean - tifo_mean) / ori_mean * 100.0
            lines.append(
                f"| {dataset} | {strength:.2f} | "
                f"{ori_mean:.6f} +/- {statistics.stdev(grouped['ori']):.6f} | "
                f"{tifo_mean:.6f} +/- {statistics.stdev(grouped['tifo']):.6f} | "
                f"{effect:+.2f}% |"
            )
    output = "\n".join(lines) + "\n"
    (OUTPUT_DIR / "spectral_shift_stress.md").write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
