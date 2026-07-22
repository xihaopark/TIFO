#!/usr/bin/env python3
"""Build cell-specific standalone TIFO architecture gates for weak H=96 cells."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_tifo_diagonal_h96.json"
OUTPUT = HERE / "tune_tifo_cell_architecture_h96.json"


# Eight declared backbone configurations per cell.  Candidate zero reproduces
# the best known standalone TIFO family for that cell; the other seven test
# capacity/depth/base-learning-rate changes without reading final-test metrics.
ARCHITECTURES = {
    "ETTm1": (
        ("control", 128, 128, 2, 1.0e-4),
        ("dm256_e2", 256, 256, 2, 1.0e-4),
        ("dm512_e2", 512, 512, 2, 1.0e-4),
        ("dm256_e3", 256, 256, 3, 1.0e-4),
        ("dm512_e3", 512, 512, 3, 1.0e-4),
        ("lr5em5", 128, 128, 2, 5.0e-5),
        ("lr2em4", 128, 128, 2, 2.0e-4),
        ("dm256_lr2em4", 256, 256, 2, 2.0e-4),
    ),
    "ETTm2": (
        ("control", 128, 128, 2, 1.0e-4),
        ("dm256_e2", 256, 256, 2, 1.0e-4),
        ("dm512_e2", 512, 512, 2, 1.0e-4),
        ("dm256_e3", 256, 256, 3, 1.0e-4),
        ("dm512_e3", 512, 512, 3, 1.0e-4),
        ("lr5em5", 128, 128, 2, 5.0e-5),
        ("lr2em4", 128, 128, 2, 2.0e-4),
        ("dm256_lr2em4", 256, 256, 2, 2.0e-4),
    ),
    "Electricity": (
        ("control", 512, 512, 3, 5.0e-4),
        ("dm256_e2", 256, 256, 2, 5.0e-4),
        ("dm256_e3", 256, 256, 3, 5.0e-4),
        ("dm512_e2", 512, 512, 2, 5.0e-4),
        ("lr2p5em4", 512, 512, 3, 2.5e-4),
        ("lr7p5em4", 512, 512, 3, 7.5e-4),
        ("lr1em3", 512, 512, 3, 1.0e-3),
        ("dm256_lr2p5em4", 256, 256, 2, 2.5e-4),
    ),
    "Weather": (
        ("control", 512, 512, 3, 1.0e-4),
        ("dm256_e2", 256, 256, 2, 1.0e-4),
        ("dm256_e3", 256, 256, 3, 1.0e-4),
        ("dm512_e2", 512, 512, 2, 1.0e-4),
        ("dm512_e4", 512, 512, 4, 1.0e-4),
        ("lr5em5", 512, 512, 3, 5.0e-5),
        ("lr2em4", 512, 512, 3, 2.0e-4),
        ("dm256_lr2em4", 256, 256, 2, 2.0e-4),
    ),
}


FILTERS = {
    "ETTm1": {
        "filter_dim": 256,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.5,
    },
    "ETTm2": {
        "filter_dim": 64,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "Electricity": {
        "tifo_variant": "hermitian_diagonal",
        "tifo_prior_strength": 1.0,
        "tifo_gain_limit": 1.0,
        "tifo_lr_scale": 4.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "Weather": {
        "filter_dim": 512,
        "tifo_variant": "hermitian_aligned",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    templates = {}
    for run in source["runs"]:
        templates.setdefault(run["dataset"], run)

    runs = []
    for dataset, candidates in ARCHITECTURES.items():
        template = templates[dataset]
        shared = {
            key: value
            for key, value in template.items()
            if key not in {"run_id", "model_args", "learning_rate"}
        }
        for name, d_model, d_ff, e_layers, learning_rate in candidates:
            runs.append(
                {
                    **shared,
                    "run_id": (
                        f"tune_tifo_cellarch_{dataset.lower()}_h96_{name}_s2022"
                    ),
                    "learning_rate": learning_rate,
                    "model_args": {
                        "d_model": d_model,
                        "d_ff": d_ff,
                        "e_layers": e_layers,
                        "n_heads": 8,
                        "factor": 3,
                        **FILTERS[dataset],
                        "skip_final_test": True,
                    },
                }
            )

    payload = {
        "protocol_id": "kdd_resubmit_tifo_cell_architecture_h96_gate_v1",
        "selection_rule": (
            "For each declared dataset, compare exactly eight standalone TIFO "
            "backbone/filter configurations using seed-2022 validation MSE only. "
            "The per-cell winner may be promoted only after the matrix is complete; "
            "final-test evaluation is disabled during selection."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
