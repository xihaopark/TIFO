#!/usr/bin/env python3
"""Freeze one complete ACN+TIFO validation cell for three-seed testing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SEEDS = (2021, 2022, 2023)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--horizon", type=int, default=96)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", required=True)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    validation = json.loads(args.validation.read_text(encoding="utf-8"))
    default_horizon = int(matrix["defaults"]["pred_len"])
    matrix_runs = {
        run["run_id"]: run
        for run in matrix["runs"]
        if run["dataset"] == args.dataset
        and int(run.get("pred_len", default_horizon)) == args.horizon
    }
    rows = [
        row
        for row in validation
        if row["dataset"] == args.dataset and int(row["pred_len"]) == args.horizon
    ]
    if len(matrix_runs) != 8 or len(rows) != 8:
        raise ValueError(
            f"{args.dataset}/H{args.horizon} requires exactly eight completed rows"
        )
    if {row["run_id"] for row in rows} != set(matrix_runs):
        raise ValueError("validation rows do not exactly match the declared cell matrix")
    controls = [row for row in rows if "_acn_control_" in row["run_id"]]
    candidates = [row for row in rows if "_acn_control_" not in row["run_id"]]
    if len(controls) != 1 or len(candidates) != 7:
        raise ValueError("expected one ACN control and seven ACN+TIFO candidates")
    control = controls[0]
    winner = min(candidates, key=lambda row: (row["validation_mse"], row["run_id"]))
    if winner["validation_mse"] >= control["validation_mse"]:
        raise SystemExit("ACN+TIFO winner does not beat the matched ACN control")

    template = matrix_runs[winner["run_id"]]
    final_runs = []
    for seed in SEEDS:
        model_args = dict(template["model_args"])
        model_args.pop("skip_final_test", None)
        final_runs.append(
            {
                **{
                    key: value
                    for key, value in template.items()
                    if key not in {"run_id", "seed", "model_args"}
                },
                "run_id": (
                    f"final_native_acn_tifo_{args.dataset.lower()}_"
                    f"h{args.horizon}_s{seed}"
                ),
                "seed": seed,
                "model_args": model_args,
            }
        )
    output = {
        "protocol_id": args.protocol,
        "selection_rule": (
            "Freeze the lowest seed-2022 validation MSE among seven ACN+TIFO "
            "candidates only after it beats the matched ACN control, then evaluate "
            "seeds 2021, 2022, and 2023 without reselection."
        ),
        "validation_selection": {
            f"{args.dataset}/H{args.horizon}": {
                "selected_run": winner["run_id"],
                "selected_validation_mse": winner["validation_mse"],
                "control_run": control["run_id"],
                "control_validation_mse": control["validation_mse"],
            }
        },
        "defaults": matrix["defaults"],
        "runs": final_runs,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"froze {winner['run_id']} into {args.output}")


if __name__ == "__main__":
    main()
