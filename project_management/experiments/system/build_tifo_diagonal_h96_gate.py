#!/usr/bin/env python3
"""Build a per-dataset H=96 gate for diagonal phase-preserving TIFO."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
ETTM2_SOURCE = HERE / "final_tifo_hermitian_h96.json"
OUTPUT = HERE / "tune_tifo_diagonal_h96.json"


def tag(value: float) -> str:
    return str(value).replace(".", "p")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ettm2_source = json.loads(ETTM2_SOURCE.read_text(encoding="utf-8"))
    templates = [
        {**source["defaults"], **run}
        for run in source["runs"]
        if run.get("method") == "ori" and run.get("seed") == 2022
    ]
    templates.extend(
        {**ettm2_source["defaults"], **run}
        for run in ettm2_source["runs"]
        if run.get("dataset") == "ETTm2" and run.get("seed") == 2022
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
        for prior, gain_limit, lr_scale in itertools.product(
            (0.25, 1.0), (0.25, 0.5), (0.25, 1.0)
        ):
            candidate = (
                f"pr{tag(prior)}_gl{tag(gain_limit)}_lr{tag(lr_scale)}"
            )
            runs.append(
                {
                    **shared,
                    "run_id": f"tune_tifo_diagonal_{dataset_id}_h96_{candidate}_s2022",
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "seed": 2022,
                    "model_args": {
                        **architecture,
                        "tifo_variant": "hermitian_diagonal",
                        "tifo_prior_strength": prior,
                        "tifo_gain_limit": gain_limit,
                        "tifo_lr_scale": lr_scale,
                        "tifo_residual_alpha": 1.0,
                        "tifo_zero_pad_ratio": 0.0,
                        "skip_final_test": True,
                    },
                }
            )

    matrix = {
        "protocol_id": "kdd_resubmit_tifo_diagonal_h96_gate_v1",
        "selection_rule": (
            "For each dataset, select one of exactly eight diagonal, "
            "phase-preserving, stationarity-conditioned TIFO candidates by "
            "seed-2022 validation MSE; final-test evaluation is disabled."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
