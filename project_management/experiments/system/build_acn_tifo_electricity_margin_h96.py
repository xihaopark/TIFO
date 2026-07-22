#!/usr/bin/env python3
"""Refine Electricity/H96 around the best ACN+TIFO validation cell."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_acn_tifo_electricity_joint_h96.json"
OUTPUT = HERE / "tune_acn_tifo_electricity_margin_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    control = next(run for run in source["runs"] if run["method"] == "acn")
    template = next(
        run
        for run in source["runs"]
        if run["run_id"] == "joint_acnt_electricity_h96_t0p1_s2022"
    )
    shared = {
        key: value
        for key, value in template.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = dict(template["model_args"])
    configs = (
        ("t0p085_lr0p25", 0.085, 0.25, 0.5),
        ("t0p09_lr0p25", 0.09, 0.25, 0.5),
        ("t0p10_lr0p15", 0.10, 0.15, 0.5),
        ("t0p10_lr0p40", 0.10, 0.40, 0.5),
        ("t0p10_lr1", 0.10, 1.00, 0.5),
        ("t0p11_lr0p25", 0.11, 0.25, 0.5),
        ("t0p12_lr0p25", 0.12, 0.25, 0.5),
    )
    runs = [
        {
            **{
                key: value
                for key, value in control.items()
                if key not in {"run_id", "model_args"}
            },
            "run_id": "margin_acnt_electricity_h96_ctrl_s2022",
            "model_args": dict(control["model_args"]),
        }
    ]
    for label, temperature, lr_scale, alpha in configs:
        model_args = {
            **base_args,
            "acn_temperature": temperature,
            "tifo_lr_scale": lr_scale,
            "tifo_residual_alpha": alpha,
        }
        runs.append(
            {
                **shared,
                "run_id": f"margin_acnt_electricity_h96_{label}_s2022",
                "method": "acn_tifo",
                "model_args": model_args,
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_electricity_margin_h96_gate_v1",
        "selection_rule": (
            "After the first frozen final missed ACN test MSE by 0.000176, refine "
            "only the local ACN-temperature/TIFO-learning-rate neighborhood. Require "
            "sample-weighted validation MSE and MAE to beat the matched ACN control."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
