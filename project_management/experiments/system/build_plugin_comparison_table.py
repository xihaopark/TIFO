#!/usr/bin/env python3
"""Build the paper-facing H=96 plug-in table from completed run artifacts."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parents[1] / "results"
DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "Electricity", "Traffic", "Weather")
SEEDS = {2021, 2022, 2023}


def load(name: str) -> list[dict]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def select(rows: list[dict], dataset: str, method: str) -> list[dict]:
    chosen = [
        row for row in rows
        if row["dataset"] == dataset and row["method"] == method and row["pred_len"] == 96
    ]
    seeds = {row["seed"] for row in chosen}
    if seeds != SEEDS or len(chosen) != 3:
        raise SystemExit(f"{dataset}/{method}: expected seeds {sorted(SEEDS)}, got {sorted(seeds)}")
    return chosen


def stats(rows: list[dict], metric: str) -> tuple[float, float]:
    values = [float(row[metric]) for row in rows]
    return statistics.mean(values), statistics.stdev(values)


def fmt(value: tuple[float, float]) -> str:
    return f"{value[0]:.3f} {{\\small $\\pm$ {value[1]:.3f}}}"


def main() -> None:
    plugins = load("plugin_h96_final.json")
    historical = load("kdd_resubmit_h96_original_and_stabilized.json")
    tuned = load("tifo_final_h96.json")
    tuned_datasets = {row["dataset"] for row in tuned}

    markdown = [
        "# Recent plug-in comparison (H=96)", "",
        "Mean +/- sample standard deviation over seeds 2021/2022/2023.", "",
        "| Dataset | iTransformer | +ACN | +WDAN | +TIFO |",
        "|---|---:|---:|---:|---:|",
    ]
    tex = ["% Generated mechanically from completed three-seed artifacts."]
    wins = {method: 0 for method in ("Ori", "ACN", "WDAN", "TIFO")}
    improves = {method: 0 for method in ("ACN", "WDAN", "TIFO")}
    worst_relative = {method: float("inf") for method in improves}

    for dataset in DATASETS:
        groups = {
            "Ori": select(historical, dataset, "iTransformer+ORI"),
            "ACN": select(plugins, dataset, "ACN"),
            "WDAN": select(plugins, dataset, "WDAN"),
            "TIFO": select(
                tuned if dataset in tuned_datasets else historical,
                dataset,
                next(row["method"] for row in (tuned if dataset in tuned_datasets else historical)
                     if row["dataset"] == dataset and row["method"].startswith("iTransformer+TIFO[")
                     and (dataset in tuned_datasets or row["method"] == "iTransformer+TIFO[historical]")),
            ),
        }
        mse = {name: stats(rows, "mse") for name, rows in groups.items()}
        mae = {name: stats(rows, "mae") for name, rows in groups.items()}
        best_mse = min(value[0] for value in mse.values())
        best_mae = min(value[0] for value in mae.values())
        second_mse = sorted(value[0] for value in mse.values())[1]
        second_mae = sorted(value[0] for value in mae.values())[1]
        for name in groups:
            wins[name] += int(mse[name][0] == best_mse)
        for name in improves:
            relative = (mse["Ori"][0] - mse[name][0]) / mse["Ori"][0] * 100.0
            improves[name] += int(relative > 0)
            worst_relative[name] = min(worst_relative[name], relative)
        markdown.append(
            f"| {dataset} | {mse['Ori'][0]:.6f} / {mae['Ori'][0]:.6f} | "
            f"{mse['ACN'][0]:.6f} / {mae['ACN'][0]:.6f} | "
            f"{mse['WDAN'][0]:.6f} / {mae['WDAN'][0]:.6f} | "
            f"{mse['TIFO'][0]:.6f} / {mae['TIFO'][0]:.6f} |"
        )
        cells = []
        for name in ("Ori", "ACN", "WDAN", "TIFO"):
            mse_cell, mae_cell = fmt(mse[name]), fmt(mae[name])
            if mse[name][0] == best_mse:
                mse_cell = f"\\textbf{{{mse_cell}}}"
            elif mse[name][0] == second_mse:
                mse_cell = f"\\uline{{{mse_cell}}}"
            if mae[name][0] == best_mae:
                mae_cell = f"\\textbf{{{mae_cell}}}"
            elif mae[name][0] == second_mae:
                mae_cell = f"\\uline{{{mae_cell}}}"
            cells.extend((mse_cell, mae_cell))
        tex.append(f"{dataset} & " + " & ".join(cells) + r" \\")

    markdown.extend((
        "",
        "MSE wins: " + ", ".join(f"{key}={value}" for key, value in wins.items()),
        "Improves Ori (MSE): " + ", ".join(f"{key}={value}/7" for key, value in improves.items()),
        "Worst relative MSE change: "
        + ", ".join(f"{key}={value:+.1f}%" for key, value in worst_relative.items()),
    ))
    (RESULTS / "plugin_comparison_h96.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    (RESULTS / "plugin_comparison_h96_rows.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'plugin_comparison_h96.md'}")


if __name__ == "__main__":
    main()
