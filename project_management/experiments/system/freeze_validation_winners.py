#!/usr/bin/env python3
"""Freeze one validation winner per dataset-horizon cell for three-seed testing."""

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
    parser.add_argument("--method", required=True)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    validation = json.loads(args.validation.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    validation_ids = {row["run_id"] for row in validation}
    if validation_ids != set(by_id):
        missing = sorted(set(by_id) - validation_ids)
        unexpected = sorted(validation_ids - set(by_id))
        raise ValueError(
            f"validation matrix is incomplete: missing={missing[:5]} "
            f"unexpected={unexpected[:5]}"
        )

    cells = defaultdict(list)
    for row in validation:
        cells[(row["dataset"], int(row["pred_len"]))].append(row)
    if any(len(rows) != 8 for rows in cells.values()):
        sizes = {f"{dataset}/H{horizon}": len(rows) for (dataset, horizon), rows in cells.items()}
        raise ValueError(f"each cell must contain exactly eight candidates: {sizes}")

    final_runs = []
    selected = {}
    for (dataset, horizon), rows in sorted(cells.items()):
        winner = min(rows, key=lambda row: (row["validation_mse"], row["run_id"]))
        template = by_id[winner["run_id"]]
        cell = f"{dataset}/H{horizon}"
        selected[cell] = {
            "selected_run": winner["run_id"],
            "selected_validation_mse": winner["validation_mse"],
            "candidate_count": len(rows),
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
                        f"final_native_{args.method.lower()}_"
                        f"{template['backbone'].lower()}_{dataset.lower()}_"
                        f"h{horizon}_s{seed}"
                    ),
                    "seed": seed,
                    "model_args": model_args,
                }
            )

    output = {
        "protocol_id": args.protocol,
        "selection_rule": (
            "For every dataset-horizon cell, freeze the lowest seed-2022 validation "
            "MSE among exactly eight candidates before reading final-test metrics; "
            "evaluate the frozen configuration on seeds 2021, 2022, and 2023."
        ),
        "validation_selection": selected,
        "defaults": matrix["defaults"],
        "runs": final_runs,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"froze {len(cells)} cells into {len(final_runs)} final runs at {args.output}")


if __name__ == "__main__":
    main()
