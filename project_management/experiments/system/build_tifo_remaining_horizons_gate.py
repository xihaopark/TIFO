#!/usr/bin/env python3
"""Build per-cell TIFO validation gates for horizons 192, 336, and 720."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_itransformer_remaining_horizons.json"
ETTM2_H192_SOURCE = HERE / "gate_ettm2_h192_two_backbones.json"
OUTPUT = HERE / "tune_tifo_remaining_horizons.json"

CANDIDATES = {
    "historical_default": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "historical_stable": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.5,
        "tifo_zero_pad_ratio": 0.0,
    },
    "historical_compact_zp1": {
        "filter_dim": 256,
        "tifo_variant": "historical",
        "tifo_dropout": 0.3,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "hermitian_aligned_zp1": {
        "filter_dim": 512,
        "tifo_variant": "hermitian_aligned",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "phase_pr0_lr0p25": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.0,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "phase_pr0p25_lr0p25": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.25,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "phase_pr0_lr1_zp1": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.0,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "phase_pr0p25_lr1_zp1": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.25,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ettm2_h192 = json.loads(ETTM2_H192_SOURCE.read_text(encoding="utf-8"))
    templates = [
        run
        for run in source["runs"]
        if run.get("method") == "ori" and run.get("seed") == 2022
    ]
    templates.extend(
        {**ettm2_h192["defaults"], **run}
        for run in ettm2_h192["runs"]
        if run.get("backbone") == "iTransformer"
        and run.get("method") == "ori"
        and run.get("seed") == 2022
    )
    runs = []
    for native in templates:
        shared = {
            key: value
            for key, value in native.items()
            if key not in {"run_id", "engine", "backbone", "method", "model_args"}
        }
        architecture = {
            key: value
            for key, value in native["model_args"].items()
            if not key.startswith("tifo_") and key != "filter_dim"
        }
        dataset_id = native["dataset"].lower()
        horizon = native["pred_len"]
        for name, candidate in CANDIDATES.items():
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_tifo_cell_{dataset_id}_h{horizon}_{name}_s2022"
                    ),
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "seed": 2022,
                    "model_args": {
                        **architecture,
                        **candidate,
                        "skip_final_test": True,
                    },
                }
            )
    output = {
        "protocol_id": "kdd_resubmit_tifo_remaining_horizons_gate_v1",
        "selection_rule": (
            "For each dataset-horizon cell, select one of eight declared TIFO "
            "candidates by seed-2022 validation MSE only; final test is disabled."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
