#!/usr/bin/env python3
"""Build matched eight-candidate ACN/WDAN gates for every DLinear cell."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_tifo_dlinear_all_horizons.json"
ACN_OUTPUT = HERE / "tune_native_acn_dlinear_all_horizons.json"
WDAN_OUTPUT = HERE / "tune_native_wdan_dlinear_all_horizons.json"

TEMPERATURES = (0.025, 0.05, 0.075, 0.1, 0.2, 0.35, 0.5, 1.0)
WDAN_CANDIDATES = (
    ("l2_w5_d0_lr1", 2, 5, 0, 1.0),
    ("l2_w12_d0_lr1", 2, 12, 0, 1.0),
    ("l3_w5_d1_lr1", 3, 5, 1, 1.0),
    ("l3_w24_d1_lr1", 3, 24, 1, 1.0),
    ("l3_w5_d2_lr1", 3, 5, 2, 1.0),
    ("l3_w24_d2_lr1", 3, 24, 2, 1.0),
    ("l2_w5_d0_lr10", 2, 5, 0, 10.0),
    ("l3_w5_d2_lr10", 3, 5, 2, 10.0),
)


def tag(value: float) -> str:
    return str(value).replace(".", "p")


def cell_templates(source: dict) -> list[dict]:
    templates = {}
    for run in source["runs"]:
        key = (run["dataset"], int(run["pred_len"]))
        templates.setdefault(key, run)
    if len(templates) != 28:
        raise ValueError(f"expected 28 DLinear cells, found {len(templates)}")
    return [templates[key] for key in sorted(templates)]


def base_run(template: dict) -> dict:
    return {
        key: value
        for key, value in template.items()
        if key not in {"run_id", "method", "seed", "model_args"}
    }


def write_matrix(
    source: dict,
    output: Path,
    protocol: str,
    method: str,
    runs: list[dict],
) -> None:
    payload = {
        "protocol_id": protocol,
        "selection_rule": (
            f"For every DLinear dataset-horizon cell, select {method.upper()} by "
            "seed-2022 validation MSE from exactly eight declared candidates. "
            "The backbone, data pipeline, optimizer budget, early stopping, and "
            "metric code match the DLinear TIFO matrix; final testing is disabled."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {output}")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates = cell_templates(source)
    acn_runs = []
    wdan_runs = []

    for template in templates:
        shared = base_run(template)
        dataset_id = template["dataset"].lower()
        horizon = int(template["pred_len"])

        for temperature in TEMPERATURES:
            acn_runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_native_acn_dlinear_{dataset_id}_h{horizon}_"
                        f"t{tag(temperature)}_s2022"
                    ),
                    "method": "acn",
                    "seed": 2022,
                    "model_args": {
                        "acn_temperature": temperature,
                        "skip_final_test": True,
                    },
                }
            )

        for name, levels, window, layers, lr_scale in WDAN_CANDIDATES:
            wdan_runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_native_wdan_dlinear_{dataset_id}_h{horizon}_"
                        f"{name}_s2022"
                    ),
                    "method": "wdan",
                    "seed": 2022,
                    "model_args": {
                        "wdan_levels": levels,
                        "wdan_window": window,
                        "wdan_d_model": 128,
                        "wdan_d_ff": 128,
                        "wdan_layers": layers,
                        "wdan_dropout": 0.1,
                        "wdan_stats_epochs": 5,
                        "wdan_lr_scale": lr_scale,
                        "skip_final_test": True,
                    },
                }
            )

    write_matrix(
        source,
        ACN_OUTPUT,
        "kdd_resubmit_native_acn_dlinear_all_horizons_gate_v1",
        "acn",
        acn_runs,
    )
    write_matrix(
        source,
        WDAN_OUTPUT,
        "kdd_resubmit_native_wdan_dlinear_all_horizons_gate_v1",
        "wdan",
        wdan_runs,
    )


if __name__ == "__main__":
    main()
