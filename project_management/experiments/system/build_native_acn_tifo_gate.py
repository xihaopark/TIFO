#!/usr/bin/env python3
"""Build matched ACN controls and ACN+TIFO gates from frozen ACN winners."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ACN_MATRIX = Path(
    "/home/park/TS/FredNormer/project_management/experiments/system/"
    "tune_native_acn_h96_v2.json"
)
ACN_VALIDATION = Path(
    "/home/park/TS/FredNormer/project_management/experiments/results/"
    "native_acn_h96_gate.json"
)
OUTPUT = HERE / "tune_native_acn_tifo_h96.json"

TIFO_CANDIDATES = {
    "historical_stable": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.5,
        "tifo_zero_pad_ratio": 0.0,
    },
    "hermitian_aligned_zp1": {
        "filter_dim": 512,
        "tifo_variant": "hermitian_aligned",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "phase_pr0p25_lr0p25": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.25,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "diagonal_gl0p5_lr1": {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "diagonal_gl0p5_lr4": {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 4.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "diagonal_gl0p5_lr16": {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 0.5,
        "tifo_lr_scale": 16.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "diagonal_gl1_lr8": {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 1.0,
        "tifo_lr_scale": 8.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
}


def main() -> None:
    matrix = json.loads(ACN_MATRIX.read_text(encoding="utf-8"))
    validation = json.loads(ACN_VALIDATION.read_text(encoding="utf-8"))
    if len(validation) != 56:
        raise ValueError(f"expected 56 completed ACN candidates, got {len(validation)}")
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    winners = {}
    for dataset in sorted({row["dataset"] for row in validation}):
        rows = [row for row in validation if row["dataset"] == dataset]
        if len(rows) != 8:
            raise ValueError(f"{dataset}: expected eight ACN candidates, got {len(rows)}")
        winners[dataset] = min(
            rows, key=lambda row: (row["validation_mse"], row["run_id"])
        )

    runs = []
    for dataset, winner in winners.items():
        template = by_id[winner["run_id"]]
        shared = {
            key: value
            for key, value in template.items()
            if key not in {"run_id", "method", "model_args"}
        }
        base_args = dict(template["model_args"])
        base_args["skip_final_test"] = True
        dataset_id = dataset.lower()
        runs.append(
            {
                **shared,
                "run_id": f"gate_native_acn_tifo_{dataset_id}_h96_acn_control_s2022",
                "method": "acn",
                "model_args": base_args,
            }
        )
        for name, candidate in TIFO_CANDIDATES.items():
            runs.append(
                {
                    **shared,
                    "run_id": f"gate_native_acn_tifo_{dataset_id}_h96_{name}_s2022",
                    "method": "acn_tifo",
                    "model_args": {**base_args, **candidate},
                }
            )

    output = {
        "protocol_id": "kdd_resubmit_native_acn_tifo_h96_gate_v1",
        "selection_rule": (
            "For each dataset, rerun the frozen ACN validation winner as a control "
            "and compare seven declared ACN+TIFO configurations using seed-2022 "
            "validation MSE only. Promote a composition only when it beats the "
            "same-source ACN control; final testing is disabled."
        ),
        "acn_validation_winners": {
            dataset: {
                "selected_run": row["run_id"],
                "selected_validation_mse": row["validation_mse"],
            }
            for dataset, row in winners.items()
        },
        "defaults": matrix["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
