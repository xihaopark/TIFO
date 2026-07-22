#!/usr/bin/env python3
"""Jointly tune ACN temperature and backbone LR for ACN+TIFO on ETTm1/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_native_acn_tifo_h96.json"
OUTPUT = HERE / "joint_native_acn_tifo_ettm1_h96.json"

# name, ACN temperature, backbone learning rate
CANDIDATES = (
    ("t0p05_lr1em4", 0.05, 1.0e-4),
    ("t0p1_lr1em4", 0.10, 1.0e-4),
    ("t0p075_lr5em5", 0.075, 5.0e-5),
    ("t0p075_lr7p5em5", 0.075, 7.5e-5),
    ("t0p075_lr1p25em4", 0.075, 1.25e-4),
    ("t0p075_lr1p5em4", 0.075, 1.5e-4),
    ("t0p075_lr2em4", 0.075, 2.0e-4),
)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [
        run
        for run in source["runs"]
        if run["dataset"] == "ETTm1" and "_acn_control_" in run["run_id"]
    ]
    if len(controls) != 1:
        raise ValueError("expected one frozen ETTm1 ACN control")
    control = controls[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args", "learning_rate"}
    }
    base_args = dict(control["model_args"])
    base_args["skip_final_test"] = True
    runs = [
        {
            **shared,
            "run_id": "joint_acnt_ettm1_h96_control_s2022",
            "method": "acn",
            "learning_rate": 1.0e-4,
            "model_args": base_args,
        }
    ]
    for name, temperature, learning_rate in CANDIDATES:
        runs.append(
            {
                **shared,
                "run_id": f"joint_acnt_ettm1_h96_{name}_s2022",
                "method": "acn_tifo",
                "learning_rate": learning_rate,
                "model_args": {
                    **base_args,
                    "acn_temperature": temperature,
                    "tifo_variant": "hermitian_diagonal",
                    "tifo_prior_strength": 1.0,
                    "tifo_gain_limit": 0.5,
                    "tifo_lr_scale": 1.0,
                    "tifo_residual_alpha": 1.0,
                    "tifo_zero_pad_ratio": 0.0,
                },
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_acn_tifo_ettm1_joint_h96_gate_v1",
                "selection_rule": (
                    "For ETTm1/H96, rerun the frozen ACN winner and compare seven "
                    "declared ACN-temperature/backbone-LR configurations for "
                    "ACN+TIFO using seed-2022 validation MSE only."
                ),
                "defaults": source["defaults"],
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
