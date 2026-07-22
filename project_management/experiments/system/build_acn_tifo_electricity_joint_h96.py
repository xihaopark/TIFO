#!/usr/bin/env python3
"""Jointly tune ACN temperature/base LR with fixed TIFO on Electricity/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_acn_tifo_electricity_refine_h96.json"
OUTPUT = HERE / "tune_acn_tifo_electricity_joint_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "acn"]
    tifo_runs = [run for run in source["runs"] if run["method"] == "acn_tifo"]
    if len(controls) != 1 or not tifo_runs:
        raise ValueError("source gate is incomplete")
    control = controls[0]
    template = next(
        run for run in tifo_runs if run["run_id"].endswith("a0p5_lr0p25_s2022")
    )
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args", "learning_rate"}
    }
    control_args = dict(control["model_args"])
    tifo_args = dict(template["model_args"])
    candidates = (
        ("t0p025", 0.025, 5.0e-4),
        ("t0p05", 0.05, 5.0e-4),
        ("t0p1", 0.1, 5.0e-4),
        ("t0p2", 0.2, 5.0e-4),
        ("blr2p5", 0.075, 2.5e-4),
        ("blr4", 0.075, 4.0e-4),
        ("blr6", 0.075, 6.0e-4),
    )
    runs = [
        {
            **shared,
            "run_id": "joint_acnt_electricity_h96_ctrl_s2022",
            "method": "acn",
            "learning_rate": 5.0e-4,
            "model_args": control_args,
        }
    ]
    for name, temperature, learning_rate in candidates:
        model_args = {**tifo_args, "acn_temperature": temperature}
        runs.append(
            {
                **shared,
                "run_id": f"joint_acnt_electricity_h96_{name}_s2022",
                "method": "acn_tifo",
                "learning_rate": learning_rate,
                "model_args": model_args,
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_electricity_joint_h96_gate_v1",
        "selection_rule": (
            "Keep the iTransformer and TIFO architecture fixed. Jointly tune only "
            "ACN temperature or the base learning rate using seed-2022 validation. "
            "Require sample-weighted validation MSE and MAE to both beat the matched "
            "ACN control before a three-seed final."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
