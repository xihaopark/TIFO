#!/usr/bin/env python3
"""Build a matched WDAN+TIFO validation gate for ETTm2/H96."""

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
    "native_wdan_h96_gate_v3.json"
)
OUTPUT = HERE / "tune_native_wdan_tifo_ettm2_h96.json"


def main() -> None:
    matrix = json.loads(WDAN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(WDAN_VALIDATION.read_text(encoding="utf-8"))
    candidates = [
        row
        for row in validation
        if row["dataset"] == "ETTm2" and int(row["pred_len"]) == 96
    ]
    if len(candidates) != 8:
        raise ValueError(f"ETTm2/H96: expected eight WDAN candidates, got {len(candidates)}")

    by_id = {run["run_id"]: run for run in matrix["runs"]}
    winner = min(candidates, key=lambda row: (row["validation_mse"], row["run_id"]))
    template = by_id[winner["run_id"]]
    shared = {
        key: value
        for key, value in template.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = {**template["model_args"], "skip_final_test": True}
    runs = [
        {
            **shared,
            "run_id": "wt_ettm2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": base_args,
        }
    ]
    for index, (name, candidate) in enumerate(TIFO_CANDIDATES.items()):
        runs.append(
            {
                **shared,
                # Keep the setting/checkpoint filename safely below filesystem limits.
                "run_id": f"wt_ettm2_h96_c{index}_s2022",
                "method": "wdan_tifo",
                "candidate_name": name,
                "model_args": {
                    **base_args,
                    "tifo_score_alignment": "raw",
                    **candidate,
                },
            }
        )

    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm2_h96_gate_v1",
        "selection_rule": (
            "For ETTm2/H96, rerun the frozen native-WDAN validation winner as "
            "a control and compare seven declared TIFO-before-WDAN configurations "
            "using seed-2022 validation MSE only. The iTransformer architecture "
            "and WDAN configuration remain fixed. Promote only a composition that "
            "beats the same-source WDAN control; final testing is disabled."
        ),
        "wdan_validation_winner": {
            "selected_run": winner["run_id"],
            "selected_validation_mse": winner["validation_mse"],
        },
        "defaults": matrix["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
