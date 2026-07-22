#!/usr/bin/env python3
"""Freeze critical WDAN+TIFO winners that beat matched WDAN controls."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
MATRIX = HERE / "tune_native_wdan_tifo_critical_h96.json"
VALIDATION = RESULTS / "native_wdan_tifo_critical_h96_gate.json"
OUTPUT = HERE / "final_native_wdan_tifo_critical_h96.json"
TARGETS = ("ETTh1", "ETTh2")
SEEDS = (2021, 2022, 2023)


def main() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    if len(validation) != 16 or {row["run_id"] for row in validation} != set(by_id):
        raise ValueError("critical WDAN+TIFO validation matrix is incomplete")

    selections = {}
    final_runs = []
    for dataset in TARGETS:
        rows = [row for row in validation if row["dataset"] == dataset]
        if len(rows) != 8:
            raise ValueError(f"{dataset}: expected one control plus seven candidates")
        controls = [row for row in rows if "_wdan_control_" in row["run_id"]]
        candidates = [row for row in rows if "_wdan_control_" not in row["run_id"]]
        if len(controls) != 1 or len(candidates) != 7:
            raise ValueError(f"{dataset}: invalid control/candidate split")
        control = controls[0]
        winner = min(candidates, key=lambda row: (row["validation_mse"], row["run_id"]))
        if winner["validation_mse"] >= control["validation_mse"]:
            continue
        selections[dataset] = {
            "selected_run": winner["run_id"],
            "selected_validation_mse": winner["validation_mse"],
            "control_run": control["run_id"],
            "control_validation_mse": control["validation_mse"],
        }
        template = by_id[winner["run_id"]]
        for seed in SEEDS:
            model_args = dict(template["model_args"])
            model_args.pop("skip_final_test", None)
            final_runs.append(
                {
                    **{
                        key: value
                        for key, value in template.items()
                        if key not in {"run_id", "seed", "model_args"}
                    },
                    "run_id": (
                        f"final_native_wdan_tifo_critical_{dataset.lower()}_h96_s{seed}"
                    ),
                    "seed": seed,
                    "model_args": model_args,
                }
            )

    if not final_runs:
        raise SystemExit("no critical WDAN+TIFO candidate beat its matched control")
    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_native_wdan_tifo_critical_h96_final_v1",
                "selection_rule": (
                    "For each critical cell, promote only the seed-2022 validation "
                    "winner when it beats the matched frozen WDAN control, then "
                    "evaluate seeds 2021, 2022, and 2023 without further selection."
                ),
                "validation_selection": selections,
                "defaults": matrix["defaults"],
                "runs": final_runs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"froze {len(selections)} critical cells into {len(final_runs)} runs")


if __name__ == "__main__":
    main()
