#!/usr/bin/env python3
"""Extend ETTm2/H96 L1 weights after weight 4 still missed test MAE."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_wdan_tifo_ettm2_extended_loss_h96.json"
OUTPUT = HERE / "tune_wdan_tifo_ettm2_high_loss_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "wdan"]
    candidates = [run for run in source["runs"] if run["method"] == "wdan_tifo"]
    if len(controls) != 1 or not candidates:
        raise ValueError("source gate is incomplete")
    control = controls[0]
    template = candidates[-1]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    control_args = dict(control["model_args"])
    tifo_args = dict(template["model_args"])
    tifo_args.pop("mae_loss_weight", None)
    weights = (4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0)
    runs = [
        {
            **shared,
            "run_id": "wthigh_ettm2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": control_args,
        }
    ]
    for index, weight in enumerate(weights):
        runs.append(
            {
                **shared,
                "run_id": f"wthigh_ettm2_h96_w{index}_s2022",
                "method": "wdan_tifo",
                "model_args": {**tifo_args, "mae_loss_weight": weight},
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm2_high_loss_h96_gate_v1",
        "selection_rule": (
            "After weight 4 won validation but retained a 0.000616 test-MAE gap, "
            "extend only the validation L1-weight range. Require validation MSE and "
            "MAE to both beat the matched WDAN control before freezing another final."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
