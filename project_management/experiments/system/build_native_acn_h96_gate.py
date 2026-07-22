#!/usr/bin/env python3
"""Build a matched native-runner ACN validation gate at horizon 96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
ETTM2_SOURCE = HERE / "final_tifo_hermitian_h96.json"
OUTPUT = HERE / "tune_native_acn_h96.json"
TEMPERATURES = (0.025, 0.05, 0.075, 0.1, 0.2, 0.35, 0.5, 1.0)


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
        architecture = {
            key: value
            for key, value in native["model_args"].items()
            if not key.startswith("tifo_") and key != "filter_dim"
        }
        for temperature in TEMPERATURES:
            dataset_id = native["dataset"].lower()
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_native_acn_{dataset_id}_h96_t{tag(temperature)}_s2022"
                    ),
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "acn",
                    "seed": 2022,
                    "model_args": {
                        **architecture,
                        "acn_temperature": temperature,
                        "skip_final_test": True,
                    },
                }
            )
    output = {
        "protocol_id": "kdd_resubmit_native_acn_h96_gate_v1",
        "selection_rule": (
            "For each dataset, select temperature by seed-2022 validation MSE. "
            "The backbone, data pipeline, optimizer, epoch budget, early stopping, "
            "and metric code are identical to native Ori/TIFO; final test is disabled."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
