#!/usr/bin/env python3
"""Build the declared PatchTST ETT coverage matrix for the KDD resubmit.

The matrix intentionally expands only the unverified ETT cells.  ETTm2 has a
separately frozen all-horizon three-seed gate, so it is not duplicated here.
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "coverage_patchtst_ett_all_horizons.json"
SEEDS = (2021, 2022, 2023)
HORIZONS = (96, 192, 336, 720)

# These are the original paper's PatchTST architecture choices, recovered from
# its historical result-directory names.  Ori and TIFO receive the same choice.
ARCHITECTURES = {
    "ETTh1": {96: (2, 1), 192: (8, 1), 336: (8, 1), 720: (16, 1)},
    "ETTh2": {96: (4, 3), 192: (4, 3), 336: (4, 3), 720: (4, 3)},
    "ETTm1": {96: (2, 1), 192: (2, 3), 336: (4, 1), 720: (4, 3)},
}


def native_run(dataset, horizon, method, seed):
    n_heads, e_layers = ARCHITECTURES[dataset][horizon]
    model_args = {
        "d_model": 512,
        "d_ff": 2048,
        "e_layers": e_layers,
        "n_heads": n_heads,
        "factor": 3,
        "patch_len": 16,
        "stride": 8,
    }
    if method == "tifo":
        model_args.update({
            "filter_dim": 512,
            "tifo_variant": "historical",
            "tifo_dropout": 0.5,
        })
    return {
        "run_id": f"coverage_patchtst_{dataset.lower()}_h{horizon}_{method}_s{seed}",
        "engine": "native",
        "dataset": dataset,
        "data_type": dataset,
        "root_path": "/home/park/TS/FredNormer/dataset/ETT-small",
        "data_path": f"{dataset}.csv",
        "enc_in": 7,
        "dec_in": 7,
        "c_out": 7,
        "backbone": "PatchTST",
        "method": method,
        "seed": seed,
        "pred_len": horizon,
        "batch_size": 128 if horizon in (192, 720) else 32,
        "model_args": model_args,
    }


def main():
    runs = [
        native_run(dataset, horizon, method, seed)
        for dataset in ARCHITECTURES
        for horizon in HORIZONS
        for seed in SEEDS
        for method in ("ori", "tifo")
    ]
    matrix = {
        "protocol_id": "kdd_resubmit_patchtst_ett_coverage_v1",
        "defaults": {
            "python": "/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python",
            "features": "M",
            "seq_len": 96,
            "label_len": 48,
            "train_epochs": 30,
            "patience": 5,
            "learning_rate": 0.0001,
            "num_workers": 0,
            "cpu_threads": 4,
        },
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
