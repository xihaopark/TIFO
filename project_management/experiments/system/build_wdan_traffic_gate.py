#!/usr/bin/env python3
"""Build a validation-only WDAN configuration gate for Traffic H96."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_wdan_traffic_config.json"

CANDIDATES = {
    "generic": dict(levels=2, window=12, dim=128, layers=0, twice=0, lr=0.0001),
    "ecl": dict(levels=3, window=12, dim=512, layers=1, twice=2, lr=0.001),
    "weather": dict(levels=2, window=5, dim=512, layers=2, twice=1, lr=0.0001),
    "sensor_deep": dict(levels=3, window=5, dim=512, layers=2, twice=1, lr=0.001),
}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    native = next(
        run for run in source["runs"]
        if run.get("dataset") == "Traffic" and run.get("method") == "ori" and run.get("seed") == 2022
    )
    shared = {key: value for key, value in native.items()
              if key not in {"run_id", "engine", "backbone", "method", "model_args"}}
    runs = []
    for name, cfg in CANDIDATES.items():
        runs.append({
            **shared,
            "run_id": f"tune_traffic_h96_wdan_{name}_s2022",
            "engine": "wdan",
            "seed": 2022,
            "model_args": {
                **native["model_args"],
                "enc_in": native["enc_in"], "dec_in": native["dec_in"], "c_out": native["c_out"],
                "stats_dwt_levels": cfg["levels"], "stats_window_len": cfg["window"],
                "stats_d_model": cfg["dim"], "stats_d_ff": cfg["dim"],
                "stats_ffn_layers": cfg["layers"], "stats_dropout": 0.1,
                "base_stats_lr": cfg["lr"], "stats_strategy": "stats_bb_union",
                "twice_epoch": cfg["twice"], "loss_type": "mse", "skip_final_test": True,
            },
        })
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_wdan_traffic_config_gate_v1",
        "selection_rule": "Select the lowest seed-2022 validation MSE; test evaluation is disabled.",
        "defaults": source["defaults"], "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
