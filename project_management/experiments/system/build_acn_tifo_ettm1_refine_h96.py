#!/usr/bin/env python3
"""Build a small-effect ACN+TIFO refinement gate for ETTm1/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_native_acn_tifo_h96.json"
OUTPUT = HERE / "refine_native_acn_tifo_ettm1_h96.json"


CANDIDATES = {
    "diag_gl0p05_lr0p25": {
        "tifo_gain_limit": 0.05,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
    },
    "diag_gl0p1_lr0p25": {
        "tifo_gain_limit": 0.1,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
    },
    "diag_gl0p25_lr0p25": {
        "tifo_gain_limit": 0.25,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
    },
    "diag_gl0p25_lr0p5": {
        "tifo_gain_limit": 0.25,
        "tifo_lr_scale": 0.5,
        "tifo_residual_alpha": 1.0,
    },
    "diag_gl0p5_lr0p5": {
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 0.5,
        "tifo_residual_alpha": 1.0,
    },
    "diag_gl0p5_lr1_a0p25": {
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 0.25,
    },
    "diag_gl0p5_lr1_a0p5": {
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 0.5,
    },
}


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
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = dict(control["model_args"])
    base_args["skip_final_test"] = True
    runs = [
        {
            **shared,
            "run_id": "refine_acnt_ettm1_h96_control_s2022",
            "method": "acn",
            "model_args": base_args,
        }
    ]
    for name, candidate in CANDIDATES.items():
        runs.append(
            {
                **shared,
                "run_id": f"refine_acnt_ettm1_h96_{name}_s2022",
                "method": "acn_tifo",
                "model_args": {
                    **base_args,
                    "tifo_variant": "hermitian_diagonal",
                    "tifo_prior_strength": 1.0,
                    "tifo_zero_pad_ratio": 0.0,
                    **candidate,
                },
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_acn_tifo_ettm1_refine_h96_gate_v1",
                "selection_rule": (
                    "For ETTm1/H96, rerun the frozen ACN winner and compare seven "
                    "declared small-effect ACN+TIFO configurations by seed-2022 "
                    "validation MSE only; promote only if a composition beats control."
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
