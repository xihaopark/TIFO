#!/usr/bin/env python3
"""Build a validation-only ACN temperature gate for Traffic H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_acn_traffic_temperature.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    native = next(
        run
        for run in source["runs"]
        if run.get("dataset") == "Traffic"
        and run.get("method") == "ori"
        and run.get("seed") == 2022
    )
    shared = {
        key: value
        for key, value in native.items()
        if key not in {"run_id", "engine", "backbone", "method", "model_args"}
    }
    runs = []
    for temperature in (0.05, 0.1, 0.2, 0.5):
        token = str(temperature).replace(".", "p")
        runs.append(
            {
                **shared,
                "run_id": f"tune_traffic_h96_acn_temp{token}_s2022",
                "engine": "acn",
                "seed": 2022,
                "model_args": {
                    **native["model_args"],
                    "temperature": temperature,
                    "skip_final_test": True,
                },
            }
        )
    matrix = {
        "protocol_id": "kdd_resubmit_acn_traffic_temperature_gate_v1",
        "selection_rule": (
            "Select the lowest seed-2022 validation MSE; test evaluation is disabled."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
