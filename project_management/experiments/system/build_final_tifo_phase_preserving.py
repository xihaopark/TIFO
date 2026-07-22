#!/usr/bin/env python3
"""Freeze validation-winning phase-preserving TIFO runs for final testing."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_tifo_phase_preserving_h96.json"
OUTPUT = HERE / "final_tifo_phase_preserving_h96.json"
SEEDS = (2021, 2022, 2023)

# Each winner is lower than the previously frozen seed-2022 validation MSE.
# Datasets without such a win remain on their previous frozen configuration.
WINNERS = {
    "ETTh1": (
        "tune_etth1_h96_tifo_phase_zp0p0_pr0p25_lr0p25_s2022",
        0.68916140,
        0.68983900,
    ),
    "ETTh2": (
        "tune_etth2_h96_tifo_phase_zp0p0_pr0p25_lr0p25_s2022",
        0.21903890,
        0.22083510,
    ),
    "ETTm2": (
        "tune_ettm2_h96_tifo_phase_zp0p0_pr0p25_lr0p25_s2022",
        0.13541950,
        0.13591400,
    ),
    "Traffic": (
        "tune_traffic_h96_tifo_phase_zp0p0_pr0p0_lr1p0_s2022",
        0.35338540,
        0.35593900,
    ),
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in source["runs"]}
    runs = []
    for dataset, (winner_id, winner_val, frozen_val) in WINNERS.items():
        if winner_val >= frozen_val:
            raise ValueError(f"{dataset}: winner does not beat frozen validation MSE")
        template = by_id[winner_id]
        for seed in SEEDS:
            model_args = dict(template["model_args"])
            model_args.pop("skip_final_test", None)
            runs.append(
                {
                    **{
                        key: value
                        for key, value in template.items()
                        if key not in {"run_id", "seed", "model_args"}
                    },
                    "run_id": f"final_{dataset.lower()}_h96_tifo_phase_s{seed}",
                    "seed": seed,
                    "model_args": model_args,
                }
            )
    output = {
        "protocol_id": "kdd_resubmit_tifo_phase_preserving_h96_final_v1",
        "selection_rule": (
            "Frozen before final testing from the lowest seed-2022 validation MSE "
            "only when it beat the dataset's previously frozen validation result."
        ),
        "validation_comparison": {
            dataset: {
                "selected_run": winner_id,
                "selected_validation_mse": winner_val,
                "previous_frozen_validation_mse": frozen_val,
            }
            for dataset, (winner_id, winner_val, frozen_val) in WINNERS.items()
        },
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
