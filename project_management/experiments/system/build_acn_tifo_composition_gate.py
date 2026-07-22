#!/usr/bin/env python3
"""Build a validation-only gate for the explicitly ordered ACN+TIFO composition."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "plugin_baselines_h96_itransformer.json"
OUTPUT = HERE / "tune_acn_tifo_composition_h96.json"
TARGETS = {"ETTh1", "ETTm2", "Traffic"}

CANDIDATES = {
    "a0p10_fd256_lr0p25": {
        "filter_dim": 256, "tifo_dropout": 0.3,
        "tifo_residual_alpha": 0.10, "tifo_lr_scale": 0.25,
        "tifo_zero_pad_ratio": 0.0,
    },
    "a0p25_fd128_lr0p25": {
        "filter_dim": 128, "tifo_dropout": 0.1,
        "tifo_residual_alpha": 0.25, "tifo_lr_scale": 0.25,
        "tifo_zero_pad_ratio": 0.0,
    },
    "a0p25_fd256_lr0p25": {
        "filter_dim": 256, "tifo_dropout": 0.3,
        "tifo_residual_alpha": 0.25, "tifo_lr_scale": 0.25,
        "tifo_zero_pad_ratio": 0.0,
    },
    "a0p50_fd256_lr0p25": {
        "filter_dim": 256, "tifo_dropout": 0.3,
        "tifo_residual_alpha": 0.50, "tifo_lr_scale": 0.25,
        "tifo_zero_pad_ratio": 0.0,
    },
    "a0p25_fd512_lr0p125": {
        "filter_dim": 512, "tifo_dropout": 0.5,
        "tifo_residual_alpha": 0.25, "tifo_lr_scale": 0.125,
        "tifo_zero_pad_ratio": 0.0,
    },
    "a0p25_fd256_zpad1": {
        "filter_dim": 256, "tifo_dropout": 0.3,
        "tifo_residual_alpha": 0.25, "tifo_lr_scale": 0.25,
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for base in source["runs"]:
        if base.get("engine") != "acn" or base.get("dataset") not in TARGETS or base.get("seed") != 2022:
            continue
        shared = {key: value for key, value in base.items() if key not in {"run_id", "model_args"}}
        architecture = {**base["model_args"], "model": "iTransformer_ACN", "skip_final_test": True}
        dataset_id = base["dataset"].lower()
        runs.append({
            **shared,
            "run_id": f"gate_{dataset_id}_h96_acn_control_s2022",
            "model_args": {**architecture, "tifo_enabled": 0},
        })
        for name, candidate in CANDIDATES.items():
            runs.append({
                **shared,
                "run_id": f"gate_{dataset_id}_h96_acn_tifo_{name}_s2022",
                "model_args": {**architecture, "tifo_enabled": 1, **candidate},
            })
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_acn_tifo_composition_gate_h96_v1",
        "selection_rule": (
            "Within each dataset, compare ACN and ACN+TIFO by seed-2022 validation MSE only; "
            "the test split is disabled for every candidate. Composition order is per-window "
            "normalization, TIFO spectral adaptation, then the ACN forecasting encoder."
        ),
        "defaults": {**source["defaults"], "patience": 3},
        "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
