#!/usr/bin/env python3
"""Audit how robust TIFO's H96 macro-MSE lead is to aggregation choices."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


RESULTS = Path(__file__).resolve().parents[1] / "results"
DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "Electricity", "Traffic", "Weather")
SEEDS = (2021, 2022, 2023)


def load(name: str) -> list[dict]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def by_seed(rows: list[dict], dataset: str, method_prefix: str) -> dict[int, float]:
    selected = [
        row
        for row in rows
        if row["dataset"] == dataset
        and row["pred_len"] == 96
        and row["method"].startswith(method_prefix)
    ]
    values = {int(row["seed"]): float(row["mse"]) for row in selected}
    if set(values) != set(SEEDS) or len(selected) != len(SEEDS):
        raise RuntimeError(f"incomplete rows for {dataset}/{method_prefix}: {sorted(values)}")
    return values


def main() -> None:
    plugins = load("plugin_h96_final.json")
    historical = load("kdd_resubmit_h96_original_and_stabilized.json")
    tuned = load("tifo_final_h96.json")
    hermitian = load("tifo_hermitian_final_h96.json")
    electricity_weather = load("tifo_electricity_weather_h96_final.json")

    tifo_sources = {
        **{dataset: historical for dataset in DATASETS},
        **{row["dataset"]: tuned for row in tuned},
        **{row["dataset"]: hermitian for row in hermitian},
        **{row["dataset"]: electricity_weather for row in electricity_weather},
    }
    acn = {dataset: by_seed(plugins, dataset, "ACN") for dataset in DATASETS}
    tifo = {
        dataset: by_seed(tifo_sources[dataset], dataset, "iTransformer+TIFO[")
        for dataset in DATASETS
    }

    dataset_rows = []
    for dataset in DATASETS:
        acn_mean = statistics.mean(acn[dataset].values())
        tifo_mean = statistics.mean(tifo[dataset].values())
        dataset_rows.append((dataset, acn_mean, tifo_mean, acn_mean - tifo_mean))

    seed_rows = []
    for seed in SEEDS:
        acn_macro = statistics.mean(acn[dataset][seed] for dataset in DATASETS)
        tifo_macro = statistics.mean(tifo[dataset][seed] for dataset in DATASETS)
        seed_rows.append((seed, acn_macro, tifo_macro, acn_macro - tifo_macro))

    loo_rows = []
    for omitted in DATASETS:
        retained = [dataset for dataset in DATASETS if dataset != omitted]
        acn_macro = statistics.mean(
            statistics.mean(acn[dataset].values()) for dataset in retained
        )
        tifo_macro = statistics.mean(
            statistics.mean(tifo[dataset].values()) for dataset in retained
        )
        loo_rows.append((omitted, acn_macro, tifo_macro, acn_macro - tifo_macro))

    acn_macro = statistics.mean(row[1] for row in dataset_rows)
    tifo_macro = statistics.mean(row[2] for row in dataset_rows)
    relative_lead = (acn_macro - tifo_macro) / acn_macro * 100.0
    positive_contributions = sum(max(row[3], 0.0) for row in dataset_rows)
    traffic_share = next(row[3] for row in dataset_rows if row[0] == "Traffic") / positive_contributions
    seed_wins = sum(row[3] > 0 for row in seed_rows)
    loo_wins = sum(row[3] > 0 for row in loo_rows)

    lines = [
        "# TIFO versus ACN H96 ranking robustness audit",
        "",
        "Date: 2026-07-22",
        "",
        "## Overall assessment: Share with caveats",
        "",
        f"TIFO's seven-dataset macro MSE is {tifo_macro:.6f}, compared with "
        f"{acn_macro:.6f} for ACN, a descriptive relative lead of {relative_lead:.2f}%. "
        f"The lead holds for {seed_wins}/3 seed-indexed macro averages. It is not "
        "a universal dataset-wise advantage or a controlled cross-engine significance result.",
        "",
        "## Dataset contributions",
        "",
        "Positive ACN-TIFO values favor TIFO.",
        "",
        "| Dataset | ACN MSE | TIFO MSE | ACN - TIFO |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        f"| {dataset} | {acn_value:.6f} | {tifo_value:.6f} | {difference:+.6f} |"
        for dataset, acn_value, tifo_value, difference in dataset_rows
    )
    lines.extend(
        [
            "",
            f"Traffic supplies {traffic_share * 100:.1f}% of the positive contributions "
            "to the absolute macro gap. This concentration must remain visible when the "
            "macro ranking is interpreted.",
            "",
            "## Seed-indexed macro check",
            "",
            "| Seed | ACN macro MSE | TIFO macro MSE | ACN - TIFO |",
            "|---:|---:|---:|---:|",
        ]
    )
    lines.extend(
        f"| {seed} | {acn_value:.6f} | {tifo_value:.6f} | {difference:+.6f} |"
        for seed, acn_value, tifo_value, difference in seed_rows
    )
    lines.extend(
        [
            "",
            "## Leave-one-dataset-out check",
            "",
            "| Omitted dataset | ACN macro MSE | TIFO macro MSE | ACN - TIFO |",
            "|---|---:|---:|---:|",
        ]
    )
    lines.extend(
        f"| {dataset} | {acn_value:.6f} | {tifo_value:.6f} | {difference:+.6f} |"
        for dataset, acn_value, tifo_value, difference in loo_rows
    )
    lines.extend(
        [
            "",
            f"TIFO remains ahead in {loo_wins}/7 leave-one-dataset-out summaries; "
            "omitting Traffic reverses the ordering.",
            "",
            "## Required reviewer-facing caveats",
            "",
            "- State that TIFO has the lowest observed seven-dataset macro-average MSE, "
            "not that it is universally or significantly superior to ACN.",
            "- Keep the within-engine paired-effect table as the causal plug-in comparison; "
            "absolute ACN and TIFO values come from different official engines.",
            "- Preserve the dataset rows and the negative Traffic paired case rather than "
            "showing only the aggregate ranking.",
            "- The final Electricity/Weather configuration was selected from eight "
            "validation-only candidates per dataset before the three final seeds were run.",
        ]
    )
    output = RESULTS / "plugin_ranking_robustness_h96.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
