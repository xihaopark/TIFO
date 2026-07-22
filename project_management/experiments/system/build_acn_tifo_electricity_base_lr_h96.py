#!/usr/bin/env python3
"""Tune base learning rate around the Electricity/H96 ACN+TIFO winner."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_acn_tifo_electricity_joint_h96.json"
OUTPUT = HERE / "tune_acn_tifo_electricity_base_lr_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    control = next(run for run in source["runs"] if run["method"] == "acn")
    template = next(
        run
        for run in source["runs"]
        if run["run_id"] == "joint_acnt_electricity_h96_t0p1_s2022"
    )
    learning_rates = (0.00030, 0.00040, 0.00045, 0.00050, 0.00055, 0.00060, 0.00070)
    runs = [
        {
            **{
                key: value
                for key, value in control.items()
                if key not in {"run_id", "model_args"}
            },
            "run_id": "baselr_acnt_electricity_h96_ctrl_s2022",
            "model_args": dict(control["model_args"]),
        }
    ]
    for index, learning_rate in enumerate(learning_rates):
        run = json.loads(json.dumps(template))
        run["run_id"] = f"baselr_acnt_electricity_h96_lr{index}_s2022"
        run["learning_rate"] = learning_rate
        runs.append(run)
    output = {
        "protocol_id": "kdd_resubmit_acn_tifo_electricity_base_lr_h96_gate_v1",
        "selection_rule": (
            "Keep the validation-best temperature and TIFO settings fixed and tune "
            "only base learning rate. Require sample-weighted validation MSE and MAE "
            "to beat the matched ACN control before freezing another final."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
