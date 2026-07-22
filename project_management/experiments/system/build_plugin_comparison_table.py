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
    hermitian = load("tifo_hermitian_final_h96.json")
    acn_controls = load("plugin_engine_controls_h96_v1.json")
    wdan_controls = load("wdan_engine_controls_h96.json")
    tuned_datasets = {row["dataset"] for row in tuned}
    hermitian_datasets = {row["dataset"] for row in hermitian}

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
    relative_effects = {method: [] for method in improves}
    aggregate = {
        method: {metric: {seed: [] for seed in SEEDS} for metric in ("mse", "mae")}
        for method in ("Ori", "ACN", "WDAN", "TIFO")
    }

    for dataset in DATASETS:
        if dataset in hermitian_datasets:
            tifo_source = hermitian
            tifo_method = next(
                row["method"]
                for row in hermitian
                if row["dataset"] == dataset
                and row["method"].startswith("iTransformer+TIFO[")
            )
        elif dataset in tuned_datasets:
            tifo_source = tuned
            tifo_method = next(
                row["method"]
                for row in tuned
                if row["dataset"] == dataset
                and row["method"].startswith("iTransformer+TIFO[")
            )
        else:
            tifo_source = historical
            tifo_method = "iTransformer+TIFO[historical]"

        groups = {
            "Ori": select(historical, dataset, "iTransformer+ORI"),
            "ACN": select(plugins, dataset, "ACN"),
            "WDAN": select(plugins, dataset, "WDAN"),
            "TIFO": select(tifo_source, dataset, tifo_method),
        }
        controls = {
            "ACN": select(acn_controls, dataset, "ACN-engine Ori"),
            "WDAN": select(wdan_controls, dataset, "WDAN-engine Ori"),
            "TIFO": groups["Ori"],
        }
        mse = {name: stats(rows, "mse") for name, rows in groups.items()}
        mae = {name: stats(rows, "mae") for name, rows in groups.items()}
        for name, rows in groups.items():
            for row in rows:
                aggregate[name]["mse"][row["seed"]].append(float(row["mse"]))
                aggregate[name]["mae"][row["seed"]].append(float(row["mae"]))
        best_mse = min(value[0] for value in mse.values())
        best_mae = min(value[0] for value in mae.values())
        second_mse = sorted(value[0] for value in mse.values())[1]
        second_mae = sorted(value[0] for value in mae.values())[1]
        for name in groups:
            wins[name] += int(mse[name][0] == best_mse)
        for name in improves:
            control_mse = stats(controls[name], "mse")[0]
            relative = (control_mse - mse[name][0]) / control_mse * 100.0
            relative_effects[name].append(relative)
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

    aggregate_stats = {}
    for name in ("Ori", "ACN", "WDAN", "TIFO"):
        aggregate_stats[name] = {}
        for metric in ("mse", "mae"):
            seed_averages = [
                statistics.mean(aggregate[name][metric][seed]) for seed in sorted(SEEDS)
            ]
            aggregate_stats[name][metric] = (
                statistics.mean(seed_averages), statistics.stdev(seed_averages)
            )
    best_avg_mse = min(aggregate_stats[name]["mse"][0] for name in aggregate_stats)
    best_avg_mae = min(aggregate_stats[name]["mae"][0] for name in aggregate_stats)
    second_avg_mse = sorted(aggregate_stats[name]["mse"][0] for name in aggregate_stats)[1]
    second_avg_mae = sorted(aggregate_stats[name]["mae"][0] for name in aggregate_stats)[1]
    markdown.append(
        "| **Macro avg.** | " + " | ".join(
            f"{aggregate_stats[name]['mse'][0]:.6f} / {aggregate_stats[name]['mae'][0]:.6f}"
            for name in ("Ori", "ACN", "WDAN", "TIFO")
        ) + " |"
    )
    aggregate_cells = []
    for name in ("Ori", "ACN", "WDAN", "TIFO"):
        mse_cell = fmt(aggregate_stats[name]["mse"])
        mae_cell = fmt(aggregate_stats[name]["mae"])
        if aggregate_stats[name]["mse"][0] == best_avg_mse:
            mse_cell = f"\\textbf{{{mse_cell}}}"
        elif aggregate_stats[name]["mse"][0] == second_avg_mse:
            mse_cell = f"\\uline{{{mse_cell}}}"
        if aggregate_stats[name]["mae"][0] == best_avg_mae:
            mae_cell = f"\\textbf{{{mae_cell}}}"
        elif aggregate_stats[name]["mae"][0] == second_avg_mae:
            mae_cell = f"\\uline{{{mae_cell}}}"
        aggregate_cells.extend((mse_cell, mae_cell))
    tex.extend((r"\midrule", "Macro avg. & " + " & ".join(aggregate_cells) + r" \\"))

    markdown.extend((
        "",
        "MSE wins: " + ", ".join(f"{key}={value}" for key, value in wins.items()),
        "",
        "## Paired plug-in effect within each official training engine",
        "",
        "| Plug-in | Improves own backbone | Mean relative MSE change | Worst relative MSE change | Across-dataset std |",
        "|---|---:|---:|---:|---:|",
    ))
    effect_tex = ["% Generated from paired plug-in/control runs within each engine."]
    effect_stats = {}
    for name in ("ACN", "WDAN", "TIFO"):
        values = relative_effects[name]
        effect_stats[name] = {
            "coverage": improves[name],
            "mean": statistics.mean(values),
            "worst": min(values),
            "std": statistics.stdev(values),
        }
        markdown.append(
            f"| {name} | {improves[name]}/7 | {effect_stats[name]['mean']:+.2f}% | "
            f"{effect_stats[name]['worst']:+.2f}% | {effect_stats[name]['std']:.2f} pp |"
        )

    best_coverage = max(value["coverage"] for value in effect_stats.values())
    best_mean = max(value["mean"] for value in effect_stats.values())
    best_worst = max(value["worst"] for value in effect_stats.values())
    best_std = min(value["std"] for value in effect_stats.values())

    def emphasize(text: str, condition: bool) -> str:
        return f"\\textbf{{{text}}}" if condition else text

    for name in ("ACN", "WDAN", "TIFO"):
        value = effect_stats[name]
        cells = (
            emphasize(f"{value['coverage']}/7", value["coverage"] == best_coverage),
            emphasize(f"{value['mean']:+.2f}\\%", value["mean"] == best_mean),
            emphasize(f"{value['worst']:+.2f}\\%", value["worst"] == best_worst),
            emphasize(f"{value['std']:.2f}", value["std"] == best_std),
        )
        effect_tex.append(f"{name} & " + " & ".join(cells) + r" \\")

    (RESULTS / "plugin_comparison_h96.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    (RESULTS / "plugin_comparison_h96_rows.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    (RESULTS / "plugin_effect_summary_h96_rows.tex").write_text(
        "\n".join(effect_tex) + "\n", encoding="utf-8"
    )
    print(f"wrote {RESULTS / 'plugin_comparison_h96.md'}")


if __name__ == "__main__":
    main()
