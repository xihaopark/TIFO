#!/usr/bin/env python3
"""Build round-one validation-only tuning runs for the three weak H96 cells."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_tifo_weak_h96_round1.json"
TARGETS = {"ETTh2", "ETTm1", "Traffic"}

CANDIDATES = {
    "stabilized": {},
    "zpad050": {"tifo_zero_pad_ratio": 0.5},
    "zpad100": {"tifo_zero_pad_ratio": 1.0},
    "zpad200": {"tifo_zero_pad_ratio": 2.0},
    "alpha025_zpad100": {"tifo_residual_alpha": 0.25, "tifo_zero_pad_ratio": 1.0},
    "alpha075_zpad100": {"tifo_residual_alpha": 0.75, "tifo_zero_pad_ratio": 1.0},
    "yamabuki_zpad100": {
        "filter_dim": 256,
        "tifo_dropout": 0.3,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "compact_stabilized_zpad100": {
        "filter_dim": 256,
        "tifo_dropout": 0.3,
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for native in source["runs"]:
        if (
            native.get("method") != "ori"
            or native.get("seed") != 2022
            or native.get("dataset") not in TARGETS
        ):
            continue
        shared = {
            key: value
            for key, value in native.items()
            if key not in {"run_id", "engine", "backbone", "method", "model_args"}
        }
        base_args = {
            **native["model_args"],
            "filter_dim": 512,
            "tifo_variant": "historical",
            "tifo_dropout": 0.5,
            "tifo_lr_scale": 0.25,
            "tifo_residual_alpha": 0.5,
            "tifo_zero_pad_ratio": 0.0,
            "skip_final_test": True,
        }
        dataset_id = native["dataset"].lower()
        for name, overrides in CANDIDATES.items():
            runs.append(
                {
                    **shared,
                    "run_id": f"tune_{dataset_id}_h96_tifo_r1_{name}_s2022",
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "seed": 2022,
                    "model_args": {**base_args, **overrides},
                }
            )
    matrix = {
        "protocol_id": "kdd_resubmit_tifo_weak_h96_round1_v1",
        "selection_rule": (
            "For each dataset independently, select the lowest validation MSE at seed 2022; "
            "the test split is disabled for every candidate."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
