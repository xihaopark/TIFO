#!/usr/bin/env python3
"""Build a small-effect WDAN+TIFO gate targeting both validation metrics."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_native_wdan_tifo_ettm2_h96.json"
OUTPUT = HERE / "tune_wdan_tifo_ettm2_dual_metric_h96.json"


def diagonal(gain: float, learning_rate_scale: float) -> dict:
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
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "wdan"]
    if len(controls) != 1:
        raise ValueError("source gate must contain exactly one matched WDAN control")
    control = controls[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = dict(control["model_args"])
    candidates = (
        ("g0p05_lr1", diagonal(0.05, 1.0)),
        ("g0p1_lr1", diagonal(0.1, 1.0)),
        ("g0p25_lr1", diagonal(0.25, 1.0)),
        ("g0p5_lr0p25", diagonal(0.5, 0.25)),
        ("g0p25_lr0p25", diagonal(0.25, 0.25)),
        ("g0p25_lr0p5", diagonal(0.25, 0.5)),
        ("g0p25_lr2", diagonal(0.25, 2.0)),
    )
    runs = [
        {
            **shared,
            "run_id": "wtdm_ettm2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": base_args,
        }
    ]
    for name, candidate in candidates:
        runs.append(
            {
                **shared,
                "run_id": f"wtdm_ettm2_h96_{name}_s2022",
                "method": "wdan_tifo",
                "model_args": {**base_args, **candidate},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm2_dual_metric_h96_gate_v1",
        "selection_rule": (
            "Evaluate the frozen seed-2022 validation checkpoint with sample-weighted "
            "MSE and MAE. A TIFO composition is eligible only if both metrics are "
            "strictly lower than the matched WDAN control; among eligible candidates, "
            "freeze the lowest validation MSE before three-seed final testing."
        ),
        "source_wdan_winner": source["wdan_validation_winner"],
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
