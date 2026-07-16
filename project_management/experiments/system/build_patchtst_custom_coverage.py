#!/usr/bin/env python3
"""Build the remaining PatchTST main-table coverage matrix (custom datasets)."""

import json
from pathlib import Path


OUTPUT = Path(__file__).with_name("coverage_patchtst_custom_all_horizons.json")
SEEDS = (2021, 2022, 2023)
HORIZONS = (96, 192, 336, 720)
DATASETS = {
    "Electricity": {
        "root_path": "/home/park/TS/FredNormer/dataset/electricity",
        "data_path": "electricity.csv", "channels": 321, "batch_size": 16,
        "d_model": 128, "d_ff": 128, "e_layers": 2, "n_heads": 8,
    },
    "Traffic": {
        "root_path": "/home/park/TS/FredNormer/dataset/traffic",
        "data_path": "traffic.csv", "channels": 862, "batch_size": 4,
        "d_model": 128, "d_ff": 128, "e_layers": 2, "n_heads": 8,
    },
    "Weather": {
        "root_path": "/home/park/TS/FredNormer/dataset/weather",
        "data_path": "weather.csv", "channels": 21, "batch_size": 128,
        "d_model": 512, "d_ff": 2048, "e_layers": 2, "n_heads": 4,
    },
}


def run(dataset, horizon, method, seed):
    spec = DATASETS[dataset]
    args = {key: spec[key] for key in ("d_model", "d_ff", "e_layers", "n_heads")}
    args.update({"factor": 3, "patch_len": 16, "stride": 8})
    if method == "tifo":
        args.update({"filter_dim": 512, "tifo_variant": "historical", "tifo_dropout": 0.5})
    return {
        "run_id": f"coverage_patchtst_{dataset.lower()}_h{horizon}_{method}_s{seed}",
        "engine": "native", "dataset": dataset, "data_type": "custom",
        "root_path": spec["root_path"], "data_path": spec["data_path"],
        "enc_in": spec["channels"], "dec_in": spec["channels"], "c_out": spec["channels"],
        "backbone": "PatchTST", "method": method, "seed": seed,
        "pred_len": horizon, "batch_size": spec["batch_size"], "model_args": args,
    }


def main():
    matrix = {
        "protocol_id": "kdd_resubmit_patchtst_custom_coverage_v1",
        "defaults": {
            "python": "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python",
            "features": "M", "seq_len": 96, "label_len": 48,
            "train_epochs": 30, "patience": 5, "learning_rate": 0.0001,
            "num_workers": 0, "cpu_threads": 4,
        },
        "runs": [
            run(dataset, horizon, method, seed)
            for dataset in DATASETS for horizon in HORIZONS
            for seed in SEEDS for method in ("ori", "tifo")
        ],
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n")
    print(f"wrote {len(matrix['runs'])} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
