#!/usr/bin/env python3
"""Tune a mixed MSE/MAE objective for the ETTm2 WDAN+TIFO candidate."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_wdan_tifo_ettm2_dual_metric_h96.json"
OUTPUT = HERE / "tune_wdan_tifo_ettm2_loss_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = [run for run in source["runs"] if run["method"] == "wdan"]
    if len(controls) != 1:
        raise ValueError("source matrix must contain one matched WDAN control")
    control = controls[0]
    shared = {
        key: value
        for key, value in control.items()
        if key not in {"run_id", "method", "model_args"}
    }
    base_args = dict(control["model_args"])
    tifo_args = {
        "tifo_score_alignment": "raw",
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 0.25,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    }
    weights = (0.0, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
    runs = [
        {
            **shared,
            "run_id": "wtloss_ettm2_h96_ctrl_s2022",
            "method": "wdan",
            "model_args": base_args,
        }
    ]
    for index, weight in enumerate(weights):
        runs.append(
            {
                **shared,
                "run_id": f"wtloss_ettm2_h96_w{index}_s2022",
                "method": "wdan_tifo",
                "model_args": {
                    **base_args,
                    **tifo_args,
                    "mae_loss_weight": weight,
                },
            }
        )
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_ettm2_loss_h96_gate_v1",
        "selection_rule": (
            "Keep the backbone, WDAN, and TIFO architecture fixed. Tune only the "
            "declared L1 weight added to MSE. Evaluate frozen seed-2022 checkpoints "
            "with sample-weighted validation MSE and MAE; require both to beat the "
            "matched WDAN control before three-seed testing."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
