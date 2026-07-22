#!/usr/bin/env python3
"""Build a validation-only gate for the phase-preserving TIFO operator."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
ETTM2_SOURCE = HERE / "final_tifo_hermitian_h96.json"
OUTPUT = HERE / "tune_tifo_phase_preserving_h96.json"


def tag(value: float) -> str:
    return str(value).replace(".", "p")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ettm2_source = json.loads(ETTM2_SOURCE.read_text(encoding="utf-8"))
    templates = [
        run
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
        architecture = native["model_args"]
        for zero_pad, prior, lr_scale in itertools.product(
            (0.0, 1.0), (0.0, 0.25), (0.25, 1.0)
        ):
            dataset_id = native["dataset"].lower()
            candidate = (
                f"zp{tag(zero_pad)}_pr{tag(prior)}_lr{tag(lr_scale)}"
            )
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_{dataset_id}_h96_tifo_phase_{candidate}_s2022"
                    ),
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "seed": 2022,
                    "model_args": {
                        **architecture,
                        "filter_dim": 128,
                        "tifo_variant": "hermitian_shared",
                        "tifo_prior_strength": prior,
                        "tifo_lr_scale": lr_scale,
                        "tifo_residual_alpha": 1.0,
                        "tifo_zero_pad_ratio": zero_pad,
                        "skip_final_test": True,
                    },
                }
            )
    matrix = {
        "protocol_id": "kdd_resubmit_tifo_phase_preserving_h96_gate_v1",
        "selection_rule": (
            "For each dataset, select by seed-2022 validation MSE only. "
            "All candidates preserve phase through one shared positive spectral "
            "gain and disable final-test evaluation."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
