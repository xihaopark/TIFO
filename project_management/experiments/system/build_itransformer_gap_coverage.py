#!/usr/bin/env python3
"""Build only the unverified iTransformer cells required by the old main table."""

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("coverage_itransformer_remaining_horizons.json")
SEEDS = (2021, 2022, 2023)
HORIZONS = (96, 192, 336, 720)
SPECS = {
    "ETTh1": ("ETTh1", "/home/park/TS/FredNormer/dataset/ETT-small", "ETTh1.csv", 7, 32, 0.0001, 128, 128, 2),
    "ETTh2": ("ETTh2", "/home/park/TS/FredNormer/dataset/ETT-small", "ETTh2.csv", 7, 32, 0.0001, 128, 128, 2),
    "ETTm1": ("ETTm1", "/home/park/TS/FredNormer/dataset/ETT-small", "ETTm1.csv", 7, 32, 0.0001, 128, 128, 2),
    "ETTm2": ("ETTm2", "/home/park/TS/FredNormer/dataset/ETT-small", "ETTm2.csv", 7, 32, 0.0001, 128, 128, 2),
    "Electricity": ("custom", "/home/park/TS/FredNormer/dataset/electricity", "electricity.csv", 321, 16, 0.0005, 512, 512, 3),
    "Traffic": ("custom", "/home/park/TS/FredNormer/dataset/traffic", "traffic.csv", 862, 16, 0.001, 512, 512, 4),
    "Weather": ("custom", "/home/park/TS/FredNormer/dataset/weather", "weather.csv", 21, 32, 0.0001, 512, 512, 3),
}


def already_verified(dataset, horizon):
    return horizon == 96 or (dataset == "ETTm2" and horizon == 192)


def build_run(dataset, horizon, method, seed):
    data_type, root_path, data_path, channels, batch_size, learning_rate, d_model, d_ff, e_layers = SPECS[dataset]
    model_args = {"d_model": d_model, "d_ff": d_ff, "e_layers": e_layers, "n_heads": 8, "factor": 3}
    if method == "tifo":
        model_args.update({"filter_dim": 512, "tifo_variant": "historical", "tifo_dropout": 0.5})
    return {
        "run_id": f"coverage_itransformer_{dataset.lower()}_h{horizon}_{method}_s{seed}",
        "engine": "native", "dataset": dataset, "data_type": data_type,
        "root_path": root_path, "data_path": data_path, "enc_in": channels,
        "dec_in": channels, "c_out": channels, "backbone": "iTransformer",
        "method": method, "seed": seed, "pred_len": horizon,
        "batch_size": batch_size, "learning_rate": learning_rate, "model_args": model_args,
    }


def main():
    runs = [
        build_run(dataset, horizon, method, seed)
        for dataset in SPECS for horizon in HORIZONS
        if not already_verified(dataset, horizon)
        for seed in SEEDS for method in ("ori", "tifo")
    ]
    matrix = {
        "protocol_id": "kdd_resubmit_itransformer_coverage_v1",
        "defaults": {
            "python": "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python",
            "features": "M", "seq_len": 96, "label_len": 48, "train_epochs": 30,
            "patience": 5, "num_workers": 0, "cpu_threads": 4,
        },
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
