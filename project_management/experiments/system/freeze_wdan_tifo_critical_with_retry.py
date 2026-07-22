#!/usr/bin/env python3
"""Freeze critical WDAN+TIFO winners after substituting safe-ID retries."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
MATRIX = HERE / "tune_native_wdan_tifo_critical_h96.json"
ORIGINAL_VALIDATION = Path(
    "/tmp/tifo-wdan-critical-cells/project_management/experiments/results/"
    "native_wdan_tifo_critical_h96_gate.json"
)
RETRY_VALIDATION = RESULTS / "wdan_tifo_raw_retry_h96.json"
OUTPUT = HERE / "final_native_wdan_tifo_critical_h96.json"
TARGETS = ("ETTh1", "ETTh2")
SEEDS = (2021, 2022, 2023)


def main() -> None:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    original = json.loads(ORIGINAL_VALIDATION.read_text(encoding="utf-8"))
    retries = json.loads(RETRY_VALIDATION.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}

    selections = {}
    final_runs = []
    for dataset in TARGETS:
        original_rows = [row for row in original if row["dataset"] == dataset]
        retry_rows = [row for row in retries if row["dataset"] == dataset]
        if len(original_rows) != 7 or len(retry_rows) != 1:
            raise ValueError(
                f"{dataset}: expected seven original successes plus one safe-ID retry"
            )
        if any(row["run_id"] not in by_id for row in original_rows):
            raise ValueError(f"{dataset}: original validation row is absent from matrix")
        raw_templates = [
            run
            for run in matrix["runs"]
            if run["dataset"] == dataset
            and "_hermitian_raw_a0p5_lr0p25_" in run["run_id"]
        ]
        if len(raw_templates) != 1:
            raise ValueError(f"{dataset}: expected one original Hermitian-raw template")

        entries = [(row, by_id[row["run_id"]]) for row in original_rows]
        entries.append((retry_rows[0], raw_templates[0]))
        controls = [entry for entry in entries if "_wdan_control_" in entry[1]["run_id"]]
        candidates = [entry for entry in entries if "_wdan_control_" not in entry[1]["run_id"]]
        if len(controls) != 1 or len(candidates) != 7:
            raise ValueError(f"{dataset}: invalid control/candidate split after retry")
        control_row, _ = controls[0]
        winner_row, winner_template = min(
            candidates,
            key=lambda entry: (entry[0]["validation_mse"], entry[0]["run_id"]),
        )
        if winner_row["validation_mse"] >= control_row["validation_mse"]:
            continue

        selections[dataset] = {
            "selected_run": winner_row["run_id"],
            "selected_validation_mse": winner_row["validation_mse"],
            "control_run": control_row["run_id"],
            "control_validation_mse": control_row["validation_mse"],
            "candidate_count": 7,
            "retry_substitution": retry_rows[0]["run_id"],
        }
        for seed in SEEDS:
            model_args = dict(winner_template["model_args"])
            model_args.pop("skip_final_test", None)
            final_runs.append(
                {
                    **{
                        key: value
                        for key, value in winner_template.items()
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
                    "For each critical cell, replace the filesystem-name failure "
                    "with its exact safe-ID retry, select the lowest seed-2022 "
                    "validation MSE among seven candidates only when it beats the "
                    "matched WDAN control, then evaluate three frozen seeds."
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
