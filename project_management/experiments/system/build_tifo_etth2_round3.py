#!/usr/bin/env python3
"""Build a focused ETTh2 grid combining the two best round-two controls."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_tifo_etth2_h96_round3.json"


def token(value: float) -> str:
    return str(value).replace(".", "p")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    native = next(run for run in source["runs"]
                  if run.get("dataset") == "ETTh2" and run.get("method") == "ori" and run.get("seed") == 2022)
    shared = {key: value for key, value in native.items()
              if key not in {"run_id", "engine", "backbone", "method", "model_args"}}
    runs = []
    for lr in (0.0625, 0.1, 0.125, 0.15, 0.1875):
        for alpha in (0.25, 0.3, 0.35, 0.4, 0.45, 0.5):
            runs.append({
                **shared,
                "run_id": f"tune_etth2_h96_tifo_r3_lr{token(lr)}_alpha{token(alpha)}_s2022",
                "engine": "native", "backbone": "iTransformer", "method": "tifo", "seed": 2022,
                "model_args": {**native["model_args"], "filter_dim": 512,
                               "tifo_variant": "historical", "tifo_dropout": 0.5,
                               "tifo_lr_scale": lr, "tifo_residual_alpha": alpha,
                               "tifo_zero_pad_ratio": 0.0, "skip_final_test": True},
            })
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_tifo_etth2_h96_round3_v1",
        "selection_rule": "Select the lowest seed-2022 validation MSE; test is disabled.",
        "defaults": {**source["defaults"], "patience": 3}, "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
