#!/usr/bin/env python3
"""Build the matched ACN/WDAN H96 matrix from the frozen native coverage task."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).with_name("coverage_h96_itransformer.json")
OUTPUT = Path(__file__).with_name("plugin_baselines_h96_itransformer.json")

ACN_TEMPERATURE = {
    "ETTh1": 0.5, "ETTh2": 0.05, "ETTm1": 0.1, "ETTm2": 0.05,
    "Electricity": 0.05, "Weather": 0.05, "Traffic": 0.1,
}

# H96 statistics-network settings from the official WDAN iTransformer script.
# Traffic is absent upstream, so the ECL-style candidate is frozen by the
# validation-only Traffic gate.
WDAN_H96 = {
    "ETTh1": (2, 12, 128, 0, 0, 0.0001),
    "ETTh2": (2, 5, 128, 0, 0, 0.0001),
    "ETTm1": (3, 5, 128, 2, 1, 0.001),
    "ETTm2": (2, 12, 128, 0, 2, 0.001),
    "Electricity": (3, 12, 512, 1, 2, 0.001),
    "Weather": (2, 5, 512, 2, 1, 0.0001),
    "Traffic": (3, 12, 512, 1, 2, 0.001),
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ettm2_source = json.loads(
        Path(__file__).with_name("gate_ettm2_96.json").read_text(encoding="utf-8")
    )
    runs = []
    source_runs = source["runs"] + [
        {**ettm2_source["defaults"], **run}
        for run in ettm2_source["runs"]
        if run.get("engine") == "native" and run.get("method") == "ori"
    ]
    for native in source_runs:
        if native["method"] != "ori":
            continue
        shared = {
            key: value
            for key, value in native.items()
            if key not in {"run_id", "engine", "backbone", "method", "model_args"}
        }
        architecture = dict(native["model_args"])
        dataset_id = native["dataset"].lower()
        seed = native["seed"]
        temperature = ACN_TEMPERATURE[native["dataset"]]
        levels, window, stats_dim, stats_layers, twice, stats_lr = WDAN_H96[native["dataset"]]
        temp_token = str(temperature).replace(".", "p")
        runs.append(
            {
                **shared,
                "run_id": f"plugin_h96_{dataset_id}_acn_t{temp_token}_s{seed}",
                "engine": "acn",
                "model_args": {**architecture, "temperature": temperature},
            }
        )
        runs.append(
            {
                **shared,
                "run_id": f"plugin_h96_{dataset_id}_wdan_officialh96_s{seed}",
                "engine": "wdan",
                "model_args": {
                    **architecture,
                    "enc_in": native["enc_in"],
                    "dec_in": native["dec_in"],
                    "c_out": native["c_out"],
                    "stats_dwt_levels": levels,
                    "stats_window_len": window,
                    "stats_d_model": stats_dim,
                    "stats_d_ff": stats_dim,
                    "stats_ffn_layers": stats_layers,
                    "stats_dropout": 0.1,
                    "base_stats_lr": stats_lr,
                    "stats_strategy": "stats_bb_union",
                    "twice_epoch": twice,
                    "loss_type": "mse",
                },
            }
        )
    matrix = {
        "protocol_id": "kdd_resubmit_plugin_baselines_h96_v2",
        "defaults": dict(source["defaults"]),
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
