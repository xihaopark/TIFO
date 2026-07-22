#!/usr/bin/env python3
"""Build an ACN+TIFO strength refinement gate for Electricity/H96."""

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
OUTPUT = HERE / "tune_acn_tifo_electricity_refine_h96.json"


def historical(alpha: float, learning_rate_scale: float) -> dict:
    return {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": learning_rate_scale,
        "tifo_residual_alpha": alpha,
        "tifo_zero_pad_ratio": 0.0,
    }


def main() -> None:
    matrix = json.loads(ACN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(ACN_VALIDATION.read_text(encoding="utf-8"))
    rows = [
        row
        for row in validation
        if row["dataset"] == "Electricity" and int(row["pred_len"]) == 96
    ]
    if len(rows) != 8:
        raise ValueError(f"Electricity/H96: expected eight ACN candidates, got {len(rows)}")
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
        ("a0p25_lr0p25", historical(0.25, 0.25)),
        ("a0p5_lr0p1", historical(0.5, 0.1)),
        ("a0p5_lr0p25", historical(0.5, 0.25)),
        ("a0p5_lr0p5", historical(0.5, 0.5)),
        ("a0p5_lr1", historical(0.5, 1.0)),
        ("a0p75_lr0p25", historical(0.75, 0.25)),
        ("a1_lr0p25", historical(1.0, 0.25)),
    )
    runs = [
        {
            **shared,
            "run_id": "refine_acnt_electricity_h96_ctrl_s2022",
            "method": "acn",
            "model_args": base_args,
        }
    ]
    for name, tifo_args in candidates:
        runs.append(
            {
                **shared,
                "run_id": f"refine_acnt_electricity_h96_{name}_s2022",
                "method": "acn_tifo",
                "model_args": {**base_args, **tifo_args},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_electricity_refine_h96_gate_v1",
        "selection_rule": (
            "Keep the iTransformer architecture, ACN temperature, and training "
            "budget fixed. Compare seven declared TIFO strength/learning-rate "
            "settings against the matched ACN control using seed-2022 validation; "
            "a final candidate must improve both validation MSE and MAE."
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
