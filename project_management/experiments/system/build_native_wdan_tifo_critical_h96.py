#!/usr/bin/env python3
"""Build WDAN+TIFO gates for the two H=96 cells where WDAN blocks TIFO."""

from __future__ import annotations

import json
from pathlib import Path

from build_native_wdan_tifo_gate import TIFO_CANDIDATES


HERE = Path(__file__).resolve().parent
WDAN_MATRIX = Path(
    "/home/park/TS/FredNormer/project_management/experiments/system/"
    "tune_native_wdan_h96.json"
)
WDAN_VALIDATION = Path(
    "/home/park/TS/FredNormer/project_management/experiments/results/"
    "native_wdan_h96_partial.json"
)
OUTPUT = HERE / "tune_native_wdan_tifo_critical_h96.json"
TARGETS = ("ETTh1", "ETTh2")


def main() -> None:
    matrix = json.loads(WDAN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(WDAN_VALIDATION.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}

    winners = {}
    for dataset in TARGETS:
        rows = [
            row
            for row in validation
            if row["dataset"] == dataset and int(row["pred_len"]) == 96
        ]
        if len(rows) != 8:
            raise ValueError(f"{dataset}/H96: expected eight completed WDAN candidates")
        if any(row["run_id"] not in by_id for row in rows):
            raise ValueError(f"{dataset}/H96: validation row is absent from WDAN matrix")
        winners[dataset] = min(
            rows, key=lambda row: (row["validation_mse"], row["run_id"])
        )

    runs = []
    for dataset in TARGETS:
        winner = winners[dataset]
        template = by_id[winner["run_id"]]
        shared = {
            key: value
            for key, value in template.items()
            if key not in {"run_id", "method", "model_args"}
        }
        base_args = dict(template["model_args"])
        base_args["skip_final_test"] = True
        dataset_id = dataset.lower()
        runs.append(
            {
                **shared,
                "run_id": (
                    f"gate_native_wdan_tifo_critical_{dataset_id}_h96_"
                    "wdan_control_s2022"
                ),
                "method": "wdan",
                "model_args": base_args,
            }
        )
        for name, candidate in TIFO_CANDIDATES.items():
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"gate_native_wdan_tifo_critical_{dataset_id}_h96_"
                        f"{name}_s2022"
                    ),
                    "method": "wdan_tifo",
                    "model_args": {
                        **base_args,
                        "tifo_score_alignment": "raw",
                        **candidate,
                    },
                }
            )

    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_native_wdan_tifo_critical_h96_gate_v1",
                "selection_rule": (
                    "For ETTh1/H96 and ETTh2/H96, rerun the frozen WDAN validation "
                    "winner as a control and compare seven declared TIFO-before-WDAN "
                    "configurations using seed-2022 validation MSE only. Promote a "
                    "composition only when it beats the same-source WDAN control."
                ),
                "wdan_validation_winners": {
                    dataset: {
                        "selected_run": row["run_id"],
                        "selected_validation_mse": row["validation_mse"],
                    }
                    for dataset, row in winners.items()
                },
                "defaults": matrix["defaults"],
                "runs": runs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
