#!/usr/bin/env python3
"""Build the single two-backbone, four-horizon plug-in comparison table."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "Electricity", "Traffic", "Weather")
HORIZONS = (96, 192, 336, 720)
METHODS = {
    "DLinear": ("TIFO*", "TIFO", "SAN", "FAN", "RevIN", "ACN", "WDAN"),
    "iTransformer": ("TIFO*", "TIFO", "SAN", "FAN", "RevIN", "ACN", "WDAN"),
}
SOURCE_PRIORITY = {
    "source_paper_reported": 1,
    "submitted_manuscript_matched_run": 2,
    "local_matched_three_seed_final": 3,
    "local_validation_selected_final": 4,
}


def load(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise ValueError(f"{path}: expected a JSON list")
        rows.extend(value)
    return rows


def summarize(rows: list[dict]) -> dict[tuple[str, str, str, int], dict]:
    grouped: dict[tuple[str, str, str, int], list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["backbone"], row["method"], row["dataset"], int(row["pred_len"]))
        grouped[key].append(row)

    summary = {}
    for key, candidates in grouped.items():
        unknown = {row["source"] for row in candidates} - set(SOURCE_PRIORITY)
        if unknown:
            raise ValueError(f"{key}: unknown source classes {sorted(unknown)}")
        best_priority = max(SOURCE_PRIORITY[row["source"]] for row in candidates)
        chosen = [
            row for row in candidates
            if SOURCE_PRIORITY[row["source"]] == best_priority
        ]
        sources = {row["source"] for row in chosen}
        if len(sources) != 1:
            raise ValueError(f"{key}: ambiguous equally ranked sources {sorted(sources)}")
        summary[key] = {
            "mse": statistics.mean(float(row["mse"]) for row in chosen),
            "mae": statistics.mean(float(row["mae"]) for row in chosen),
            "source": next(iter(sources)),
            "n": len(chosen),
        }
    return summary


def rank_levels(values: dict[str, dict], metric: str) -> dict[str, int]:
    """Rank at the same three-decimal precision shown to the reader.

    Methods that are tied at the displayed precision receive the same
    formatting. The underline marks the second distinct displayed value.
    """

    displayed = {method: round(value[metric], 3) for method, value in values.items()}
    distinct = sorted(set(displayed.values()))
    best = distinct[0] if distinct else None
    second = distinct[1] if len(distinct) > 1 else None
    return {
        method: 1 if value == best else 2 if value == second else 0
        for method, value in displayed.items()
    }


def tex_number(value: float, rank_value: int) -> str:
    rendered = f"{value:.3f}"
    if rank_value == 1:
        return rf"\textbf{{{rendered}}}"
    if rank_value == 2:
        return rf"\uline{{{rendered}}}"
    return rendered


def render(summary: dict) -> tuple[str, str]:
    tex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Complete plug-in comparison obtained by retaining the submitted TIFO, TIFO*, RevIN, SAN, and FAN results and adding locally evaluated ACN and WDAN. Each cell is MSE/MAE (lower is better). Bold and underline indicate the best and second-best result within the same backbone--dataset--horizon comparison or the $H=96$ average. TIFO* denotes TIFO used together with SAN, as in the submitted manuscript.}",
        r"\label{table:full_plugin_comparison}",
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{0.91}",
        r"\begin{tabular}{cc|ccccccc}",
        r"\toprule",
    ]
    md = [
        "# Full plug-in comparison",
        "",
        "Each cell is MSE/MAE. TIFO* denotes TIFO used together with SAN.",
    ]

    for backbone_index, (backbone, methods) in enumerate(METHODS.items()):
        if backbone_index:
            tex.append(r"\midrule")
        tex.extend(
            (
                rf"\multicolumn{{9}}{{c}}{{\textbf{{{backbone}}}}} \\",
                r"Dataset & $H$ & TIFO* & TIFO & SAN & FAN & RevIN & ACN & WDAN \\",
                r"\midrule",
            )
        )
        md.extend(
            (
                "",
                f"## {backbone}",
                "",
                "| Dataset | H | TIFO* | TIFO | SAN | FAN | RevIN | ACN | WDAN |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            )
        )
        for dataset_index, dataset in enumerate(DATASETS):
            for horizon in HORIZONS:
                tex_cells = [dataset if horizon == 96 else "", str(horizon)]
                md_cells = [dataset, str(horizon)]
                available = {
                    method: summary[(backbone, method, dataset, horizon)]
                    for method in methods
                    if (backbone, method, dataset, horizon) in summary
                }
                mse_ranks = rank_levels(available, "mse")
                mae_ranks = rank_levels(available, "mae")
                for method in methods:
                    value = available.get(method)
                    if value is None:
                        tex_cells.append("--")
                        md_cells.append("--")
                        continue
                    tex_cells.append(
                        f"{tex_number(value['mse'], mse_ranks[method])}/"
                        f"{tex_number(value['mae'], mae_ranks[method])}"
                    )
                    md_cells.append(
                        f"{value['mse']:.3f}/{value['mae']:.3f}"
                    )
                tex.append(" & ".join(tex_cells) + r" \\")
                md.append("| " + " | ".join(md_cells) + " |")
            if dataset_index != len(DATASETS) - 1:
                tex.append(r"\addlinespace[1pt]")
        tex.append(r"\midrule")
        tex_cells = [r"Avg. ($H=96$)", "96"]
        md_cells = ["Avg. (H=96)", "96"]
        averages = {}
        for method in methods:
            values = [
                summary[(backbone, method, dataset, 96)]
                for dataset in DATASETS
                if (backbone, method, dataset, 96) in summary
            ]
            if len(values) == len(DATASETS):
                averages[method] = {
                    "mse": statistics.mean(value["mse"] for value in values),
                    "mae": statistics.mean(value["mae"] for value in values),
                }
        mse_ranks = rank_levels(averages, "mse")
        mae_ranks = rank_levels(averages, "mae")
        for method in methods:
            value = averages.get(method)
            if value is None:
                tex_cells.append("--")
                md_cells.append("--")
                continue
            tex_cells.append(
                f"{tex_number(value['mse'], mse_ranks[method])}/"
                f"{tex_number(value['mae'], mae_ranks[method])}"
            )
            md_cells.append(f"{value['mse']:.3f}/{value['mae']:.3f}")
        tex.append(" & ".join(tex_cells) + r" \\")
        md.append("| " + " | ".join(md_cells) + " |")
    tex.extend(
        (
            r"\bottomrule",
            r"\end{tabular}",
            r"\endgroup",
            r"\end{table*}",
        )
    )
    return "\n".join(tex) + "\n", "\n".join(md) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, nargs="+", required=True)
    parser.add_argument("--tex-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    tex, markdown = render(summarize(load(args.records)))
    args.tex_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.tex_output.write_text(tex, encoding="utf-8")
    args.markdown_output.write_text(markdown, encoding="utf-8")
    print(f"wrote {args.tex_output} and {args.markdown_output}")


if __name__ == "__main__":
    main()
