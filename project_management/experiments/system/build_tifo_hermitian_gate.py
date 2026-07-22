#!/usr/bin/env python3
"""Build a validation-only gate for paper-consistent Hermitian TIFO variants."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("tifo_hermitian_gate_h96.json")
PYTHON = "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python"

DATASETS = {
    "ETTh1": {
        "data_type": "ETTh1",
        "data_path": "ETTh1.csv",
        "filter_dim": 256,
        "tifo_dropout": 0.3,
    },
    "ETTm2": {
        "data_type": "ETTm2",
        "data_path": "ETTm2.csv",
        "filter_dim": 512,
        "tifo_dropout": 0.5,
    },
}


def main() -> None:
    runs = []
    for dataset, dataset_config in DATASETS.items():
        dataset_id = dataset.lower()
        for variant in ("hermitian_raw", "hermitian_aligned"):
            for zero_pad_ratio in (0.0, 1.0):
                pad_token = "z0" if zero_pad_ratio == 0 else "z1"
                runs.append(
                    {
                        "run_id": (
                            f"tune_{dataset_id}_h96_tifo_{variant}_{pad_token}_s2022"
                        ),
                        "engine": "native",
                        "backbone": "iTransformer",
                        "method": "tifo",
                        "dataset": dataset,
                        "data_type": dataset_config["data_type"],
                        "data_path": dataset_config["data_path"],
                        "seed": 2022,
                        "model_args": {
                            "d_model": 128,
                            "d_ff": 128,
                            "e_layers": 2,
                            "n_heads": 8,
                            "factor": 3,
                            "filter_dim": dataset_config["filter_dim"],
                            "tifo_variant": variant,
                            "tifo_dropout": dataset_config["tifo_dropout"],
                            "tifo_residual_alpha": 1.0,
                            "tifo_zero_pad_ratio": zero_pad_ratio,
                            "skip_final_test": True,
                        },
                    }
                )

    matrix = {
        "protocol_id": "kdd_resubmit_tifo_hermitian_gate_h96_v1",
        "defaults": {
            "python": PYTHON,
            "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
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
