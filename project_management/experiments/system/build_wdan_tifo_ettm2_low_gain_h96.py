#!/usr/bin/env python3
"""Tune a conservative TIFO gain for ETTm2/H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_wdan_tifo_ettm2_extended_loss_h96.json"
OUTPUT = HERE / "tune_wdan_tifo_ettm2_low_gain_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    control = next(run for run in source["runs"] if run["method"] == "wdan")
    template = next(run for run in source["runs"] if run["method"] == "wdan_tifo")
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    tifo_args = dict(template["model_args"])
    configs = (
        ("g0p02_w4", 0.02, 4.0),
        ("g0p05_w4", 0.05, 4.0),
        ("g0p10_w4", 0.10, 4.0),
        ("g0p15_w4", 0.15, 4.0),
        ("g0p20_w4", 0.20, 4.0),
        ("g0p05_w8", 0.05, 8.0),
        ("g0p10_w8", 0.10, 8.0),
    )
    runs = [
        {
            **shared,
            "run_id": "wtgain_ettm2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": dict(control["model_args"]),
        }
    ]
    for label, gain, weight in configs:
        runs.append(
            {
                **shared,
                "run_id": f"wtgain_ettm2_h96_{label}_s2022",
                "method": "wdan_tifo",
                "model_args": {
                    **tifo_args,
                    "tifo_gain_limit": gain,
                    "mae_loss_weight": weight,
                },
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm2_low_gain_h96_gate_v1",
        "selection_rule": (
            "After large L1 weights improved validation but not final-test MAE, tune "
            "only conservative TIFO gains while keeping the WDAN host fixed. Require "
            "sample-weighted validation MSE and MAE to beat the matched WDAN control."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
