#!/usr/bin/env python3
"""Build frozen three-seed TIFO finals selected by the EW validation gate."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "final_tifo_electricity_weather_h96.json"
TARGETS = {"Electricity", "Weather"}
SEEDS = {2021, 2022, 2023}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for native in source["runs"]:
        dataset = native.get("dataset")
        if (
            native.get("method") != "ori"
            or native.get("seed") not in SEEDS
            or dataset not in TARGETS
        ):
            continue
        shared = {
            key: value
            for key, value in native.items()
            if key not in {"run_id", "engine", "backbone", "method", "model_args"}
        }
        runs.append(
            {
                **shared,
                "run_id": (
                    f"final_{dataset.lower()}_h96_tifo_hermitian_aligned_"
                    f"zpad100_s{native['seed']}"
                ),
                "engine": "native",
                "backbone": "iTransformer",
                "method": "tifo",
                "model_args": {
                    **native["model_args"],
                    "filter_dim": 512,
                    "tifo_variant": "hermitian_aligned",
                    "tifo_dropout": 0.5,
                    "tifo_lr_scale": 1.0,
                    "tifo_residual_alpha": 1.0,
                    "tifo_zero_pad_ratio": 1.0,
                },
            }
        )
    matrix = {
        "protocol_id": "kdd_resubmit_tifo_electricity_weather_h96_final_v1",
        "selection_provenance": (
            "Frozen before final testing: hermitian_aligned with zero-pad ratio 1.0 "
            "was the lowest seed-2022 validation MSE for both datasets in "
            "kdd_resubmit_tifo_electricity_weather_h96_gate_v1."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
