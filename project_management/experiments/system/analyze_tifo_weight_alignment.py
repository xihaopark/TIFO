#!/usr/bin/env python3
"""Measure alignment between TIFO stationarity scores and learned gains."""

from __future__ import annotations

import csv
import glob
import json
import statistics
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from utils.frequency_domain_filter import FrequencyDomainFilter  # noqa: E402


OUTPUT_DIR = ROOT / "project_management/experiments/results"
SPECS = {
    "ETTh1": {
        "run_prefix": "final_etth1_h96_tifo_hermitian",
        "variant": "hermitian_aligned",
        "filter_dim": 256,
        "dropout": 0.3,
        "zero_pad_ratio": 1.0,
    },
    "ETTm2": {
        "run_prefix": "final_ettm2_h96_tifo_hermitian",
        "variant": "hermitian_raw",
        "filter_dim": 512,
        "dropout": 0.5,
        "zero_pad_ratio": 0.0,
    },
}


def checkpoint_for(run_prefix: str, seed: int) -> Path:
    pattern = str(
        ROOT
        / "checkpoints"
        / f"long_term_forecast_{run_prefix}_s{seed}_*"
        / "checkpoint.pth"
    )
    matches = [Path(path) for path in glob.glob(pattern)]
    if len(matches) != 1:
        raise ValueError(f"expected one checkpoint for {pattern}, found {matches}")
    return matches[0]


def analyze(dataset: str, spec: dict, seed: int) -> dict:
    checkpoint = checkpoint_for(spec["run_prefix"], seed)
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    prefix = "filter."
    score = state[prefix + "stationarity_score"]
    args = SimpleNamespace(
        seq_len=96,
        enc_in=7,
        tifo_variant=spec["variant"],
        tifo_zero_pad_ratio=spec["zero_pad_ratio"],
        filter_dim=spec["filter_dim"],
        tifo_dropout=spec["dropout"],
        tifo_residual_alpha=1.0,
    )
    transform = FrequencyDomainFilter(args, score)
    transform.load_state_dict(
        {
            key.removeprefix(prefix): value
            for key, value in state.items()
            if key.startswith(prefix)
        }
    )
    transform.eval()
    with torch.no_grad():
        real_weight, imag_weight = transform.frequency_weights()
        gain = torch.sqrt((real_weight.square() + imag_weight.square()) / 2.0)

    score_array = score.flatten().numpy()
    gain_array = gain.flatten().numpy()
    lower = np.quantile(score_array, 0.25)
    upper = np.quantile(score_array, 0.75)
    low_gain = float(gain_array[score_array <= lower].mean())
    high_gain = float(gain_array[score_array >= upper].mean())
    return {
        "dataset": dataset,
        "seed": seed,
        "variant": spec["variant"],
        "spearman_score_gain": float(spearmanr(score_array, gain_array).statistic),
        "low_quartile_gain": low_gain,
        "high_quartile_gain": high_gain,
        "high_low_gain_ratio": high_gain / low_gain,
        "checkpoint": str(checkpoint),
    }


def main() -> None:
    rows = [
        analyze(dataset, spec, seed)
        for dataset, spec in SPECS.items()
        for seed in (2021, 2022, 2023)
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "tifo_weight_alignment.json").write_text(
        json.dumps(rows, indent=2) + "\n", encoding="utf-8"
    )
    with (OUTPUT_DIR / "tifo_weight_alignment.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Learned TIFO gain alignment",
        "",
        "Spearman correlation and high/low score-quartile gain ratio from the final three-seed checkpoints.",
        "",
        "| Dataset | Variant | Spearman mean +/- std | High/low gain ratio mean +/- std |",
        "|---|---|---:|---:|",
    ]
    for dataset, spec in SPECS.items():
        group = [row for row in rows if row["dataset"] == dataset]
        correlations = [row["spearman_score_gain"] for row in group]
        ratios = [row["high_low_gain_ratio"] for row in group]
        lines.append(
            f"| {dataset} | {spec['variant']} | "
            f"{statistics.mean(correlations):.3f} +/- {statistics.stdev(correlations):.3f} | "
            f"{statistics.mean(ratios):.3f} +/- {statistics.stdev(ratios):.3f} |"
        )
    (OUTPUT_DIR / "tifo_weight_alignment.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
