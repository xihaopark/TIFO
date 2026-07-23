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
    "DLinear": ("TIFO", "RevIN", "SAN", "FAN"),
    "iTransformer": ("TIFO", "RevIN", "SAN", "FAN", "ACN", "WDAN"),
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


def rank(values: dict[str, dict], metric: str) -> tuple[str | None, str | None]:
    ordered = sorted(
        ((method, value[metric]) for method, value in values.items()),
        key=lambda item: (item[1], item[0]),
    )
    return (
        ordered[0][0] if ordered else None,
        ordered[1][0] if len(ordered) > 1 else None,
    )


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
        r"\caption{Full standalone plug-in comparison across two architecturally distinct backbones and four prediction horizons. Each cell is MSE/MAE (lower is better). Bold and underline indicate the best and second-best result within the same backbone--dataset--horizon comparison. $\dagger$ denotes a source-paper-reported ACN/WDAN result; unmarked cells are local matched runs or values retained from the submitted matched table.}",
        r"\label{table:full_plugin_comparison}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{cc|cccc|cccccc}",
        r"\toprule",
        r"\multicolumn{2}{c|}{} & \multicolumn{4}{c|}{DLinear} & \multicolumn{6}{c}{iTransformer} \\",
        r"Dataset & $H$ & TIFO & RevIN & SAN & FAN & TIFO & RevIN & SAN & FAN & ACN & WDAN \\",
        r"\midrule",
    ]
    md = [
        "# Full standalone plug-in comparison",
        "",
        "Each cell is MSE/MAE. † marks a source-paper-reported value; a dash means that no compatible public or local result is available.",
        "",
        "| Dataset | H | DLinear+TIFO | +RevIN | +SAN | +FAN | iTransformer+TIFO | +RevIN | +SAN | +FAN | +ACN | +WDAN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset_index, dataset in enumerate(DATASETS):
        for horizon in HORIZONS:
            tex_cells = [dataset if horizon == 96 else "", str(horizon)]
            md_cells = [dataset, str(horizon)]
            for backbone, methods in METHODS.items():
                available = {
                    method: summary[(backbone, method, dataset, horizon)]
                    for method in methods
                    if (backbone, method, dataset, horizon) in summary
                }
                mse_ranks = rank(available, "mse")
                mae_ranks = rank(available, "mae")
                for method in methods:
                    value = available.get(method)
                    if value is None:
                        tex_cells.append("--")
                        md_cells.append("--")
                        continue
                    mse_rank = 1 if method == mse_ranks[0] else 2 if method == mse_ranks[1] else 0
                    mae_rank = 1 if method == mae_ranks[0] else 2 if method == mae_ranks[1] else 0
                    tex_cells.append(
                        f"{tex_number(value['mse'], mse_rank)}/{tex_number(value['mae'], mae_rank)}"
                        + (r"\textsuperscript{\dagger}" if value["source"] == "source_paper_reported" else "")
                    )
                    md_cells.append(
                        f"{value['mse']:.3f}/{value['mae']:.3f}"
                        + ("†" if value["source"] == "source_paper_reported" else "")
                    )
            tex.append(" & ".join(tex_cells) + r" \\")
            md.append("| " + " | ".join(md_cells) + " |")
        if dataset_index != len(DATASETS) - 1:
            tex.append(r"\midrule")
    tex.extend((r"\bottomrule", r"\end{tabular}}", r"\end{table*}"))
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
