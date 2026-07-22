#!/usr/bin/env python3
"""Build matched native-ACN validation gates for horizons 192/336/720."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_itransformer_remaining_horizons.json"
ETTM2_H192_SOURCE = HERE / "gate_ettm2_h192_two_backbones.json"
OUTPUT = HERE / "tune_native_acn_remaining_horizons.json"
TEMPERATURES = (0.025, 0.05, 0.075, 0.1, 0.2, 0.35, 0.5, 1.0)


def tag(value: float) -> str:
    return str(value).replace(".", "p")


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
        for temperature in TEMPERATURES:
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_native_acn_cell_{dataset_id}_h{horizon}_"
                        f"t{tag(temperature)}_s2022"
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
        "protocol_id": "kdd_resubmit_native_acn_remaining_horizons_gate_v1",
        "selection_rule": (
            "For each dataset-horizon cell, select ACN temperature from the same "
            "eight-candidate budget by seed-2022 validation MSE; final test is disabled."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
