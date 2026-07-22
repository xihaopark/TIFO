#!/usr/bin/env python3
"""Build the paired ACN versus ACN+TIFO complementarity report."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
ACN_SOURCE = RESULTS / "plugin_h96_final.json"
COMPOSITION_SOURCE = RESULTS / "acn_tifo_composition_final.json"
MARKDOWN_OUTPUT = RESULTS / "acn_tifo_composition_paired.md"
TEX_OUTPUT = RESULTS / "acn_tifo_composition_paired_rows.tex"
EXPECTED_DATASETS = ("ETTh1", "ETTm2", "Traffic")
EXPECTED_SEEDS = (2021, 2022, 2023)


def fmt(values: list[float]) -> str:
    return f"{statistics.mean(values):.6f} ± {statistics.stdev(values):.6f}"


def tex_fmt(values: list[float]) -> str:
    return f"{statistics.mean(values):.6f} {{\\small $\\pm$ {statistics.stdev(values):.6f}}}"


def index(rows: list[dict], method: str) -> dict[tuple[str, int], dict]:
    selected = {}
    for row in rows:
        if row["method"] != method or row["dataset"] not in EXPECTED_DATASETS:
            continue
        if int(row["pred_len"]) != 96:
            raise ValueError(f"unexpected horizon in {row['run_id']}: {row['pred_len']}")
        key = (row["dataset"], int(row["seed"]))
        if key in selected:
            raise ValueError(f"duplicate result for {method}/{key}")
        selected[key] = row
    expected = {(dataset, seed) for dataset in EXPECTED_DATASETS for seed in EXPECTED_SEEDS}
    if set(selected) != expected:
        raise ValueError(
            f"incomplete {method} coverage: missing={sorted(expected - set(selected))}, "
            f"extra={sorted(set(selected) - expected)}"
        )
    return selected


def main() -> None:
    acn = index(json.loads(ACN_SOURCE.read_text(encoding="utf-8")), "ACN")
    composition = index(
        json.loads(COMPOSITION_SOURCE.read_text(encoding="utf-8")), "ACN+TIFO"
    )

    lines = [
        "# Paired ACN+TIFO complementarity result",
        "",
        "The composition order is normalization -> TIFO spectral adapter -> ACN encoder. "
        "All configurations were selected on validation seed 2022 and frozen before final testing.",
        "",
        "| Dataset | ACN MSE | ACN+TIFO MSE | Paired wins | Relative MSE reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    tex = ["% Generated paired ACN versus ACN+TIFO complementarity rows."]
    total_wins = 0
    total_pairs = 0
    for dataset in EXPECTED_DATASETS:
        acn_mse = [acn[(dataset, seed)]["mse"] for seed in EXPECTED_SEEDS]
        combined_mse = [composition[(dataset, seed)]["mse"] for seed in EXPECTED_SEEDS]
        for seed in EXPECTED_SEEDS:
            if acn[(dataset, seed)]["dataset_sha256"] != composition[(dataset, seed)]["dataset_sha256"]:
                raise ValueError(f"dataset hash mismatch for {dataset}/seed{seed}")
        deltas = [combined - baseline for baseline, combined in zip(acn_mse, combined_mse)]
        relative = [
            (baseline - combined) / baseline * 100.0
            for baseline, combined in zip(acn_mse, combined_mse)
        ]
        wins = sum(delta < 0 for delta in deltas)
        total_wins += wins
        total_pairs += len(deltas)
        lines.append(
            f"| {dataset} | {fmt(acn_mse)} | {fmt(combined_mse)} | "
            f"{wins}/{len(deltas)} | {fmt(relative)}% |"
        )
        tex.append(
            f"{dataset} & {tex_fmt(acn_mse)} & {tex_fmt(combined_mse)} & "
            f"{wins}/{len(deltas)} & {statistics.mean(relative):.2f}\\% \\\\"
        )
    lines.extend(
        (
            "",
            f"Across the preregistered matrix, ACN+TIFO wins {total_wins}/{total_pairs} paired seeds.",
            "The comparison supports complementarity with ACN; it does not replace the standalone TIFO row or establish complementarity with FilterNet.",
        )
    )
    MARKDOWN_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    TEX_OUTPUT.write_text("\n".join(tex) + "\n", encoding="utf-8")
    print(MARKDOWN_OUTPUT)
    print(TEX_OUTPUT)


if __name__ == "__main__":
    main()
