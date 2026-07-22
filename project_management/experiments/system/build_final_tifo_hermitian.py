#!/usr/bin/env python3
"""Build final three-seed runs for validation-selected Hermitian TIFO."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("final_tifo_hermitian_h96.json")

SELECTIONS = {
    "ETTh1": {
        "data_type": "ETTh1",
        "data_path": "ETTh1.csv",
        "filter_dim": 256,
        "tifo_dropout": 0.3,
        "tifo_variant": "hermitian_aligned",
        "tifo_zero_pad_ratio": 1.0,
    },
    "ETTm2": {
        "data_type": "ETTm2",
        "data_path": "ETTm2.csv",
        "filter_dim": 512,
        "tifo_dropout": 0.5,
        "tifo_variant": "hermitian_raw",
        "tifo_zero_pad_ratio": 0.0,
    },
}


def main() -> None:
    runs = []
    for dataset, selection in SELECTIONS.items():
        for seed in (2021, 2022, 2023):
            runs.append(
                {
                    "run_id": f"final_{dataset.lower()}_h96_tifo_hermitian_s{seed}",
                    "engine": "native",
                    "backbone": "iTransformer",
                    "method": "tifo",
                    "dataset": dataset,
                    "data_type": selection["data_type"],
                    "data_path": selection["data_path"],
                    "seed": seed,
                    "model_args": {
                        "d_model": 128,
                        "d_ff": 128,
                        "e_layers": 2,
                        "n_heads": 8,
                        "factor": 3,
                        "filter_dim": selection["filter_dim"],
                        "tifo_variant": selection["tifo_variant"],
                        "tifo_dropout": selection["tifo_dropout"],
                        "tifo_residual_alpha": 1.0,
                        "tifo_zero_pad_ratio": selection["tifo_zero_pad_ratio"],
                    },
                }
            )

    matrix = {
        "protocol_id": "kdd_resubmit_tifo_hermitian_final_h96_v1",
        "defaults": {
            "python": "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python",
            "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
            "features": "M",
            "seq_len": 96,
            "label_len": 48,
            "pred_len": 96,
            "enc_in": 7,
            "dec_in": 7,
            "c_out": 7,
            "train_epochs": 30,
            "patience": 5,
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
