#!/usr/bin/env python3
"""Build the matched ACN/WDAN H96 matrix from the frozen native coverage task."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).with_name("coverage_h96_itransformer.json")
OUTPUT = Path(__file__).with_name("plugin_baselines_h96_itransformer.json")


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
        runs.append(
            {
                **shared,
                "run_id": f"plugin_h96_{dataset_id}_acn_s{seed}",
                "engine": "acn",
                "model_args": architecture,
            }
        )
        runs.append(
            {
                **shared,
                "run_id": f"plugin_h96_{dataset_id}_wdan_s{seed}",
                "engine": "wdan",
                "model_args": {
                    **architecture,
                    "enc_in": native["enc_in"],
                    "dec_in": native["dec_in"],
                    "c_out": native["c_out"],
                    "stats_dwt_levels": 2,
                    "stats_window_len": 12,
                    "stats_d_model": 128,
                    "stats_d_ff": 128,
                    "stats_ffn_layers": 0,
                    "stats_dropout": 0.1,
                    "base_stats_lr": 0.0001,
                    "stats_strategy": "stats_bb_union",
                    "twice_epoch": 0,
                    "loss_type": "mse",
                },
            }
        )
    matrix = {
        "protocol_id": "kdd_resubmit_plugin_baselines_h96_v1",
        "defaults": dict(source["defaults"]),
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
