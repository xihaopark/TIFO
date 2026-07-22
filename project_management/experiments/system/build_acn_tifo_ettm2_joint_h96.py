#!/usr/bin/env python3
"""Joint architecture/LR/temperature gate for ACN+TIFO on ETTm2/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_native_acn_tifo_h96.json"
OUTPUT = HERE / "joint_native_acn_tifo_ettm2_h96.json"

# name, d_model, d_ff, e_layers, backbone LR, ACN temperature
CANDIDATES = (
    ("base", 128, 128, 2, 1.0e-4, 0.025),
    ("dm256_lr2em4", 256, 256, 2, 2.0e-4, 0.025),
    ("dm256_lr1em4", 256, 256, 2, 1.0e-4, 0.025),
    ("dm512_lr1em4", 512, 512, 2, 1.0e-4, 0.025),
    ("lr1p5em4", 128, 128, 2, 1.5e-4, 0.025),
    ("lr2em4", 128, 128, 2, 2.0e-4, 0.025),
    ("temp0p05", 128, 128, 2, 1.0e-4, 0.05),
)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [
        run
        for run in source["runs"]
        if run["dataset"] == "ETTm2" and "_acn_control_" in run["run_id"]
    ]
    if len(controls) != 1:
        raise ValueError("expected one frozen ETTm2 ACN control")
    control = controls[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args", "learning_rate"}
    }
    control_args = dict(control["model_args"])
    control_args["skip_final_test"] = True
    runs = [
        {
            **shared,
            "run_id": "joint_acnt_ettm2_h96_control_s2022",
            "method": "acn",
            "learning_rate": 1.0e-4,
            "model_args": control_args,
        }
    ]
    for name, d_model, d_ff, e_layers, learning_rate, temperature in CANDIDATES:
        runs.append(
            {
                **shared,
                "run_id": f"joint_acnt_ettm2_h96_{name}_s2022",
                "method": "acn_tifo",
                "learning_rate": learning_rate,
                "model_args": {
                    **control_args,
                    "d_model": d_model,
                    "d_ff": d_ff,
                    "e_layers": e_layers,
                    "acn_temperature": temperature,
                    "tifo_variant": "hermitian_diagonal",
                    "tifo_prior_strength": 1.0,
                    "tifo_gain_limit": 1.0,
                    "tifo_lr_scale": 8.0,
                    "tifo_residual_alpha": 1.0,
                    "tifo_zero_pad_ratio": 0.0,
                },
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_acn_tifo_ettm2_joint_h96_gate_v1",
                "selection_rule": (
                    "For ETTm2/H96, rerun the frozen ACN winner and compare seven "
                    "declared architecture/backbone-LR/ACN-temperature configurations "
                    "for ACN+TIFO using seed-2022 validation MSE only."
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
