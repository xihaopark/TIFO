#!/usr/bin/env python3
"""Promote only validation-winning ACN+TIFO configurations to three-seed tests."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
VALIDATION = RESULTS / "acn_tifo_composition_gate.json"
SOURCE = HERE / "plugin_baselines_h96_itransformer.json"
OUTPUT = HERE / "final_acn_tifo_composition_h96.json"


def main() -> None:
    rows = json.loads(VALIDATION.read_text(encoding="utf-8"))
    by_dataset = {}
    for row in rows:
        by_dataset.setdefault(row["dataset"], []).append(row)

    selections = {}
    for dataset, candidates in by_dataset.items():
        control = min(row["validation_mse"] for row in candidates if "_control_" in row["run_id"])
        winner = min(candidates, key=lambda row: row["validation_mse"])
        if "_acn_tifo_" in winner["run_id"] and winner["validation_mse"] < control:
            selections[dataset] = {
                "validation_mse": winner["validation_mse"],
                "control_validation_mse": control,
                "model_args": json.loads(winner["model_args"]),
                "source_run_id": winner["run_id"],
            }

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for base in source["runs"]:
        dataset = base.get("dataset")
        if base.get("engine") != "acn" or dataset not in selections:
            continue
        model_args = {**base["model_args"], **selections[dataset]["model_args"]}
        model_args.pop("skip_final_test", None)
        runs.append({
            **{key: value for key, value in base.items() if key not in {"run_id", "model_args"}},
            "run_id": f"final_{dataset.lower()}_h96_acn_tifo_s{base['seed']}",
            "model_args": model_args,
        })

    if not runs:
        raise SystemExit("no ACN+TIFO candidate beat its ACN validation control")
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_acn_tifo_composition_final_h96_v1",
        "selection_rule": "Promote only the per-dataset ACN+TIFO validation winner when it beats ACN control.",
        "validation_selections": selections,
        "defaults": source["defaults"],
        "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"promoted {len(selections)} datasets into {len(runs)} final runs")


if __name__ == "__main__":
    main()
