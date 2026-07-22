#!/usr/bin/env python3
"""Build equal-budget native WDAN validation matrices for all 7x4 cells."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
H96_SOURCE = HERE / "coverage_h96_itransformer.json"
ETTM2_H96_SOURCE = HERE / "final_tifo_hermitian_h96.json"
REMAINING_SOURCE = HERE / "coverage_itransformer_remaining_horizons.json"
ETTM2_H192_SOURCE = HERE / "gate_ettm2_h192_two_backbones.json"

# The official WDAN iTransformer scripts use these level/window/depth families
# and either 1x or 10x statistics-network learning rate.  Holding the auxiliary
# weight and hidden width fixed gives every dataset-horizon cell exactly eight
# validation candidates, matching the ACN and TIFO selection budget.
CANDIDATES = (
    ("l2_w5_d0_lr1", 2, 5, 0, 1.0),
    ("l2_w12_d0_lr1", 2, 12, 0, 1.0),
    ("l3_w5_d1_lr1", 3, 5, 1, 1.0),
    ("l3_w24_d1_lr1", 3, 24, 1, 1.0),
    ("l3_w5_d2_lr1", 3, 5, 2, 1.0),
    ("l3_w24_d2_lr1", 3, 24, 2, 1.0),
    ("l2_w5_d0_lr10", 2, 5, 0, 10.0),
    ("l3_w5_d2_lr10", 3, 5, 2, 10.0),
)


def native_templates(source_path: Path, extra_path: Path, extra_horizon: int):
    source = json.loads(source_path.read_text(encoding="utf-8"))
    extra = json.loads(extra_path.read_text(encoding="utf-8"))
    templates = [
        {**source["defaults"], **run}
        for run in source["runs"]
        if run.get("method") == "ori" and run.get("seed") == 2022
    ]
    merged_extra = [{**extra["defaults"], **run} for run in extra["runs"]]
    extra_templates = [
        run
        for run in merged_extra
        if run.get("dataset") == "ETTm2"
        and run.get("pred_len") == extra_horizon
        and run.get("seed") == 2022
        and run.get("backbone", "iTransformer") == "iTransformer"
    ]
    ori_templates = [run for run in extra_templates if run.get("method") == "ori"]
    templates.extend(ori_templates or extra_templates[:1])
    return source, templates


def build(source_path: Path, extra_path: Path, extra_horizon: int, output: Path, protocol: str):
    source, templates = native_templates(source_path, extra_path, extra_horizon)
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
        for name, levels, window, layers, lr_scale in CANDIDATES:
            runs.append(
                {
                    **shared,
                    "run_id": f"tune_native_wdan_{dataset_id}_h{horizon}_{name}_s2022",
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "wdan",
                    "seed": 2022,
                    "model_args": {
                        **architecture,
                        "wdan_levels": levels,
                        "wdan_window": window,
                        "wdan_d_model": 128,
                        "wdan_d_ff": 128,
                        "wdan_layers": layers,
                        "wdan_dropout": 0.1,
                        "wdan_aux_weight": 1.0,
                        "wdan_lr_scale": lr_scale,
                        "skip_final_test": True,
                    },
                }
            )
    payload = {
        "protocol_id": protocol,
        "selection_rule": (
            "For each dataset-horizon cell, select one of eight WDAN configurations "
            "by seed-2022 validation MSE. The native data pipeline, iTransformer "
            "backbone, optimizer schedule, epoch budget, early stopping, and metric "
            "code are shared with TIFO and ACN; final test is disabled."
        ),
        "defaults": {**source["defaults"], "patience": 5},
        "runs": runs,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {output}")


def main() -> None:
    build(
        H96_SOURCE,
        ETTM2_H96_SOURCE,
        96,
        HERE / "tune_native_wdan_h96.json",
        "kdd_resubmit_native_wdan_h96_gate_v1",
    )
    build(
        REMAINING_SOURCE,
        ETTM2_H192_SOURCE,
        192,
        HERE / "tune_native_wdan_remaining_horizons.json",
        "kdd_resubmit_native_wdan_remaining_horizons_gate_v1",
    )


if __name__ == "__main__":
    main()
