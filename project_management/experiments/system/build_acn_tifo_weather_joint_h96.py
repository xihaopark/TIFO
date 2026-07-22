#!/usr/bin/env python3
"""Build a cell-specific ACN+TIFO validation gate for Weather/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ACN_MATRIX = Path(
    "/home/park/TS/FredNormer/project_management/experiments/system/"
    "tune_native_acn_h96_v2.json"
)
ACN_VALIDATION = Path(
    "/home/park/TS/FredNormer/project_management/experiments/results/"
    "native_acn_h96_gate.json"
)
OUTPUT = HERE / "joint_native_acn_tifo_weather_h96.json"


def diagonal(gain: float, tifo_lr: float = 1.0) -> dict:
    return {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": gain,
        "tifo_lr_scale": tifo_lr,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    }


def main() -> None:
    matrix = json.loads(ACN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(ACN_VALIDATION.read_text(encoding="utf-8"))
    rows = [
        row
        for row in validation
        if row["dataset"] == "Weather" and int(row["pred_len"]) == 96
    ]
    if len(rows) != 8:
        raise ValueError(f"Weather/H96: expected eight ACN candidates, got {len(rows)}")
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
            1.0e-4,
            {
                "filter_dim": 512,
                "tifo_variant": "historical",
                "tifo_dropout": 0.5,
                "tifo_lr_scale": 0.25,
                "tifo_residual_alpha": 0.5,
                "tifo_zero_pad_ratio": 0.0,
            },
        ),
        ("diag_g0p5", 1.0e-4, diagonal(0.5)),
        ("diag_g0p25", 1.0e-4, diagonal(0.25)),
        ("diag_g0p1", 1.0e-4, diagonal(0.1)),
        ("diag_g0p5_tlr4", 1.0e-4, diagonal(0.5, 4.0)),
        ("diag_g0p5_blr1p5", 1.5e-4, diagonal(0.5)),
        ("diag_g0p5_blr2", 2.0e-4, diagonal(0.5)),
    )
    runs = [
        {
            **shared,
            "run_id": "joint_acnt_weather_h96_control_s2022",
            "method": "acn",
            "model_args": base_args,
        }
    ]
    for name, learning_rate, tifo_args in candidates:
        runs.append(
            {
                **shared,
                "run_id": f"joint_acnt_weather_h96_{name}_s2022",
                "method": "acn_tifo",
                "learning_rate": learning_rate,
                "model_args": {**base_args, **tifo_args},
            }
        )

    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_weather_joint_h96_gate_v1",
        "selection_rule": (
            "For Weather/H96, keep the iTransformer architecture and frozen ACN "
            "temperature fixed, then compare the same-source ACN control against "
            "seven declared TIFO configurations using seed-2022 validation MSE "
            "only. Promote only a composition that beats the control."
        ),
        "acn_validation_winner": {
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
