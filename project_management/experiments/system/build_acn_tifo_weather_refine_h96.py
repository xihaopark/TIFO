#!/usr/bin/env python3
"""Refine historical TIFO strength and learning rate for Weather/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "joint_native_acn_tifo_weather_h96.json"
OUTPUT = HERE / "tune_acn_tifo_weather_refine_h96.json"


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
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "acn"]
    if len(controls) != 1:
        raise ValueError("source matrix must contain exactly one ACN control")
    control = controls[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = dict(control["model_args"])
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
            "run_id": "refine_acnt_weather_h96_ctrl_s2022",
            "method": "acn",
            "model_args": base_args,
        }
    ]
    for name, tifo_args in candidates:
        runs.append(
            {
                **shared,
                "run_id": f"refine_acnt_weather_h96_{name}_s2022",
                "method": "acn_tifo",
                "model_args": {**base_args, **tifo_args},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_weather_refine_h96_gate_v1",
        "selection_rule": (
            "Keep the iTransformer architecture, ACN temperature, base learning "
            "rate, and budget fixed. Evaluate seed-2022 checkpoints with "
            "sample-weighted validation MSE and MAE; require both to beat the "
            "matched ACN control before freezing a three-seed final."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
