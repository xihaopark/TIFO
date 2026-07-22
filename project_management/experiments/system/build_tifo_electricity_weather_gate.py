#!/usr/bin/env python3
"""Build the final validation-only TIFO gate for untuned H96 datasets."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_tifo_electricity_weather_h96.json"
TARGETS = {"Electricity", "Weather"}

# This compact gate covers the controls that helped other datasets while keeping
# the previously reported configuration as an explicit validation comparator.
CANDIDATES = {
    "historical_control": {},
    "lr0p25": {"tifo_lr_scale": 0.25},
    "alpha0p5": {"tifo_residual_alpha": 0.5},
    "zpad100": {"tifo_zero_pad_ratio": 1.0},
    "lr0p25_alpha0p5": {
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.5,
    },
    "lr0p25_alpha0p5_zpad100": {
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.5,
        "tifo_zero_pad_ratio": 1.0,
    },
    "compact_zpad100": {
        "filter_dim": 256,
        "tifo_dropout": 0.3,
        "tifo_zero_pad_ratio": 1.0,
    },
    "hermitian_aligned_zpad100": {
        "tifo_variant": "hermitian_aligned",
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for native in source["runs"]:
        dataset = native.get("dataset")
        if (
            native.get("method") != "ori"
            or native.get("seed") != 2022
            or dataset not in TARGETS
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
            "tifo_lr_scale": 1.0,
            "tifo_residual_alpha": 1.0,
            "tifo_zero_pad_ratio": 0.0,
            "skip_final_test": True,
        }
        dataset_id = dataset.lower()
        for name, overrides in CANDIDATES.items():
            runs.append(
                {
                    **shared,
                    "run_id": f"tune_{dataset_id}_h96_tifo_ew_{name}_s2022",
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "seed": 2022,
                    "model_args": {**base_args, **overrides},
                }
            )
    matrix = {
        "protocol_id": "kdd_resubmit_tifo_electricity_weather_h96_gate_v1",
        "selection_rule": (
            "For Electricity and Weather independently, select the lowest seed-2022 "
            "validation MSE. The test split is disabled for all candidates. Run final "
            "seeds 2021/2022/2023 only if the winner improves over historical_control."
        ),
        "defaults": {**source["defaults"], "patience": 3},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
