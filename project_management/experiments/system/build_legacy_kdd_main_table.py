#!/usr/bin/env python3
"""Render the submitted KDD main-table body from complete three-seed evidence.

The rendered rows retain the submitted table's column order:
PatchTST+TIFO, PatchTST Ori, iTransformer+TIFO, and iTransformer Ori.
Every rendered numerical value is wrapped in ``\\resubmitchange`` so it is
blue in the resubmission manuscript.  The script fails on incomplete cells;
it never falls back to submitted numbers.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "project_management" / "experiments" / "results"
DATASETS = ("ETTh1", "ETTh2", "ETTm1", "ETTm2", "Electricity", "Traffic", "Weather")
HORIZONS = (96, 192, 336, 720)
SEEDS = (2021, 2022, 2023)

# Later sources are intentional replacements only for the selected TIFO
# configuration; bare-backbone controls must still be directly reproduced.
SOURCES = (
    ("kdd_resubmit_patchtst_ett_all_horizons.csv", 10),
    ("kdd_resubmit_patchtst_ettm2_h96_gate.csv", 10),
    ("kdd_resubmit_ettm2_h192_two_backbones_gate.csv", 10),
    ("kdd_resubmit_patchtst_ettm2_h336_h720.csv", 10),
    ("kdd_resubmit_patchtst_custom_all_horizons.csv", 10),
    ("kdd_resubmit_h96_all_evidence.csv", 20),
    ("tifo_final_h96.csv", 30),
    ("tifo_hermitian_final_h96.csv", 30),
    ("tifo_electricity_weather_h96_final.csv", 30),
    # The H=96 cells have dedicated validation-selected final runs above.
    # This broader file supplies H=192/336/720 and is deliberately lower
    # priority should it also contain a duplicate H=96 configuration.
    ("tifo_itransformer_all_horizons_final.csv", 25),
    ("kdd_resubmit_itransformer_remaining_horizons.csv", 20),
)
PROMOTED_TIFO = {
    "tifo_final_h96.csv",
    "tifo_hermitian_final_h96.csv",
    "tifo_electricity_weather_h96_final.csv",
    "tifo_itransformer_all_horizons_final.csv",
}


def classify(label: str, source_name: str) -> tuple[str, str] | None:
    for backbone in ("PatchTST", "iTransformer"):
        if not label.startswith(backbone + "+"):
            continue
        if "+ORI" in label:
            return backbone, "Ori"
        if "+TIFO[historical]" in label:
            return backbone, "TIFO"
        if backbone == "iTransformer" and source_name in PROMOTED_TIFO and "+TIFO[" in label:
            return backbone, "TIFO"
    return None


def load() -> dict[tuple[str, str, str, int, int], tuple[float, float, int, str]]:
    values = {}
    for source_name, priority in SOURCES:
        path = RESULTS / source_name
        if not path.is_file():
            raise SystemExit(f"missing required result source: {path}")
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                kind = classify(row["method"], source_name)
                if kind is None:
                    continue
                backbone, method = kind
                key = (backbone, method, row["dataset"], int(row["pred_len"]), int(row["seed"]))
                value = (float(row["mse"]), float(row["mae"]), priority, source_name)
                existing = values.get(key)
                if existing is None or priority > existing[2]:
                    values[key] = value
                elif priority == existing[2] and value[:2] != existing[:2]:
                    raise SystemExit(f"conflicting equally ranked evidence for {key}: {existing[3]} vs {source_name}")
    return values


def summarize(values: dict, backbone: str, method: str, dataset: str) -> tuple[tuple[float, float], tuple[float, float]]:
    per_seed = []
    missing = []
    for seed in SEEDS:
        cells = []
        for horizon in HORIZONS:
            key = (backbone, method, dataset, horizon, seed)
            record = values.get(key)
            if record is None:
                missing.append(f"{backbone}+{method}/{dataset}/H{horizon}/s{seed}")
            else:
                cells.append(record[:2])
        if len(cells) == len(HORIZONS):
            per_seed.append(tuple(sum(cell[index] for cell in cells) / len(cells) for index in (0, 1)))
    if missing:
        raise SystemExit("incomplete evidence: " + "; ".join(missing))
    return tuple(
        (statistics.mean(metric), statistics.stdev(metric))
        for metric in zip(*per_seed)
    )


def number(value: tuple[float, float], best: bool) -> str:
    rendered = f"{value[0]:.3f} {{\\small $\\pm$ {value[1]:.3f}}}"
    if best:
        rendered = "\\textbf{" + rendered + "}"
    return "\\resubmitchange{" + rendered + "}"


def main() -> None:
    values = load()
    rows = ["% Generated from complete local three-seed evidence; do not edit numbers manually."]
    summaries = {}
    for dataset in DATASETS:
        for backbone in ("PatchTST", "iTransformer"):
            for method in ("TIFO", "Ori"):
                summaries[(backbone, method, dataset)] = summarize(values, backbone, method, dataset)
    for index, dataset in enumerate(DATASETS):
        cells = ["{" + dataset + "}"]
        for backbone in ("PatchTST", "iTransformer"):
            tifo = summaries[(backbone, "TIFO", dataset)]
            ori = summaries[(backbone, "Ori", dataset)]
            cells.extend((
                number(tifo[0], tifo[0][0] <= ori[0][0]),
                number(tifo[1], tifo[1][0] <= ori[1][0]),
                number(ori[0], ori[0][0] < tifo[0][0]),
                number(ori[1], ori[1][0] < tifo[1][0]),
            ))
        rows.append(" & ".join(cells) + r" \\")
        if index + 1 < len(DATASETS):
            rows.append(r"\midrule")
    output = RESULTS / "kdd_resubmit_legacy_main_table_rows.tex"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
