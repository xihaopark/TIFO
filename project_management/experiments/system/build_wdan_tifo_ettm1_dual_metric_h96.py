#!/usr/bin/env python3
"""Build a matched WDAN+TIFO dual-metric gate for ETTm1/H96."""

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
OUTPUT = HERE / "tune_wdan_tifo_ettm1_dual_metric_h96.json"


def diagonal(gain: float, learning_rate_scale: float = 1.0) -> dict:
    return {
        "tifo_score_alignment": "raw",
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": gain,
        "tifo_lr_scale": learning_rate_scale,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    }


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
    base_args = {**template["model_args"], "skip_final_test": True}
    candidates = (
        (
            "hist",
            {
                "tifo_score_alignment": "raw",
                "filter_dim": 512,
                "tifo_variant": "historical",
                "tifo_dropout": 0.5,
                "tifo_lr_scale": 0.25,
                "tifo_residual_alpha": 0.5,
                "tifo_zero_pad_ratio": 0.0,
            },
        ),
        ("g0p05_lr1", diagonal(0.05)),
        ("g0p1_lr1", diagonal(0.1)),
        ("g0p25_lr1", diagonal(0.25)),
        ("g0p5_lr1", diagonal(0.5)),
        ("g0p25_lr0p25", diagonal(0.25, 0.25)),
        ("g0p25_lr2", diagonal(0.25, 2.0)),
    )
    runs = [
        {
            **shared,
            "run_id": "wtdm_ettm1_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": base_args,
        }
    ]
    for name, tifo_args in candidates:
        runs.append(
            {
                **shared,
                "run_id": f"wtdm_ettm1_h96_{name}_s2022",
                "method": "wdan_tifo",
                "model_args": {**base_args, **tifo_args},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm1_dual_metric_h96_gate_v1",
        "selection_rule": (
            "Evaluate each frozen seed-2022 validation checkpoint with sample-weighted "
            "MSE and MAE. A TIFO composition is eligible only if both metrics are "
            "strictly lower than the matched WDAN control; among eligible candidates, "
            "freeze the lowest validation MSE before three-seed final testing."
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
