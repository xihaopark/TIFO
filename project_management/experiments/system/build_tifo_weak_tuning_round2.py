#!/usr/bin/env python3
"""Build the second validation-only search around round-one weak-cell winners."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "coverage_h96_itransformer.json"
OUTPUT = HERE / "tune_tifo_weak_h96_round2.json"


def variants(dataset: str) -> dict[str, dict]:
    if dataset == "ETTh2":
        return {
            **{f"fd{fd}_do{str(do).replace('.', 'p')}": {"filter_dim": fd, "tifo_dropout": do}
               for fd in (64, 128, 256) for do in (0.1, 0.3)},
            **{f"alpha{str(a).replace('.', 'p')}": {"tifo_residual_alpha": a}
               for a in (0.35, 0.45, 0.55, 0.65)},
            "lr0p125": {"tifo_lr_scale": 0.125},
            "lr0p375": {"tifo_lr_scale": 0.375},
        }
    if dataset == "ETTm1":
        return {
            "zpad075": {"tifo_zero_pad_ratio": 0.75},
            "zpad125": {"tifo_zero_pad_ratio": 1.25},
            "zpad150": {"tifo_zero_pad_ratio": 1.5},
            "lr0p5": {"tifo_lr_scale": 0.5},
            "lr0p75": {"tifo_lr_scale": 0.75},
            "alpha0p8": {"tifo_residual_alpha": 0.8},
            "alpha0p9": {"tifo_residual_alpha": 0.9},
            "fd128": {"filter_dim": 128},
            "fd512": {"filter_dim": 512},
        }
    return {
        "zpad150": {"tifo_zero_pad_ratio": 1.5},
        "zpad250": {"tifo_zero_pad_ratio": 2.5},
        "zpad300": {"tifo_zero_pad_ratio": 3.0},
        "alpha0p35": {"tifo_residual_alpha": 0.35},
        "alpha0p65": {"tifo_residual_alpha": 0.65},
        "lr0p125": {"tifo_lr_scale": 0.125},
        "lr0p375": {"tifo_lr_scale": 0.375},
        "compact": {"filter_dim": 256, "tifo_dropout": 0.3},
    }


def base_args(dataset: str, architecture: dict) -> dict:
    common = {**architecture, "tifo_variant": "historical", "skip_final_test": True}
    if dataset == "ETTm1":
        return {**common, "filter_dim": 256, "tifo_dropout": 0.3,
                "tifo_lr_scale": 1.0, "tifo_residual_alpha": 1.0,
                "tifo_zero_pad_ratio": 1.0}
    return {**common, "filter_dim": 512, "tifo_dropout": 0.5,
            "tifo_lr_scale": 0.25, "tifo_residual_alpha": 0.5,
            "tifo_zero_pad_ratio": 2.0 if dataset == "Traffic" else 0.0}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for native in source["runs"]:
        dataset = native.get("dataset")
        if native.get("method") != "ori" or native.get("seed") != 2022 or dataset not in {"ETTh2", "ETTm1", "Traffic"}:
            continue
        shared = {key: value for key, value in native.items()
                  if key not in {"run_id", "engine", "backbone", "method", "model_args"}}
        base = base_args(dataset, native["model_args"])
        for name, override in variants(dataset).items():
            runs.append({**shared,
                         "run_id": f"tune_{dataset.lower()}_h96_tifo_r2_{name}_s2022",
                         "engine": "native", "backbone": "iTransformer", "method": "tifo", "seed": 2022,
                         "model_args": {**base, **override}})
    defaults = {**source["defaults"], "patience": 3}
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_tifo_weak_h96_round2_v1",
        "selection_rule": "Per dataset, select the lowest seed-2022 validation MSE; test is disabled.",
        "defaults": defaults, "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
