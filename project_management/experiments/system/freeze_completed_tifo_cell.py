#!/usr/bin/env python3
"""Freeze one fully completed eight-candidate TIFO cell for final testing."""

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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", required=True)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    validation = json.loads(args.validation.read_text(encoding="utf-8"))
    matrix_runs = {
        run["run_id"]: run
        for run in matrix["runs"]
        if run["dataset"] == args.dataset and int(run["pred_len"]) == 96
    }
    rows = [
        row
        for row in validation
        if row["dataset"] == args.dataset and int(row["pred_len"]) == 96
    ]
    if len(matrix_runs) != 8 or len(rows) != 8:
        raise ValueError(
            f"{args.dataset}/H96 must have exactly eight matrix and validation rows"
        )
    if {row["run_id"] for row in rows} != set(matrix_runs):
        raise ValueError(f"{args.dataset}/H96 validation rows do not match the matrix")

    winner = min(rows, key=lambda row: (row["validation_mse"], row["run_id"]))
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
                    f"final_tifo_cellarch_{args.dataset.lower()}_h96_s{seed}"
                ),
                "seed": seed,
                "model_args": model_args,
            }
        )

    args.output.write_text(
        json.dumps(
            {
                "protocol_id": args.protocol,
                "selection_rule": (
                    "Freeze the lowest seed-2022 validation MSE among exactly "
                    "eight declared candidates for this dataset/H96 cell, then "
                    "evaluate seeds 2021, 2022, and 2023 without further selection."
                ),
                "validation_selection": {
                    f"{args.dataset}/H96": {
                        "selected_run": winner["run_id"],
                        "selected_validation_mse": winner["validation_mse"],
                        "candidate_count": 8,
                    }
                },
                "defaults": matrix["defaults"],
                "runs": final_runs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"froze {winner['run_id']} at validation MSE "
        f"{winner['validation_mse']} into {args.output}"
    )


if __name__ == "__main__":
    main()
