#!/usr/bin/env python3
"""Build validation-only TIFO tuning runs for the legacy DLinear protocol.

The DLinear input lengths intentionally reproduce the scripts used for the
original RevIN/SAN/FAN table.  This lets those frozen baseline values remain
comparable while TIFO is selected independently in every dataset-horizon cell.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "tune_tifo_dlinear_all_horizons.json"

PYTHON = "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python"
HORIZONS = (96, 192, 336, 720)

DATASETS = {
    "ETTh1": {
        "data_type": "ETTh1",
        "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
        "data_path": "ETTh1.csv",
        "enc_in": 7,
        "seq_len": 336,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
    "ETTh2": {
        "data_type": "ETTh2",
        "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
        "data_path": "ETTh2.csv",
        "enc_in": 7,
        "seq_len": 336,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
    "ETTm1": {
        "data_type": "ETTm1",
        "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
        "data_path": "ETTm1.csv",
        "enc_in": 7,
        "seq_len": 96,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
    "ETTm2": {
        "data_type": "ETTm2",
        "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
        "data_path": "ETTm2.csv",
        "enc_in": 7,
        "seq_len": 336,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
    "Electricity": {
        "data_type": "custom",
        "root_path": "/home/park/TS/FredNormer/dataset/electricity",
        "data_path": "electricity.csv",
        "enc_in": 321,
        "seq_len": 96,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
    "Traffic": {
        "data_type": "custom",
        "root_path": "/home/park/TS/FredNormer/dataset/traffic",
        "data_path": "traffic.csv",
        "enc_in": 862,
        "seq_len": 96,
        "batch_size": 16,
        "learning_rate": 0.001,
    },
    "Weather": {
        "data_type": "custom",
        "root_path": "/home/park/TS/FredNormer/dataset/weather",
        "data_path": "weather.csv",
        "enc_in": 21,
        "seq_len": 96,
        "batch_size": 32,
        "learning_rate": 0.0001,
    },
}

CANDIDATES = {
    "historical_default": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "historical_stable": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.5,
        "tifo_zero_pad_ratio": 0.0,
    },
    "historical_low_alpha": {
        "filter_dim": 512,
        "tifo_variant": "historical",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 0.25,
        "tifo_zero_pad_ratio": 0.0,
    },
    "historical_compact_zp1": {
        "filter_dim": 256,
        "tifo_variant": "historical",
        "tifo_dropout": 0.3,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "hermitian_aligned_zp1": {
        "filter_dim": 512,
        "tifo_variant": "hermitian_aligned",
        "tifo_dropout": 0.5,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
    "phase_pr0_lr0p25": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.0,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "phase_pr0p25_lr0p25": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.25,
        "tifo_lr_scale": 0.25,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 0.0,
    },
    "phase_pr0p25_lr1_zp1": {
        "filter_dim": 128,
        "tifo_variant": "hermitian_shared",
        "tifo_prior_strength": 0.25,
        "tifo_lr_scale": 1.0,
        "tifo_residual_alpha": 1.0,
        "tifo_zero_pad_ratio": 1.0,
    },
}


def main() -> None:
    runs = []
    for dataset, config in DATASETS.items():
        for horizon in HORIZONS:
            for candidate_name, candidate in CANDIDATES.items():
                runs.append(
                    {
                        "run_id": (
                            f"tune_tifo_dlinear_{dataset.lower()}_h{horizon}_"
                            f"{candidate_name}_s2022"
                        ),
                        "engine": "native",
                        "backbone": "DLinear",
                        "method": "tifo",
                        "dataset": dataset,
                        "data_type": config["data_type"],
                        "root_path": config["root_path"],
                        "data_path": config["data_path"],
                        "enc_in": config["enc_in"],
                        "dec_in": config["enc_in"],
                        "c_out": config["enc_in"],
                        "seq_len": config["seq_len"],
                        "pred_len": horizon,
                        "batch_size": config["batch_size"],
                        "learning_rate": config["learning_rate"],
                        "seed": 2022,
                        "model_args": {
                            **candidate,
                            "skip_final_test": True,
                        },
                    }
                )

    matrix = {
        "protocol_id": "kdd_resubmit_tifo_dlinear_all_horizons_gate_v1",
        "selection_rule": (
            "For every DLinear dataset-horizon cell, select the lowest seed-2022 "
            "validation MSE among eight declared TIFO candidates. The final test "
            "split is disabled for every tuning run."
        ),
        "defaults": {
            "python": PYTHON,
            "features": "M",
            "label_len": 48,
            "train_epochs": 30,
            "patience": 5,
            "num_workers": 0,
            "cpu_threads": 4,
        },
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
