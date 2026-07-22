#!/usr/bin/env python3
"""Tune a mixed MSE/MAE objective for ETTm1 WDAN+TIFO."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
WDAN_MATRIX = Path(
    "/home/park/TS/FredNormer/project_management/experiments/system/"
    "tune_native_wdan_h96.json"
)
WDAN_VALIDATION = Path(
    "/home/park/TS/FredNormer/project_management/experiments/results/"
    "native_wdan_h96_gate_v3.json"
)
OUTPUT = HERE / "tune_wdan_tifo_ettm1_loss_h96.json"


def main() -> None:
    matrix = json.loads(WDAN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(WDAN_VALIDATION.read_text(encoding="utf-8"))
    rows = [
        row
        for row in validation
        if row["dataset"] == "ETTm1" and int(row["pred_len"]) == 96
    ]
    if len(rows) != 8:
        raise ValueError(f"ETTm1/H96: expected eight WDAN candidates, got {len(rows)}")
    winner = min(rows, key=lambda row: (row["validation_mse"], row["run_id"]))
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    template = by_id[winner["run_id"]]
    shared = {
        key: value
        for key, value in template.items()
        if key not in {"run_id", "method", "model_args"}
    }
    control_args = {**template["model_args"], "skip_final_test": True}
    tifo_args = {
        "tifo_score_alignment": "raw",
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    }
    weights = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 2.0)
    runs = [
        {
            **shared,
            "run_id": "wtloss_ettm1_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": control_args,
        }
    ]
    for index, weight in enumerate(weights):
        runs.append(
            {
                **shared,
                "run_id": f"wtloss_ettm1_h96_w{index}_s2022",
                "method": "wdan_tifo",
                "model_args": {
                    **control_args,
                    **tifo_args,
                    "mae_loss_weight": weight,
                },
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm1_loss_h96_gate_v1",
        "selection_rule": (
            "Keep the backbone, WDAN, and TIFO architecture fixed. Tune only the "
            "declared L1 weight added to MSE after the zero-weight final retained an "
            "MSE lead but missed MAE. Require both frozen validation metrics to beat "
            "the matched WDAN control before three-seed testing."
        ),
        "defaults": matrix["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
