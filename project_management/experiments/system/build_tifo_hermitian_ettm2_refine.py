#!/usr/bin/env python3
"""Build the final validation-only ETTm2 refinement around Hermitian TIFO."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("tifo_hermitian_ettm2_refine.json")

CANDIDATES = {
    "fd128": {"filter_dim": 128},
    "fd256": {"filter_dim": 256},
    "fd1024": {"filter_dim": 1024},
    "do0": {"tifo_dropout": 0.0},
    "do0p1": {"tifo_dropout": 0.1},
    "do0p3": {"tifo_dropout": 0.3},
    "lr0p125": {"tifo_lr_scale": 0.125},
    "lr0p25": {"tifo_lr_scale": 0.25},
    "lr0p5": {"tifo_lr_scale": 0.5},
    "lr2": {"tifo_lr_scale": 2.0},
    "alpha0p5": {"tifo_residual_alpha": 0.5},
    "alpha0p75": {"tifo_residual_alpha": 0.75},
}


def main() -> None:
    base_model_args = {
        "d_model": 128,
        "d_ff": 128,
        "e_layers": 2,
        "n_heads": 8,
        "factor": 3,
        "filter_dim": 512,
        "tifo_variant": "hermitian_raw",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
        "skip_final_test": True,
    }
    runs = []
    for name, override in CANDIDATES.items():
        runs.append(
            {
                "run_id": f"tune_ettm2_h96_tifo_hermitian_refine_{name}_s2022",
                "engine": "native",
                "backbone": "iTransformer",
                "method": "tifo",
                "seed": 2022,
                "model_args": {**base_model_args, **override},
            }
        )

    matrix = {
        "protocol_id": "kdd_resubmit_tifo_hermitian_ettm2_refine_v1",
        "defaults": {
            "python": "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python",
            "dataset": "ETTm2",
            "data_type": "ETTm2",
            "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
            "data_path": "ETTm2.csv",
            "features": "M",
            "seq_len": 96,
            "label_len": 48,
            "pred_len": 96,
            "enc_in": 7,
            "dec_in": 7,
            "c_out": 7,
            "train_epochs": 30,
            "patience": 3,
            "batch_size": 32,
            "learning_rate": 0.0001,
            "num_workers": 0,
            "cpu_threads": 4,
        },
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
