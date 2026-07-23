#!/usr/bin/env python3
"""Freeze per-cell validation winners into a three-seed final-test matrix."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


SEEDS = (2021, 2022, 2023)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--expected-candidates", type=int, required=True)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    validation = json.loads(args.validation.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    if len(by_id) != len(matrix["runs"]):
        raise ValueError("source matrix contains duplicate run IDs")
    if {row["run_id"] for row in validation} != set(by_id):
        missing = sorted(set(by_id) - {row["run_id"] for row in validation})
        extra = sorted({row["run_id"] for row in validation} - set(by_id))
        raise ValueError(f"validation/source mismatch: missing={missing}, extra={extra}")

    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in validation:
        grouped[(row["dataset"], int(row["pred_len"]))].append(row)

    winners = {}
    final_runs = []
    for (dataset, horizon), rows in sorted(grouped.items()):
        if len(rows) != args.expected_candidates:
            raise ValueError(
                f"{dataset}/H{horizon}: expected {args.expected_candidates} "
                f"validation candidates, got {len(rows)}"
            )
        winner = min(rows, key=lambda row: (row["validation_mse"], row["run_id"]))
        template = by_id[winner["run_id"]]
        winners[f"{dataset}/H{horizon}"] = {
            "selected_run": winner["run_id"],
            "selected_validation_mse": winner["validation_mse"],
        }
        for seed in SEEDS:
            model_args = dict(template.get("model_args", {}))
            model_args.pop("skip_final_test", None)
            final_runs.append(
                {
                    **{
                        key: value
                        for key, value in template.items()
                        if key not in {"run_id", "seed", "model_args"}
                    },
                    "run_id": (
                        f"final_tifo_{template['backbone'].lower()}_"
                        f"{dataset.lower()}_h{horizon}_s{seed}"
                    ),
                    "seed": seed,
                    "model_args": model_args,
                }
            )

    output = {
        "protocol_id": args.protocol,
        "selection_rule": (
            "For each dataset-backbone-horizon cell, freeze the lowest seed-2022 "
            "validation-MSE configuration before evaluating the final test split "
            "with seeds 2021, 2022, and 2023."
        ),
        "source_matrix": str(args.matrix),
        "validation_evidence": str(args.validation),
        "validation_selection": winners,
        "defaults": matrix["defaults"],
        "runs": final_runs,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"froze {len(winners)} cells into {len(final_runs)} final runs at {args.output}")


if __name__ == "__main__":
    main()
