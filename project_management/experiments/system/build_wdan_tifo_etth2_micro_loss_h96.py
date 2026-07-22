#!/usr/bin/env python3
"""Refine very small L1 weights for ETTh2 WDAN+TIFO."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_wdan_tifo_etth2_loss_h96.json"
OUTPUT = HERE / "tune_wdan_tifo_etth2_micro_loss_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "wdan"]
    candidates = [run for run in source["runs"] if run["method"] == "wdan_tifo"]
    if len(controls) != 1 or not candidates:
        raise ValueError("source gate is incomplete")
    control = controls[0]
    template = candidates[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_control_args = dict(control["model_args"])
    base_tifo_args = dict(template["model_args"])
    base_tifo_args.pop("mae_loss_weight", None)
    weights = (0.0, 0.0001, 0.00025, 0.0005, 0.001, 0.0025, 0.005)
    runs = [
        {
            **shared,
            "run_id": "wtmicro_etth2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": base_control_args,
        }
    ]
    for index, weight in enumerate(weights):
        runs.append(
            {
                **shared,
                "run_id": f"wtmicro_etth2_h96_w{index}_s2022",
                "method": "wdan_tifo",
                "model_args": {**base_tifo_args, "mae_loss_weight": weight},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_etth2_micro_loss_h96_gate_v1",
        "selection_rule": (
            "Refine only very small L1 weights after the declared coarse gate showed "
            "that 0.01 was too large. Require sample-weighted validation MSE and MAE "
            "to both beat the matched WDAN control before final testing."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
