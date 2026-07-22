#!/usr/bin/env python3
"""Freeze a WDAN+TIFO cell only when both validation metrics improve."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SEEDS = (2021, 2022, 2023)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", required=True)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    by_id = {run["run_id"]: run for run in matrix["runs"]}
    metric_by_id = {row["run_id"]: row for row in metrics}
    if len(by_id) != 8 or set(by_id) != set(metric_by_id):
        raise ValueError("matrix and dual-metric validation evidence must match exactly")
    controls = [run for run in matrix["runs"] if run["method"] == "wdan"]
    candidates = [run for run in matrix["runs"] if run["method"] == "wdan_tifo"]
    if len(controls) != 1 or len(candidates) != 7:
        raise ValueError("expected one WDAN control and seven WDAN+TIFO candidates")
    control = metric_by_id[controls[0]["run_id"]]
    eligible = [
        run
        for run in candidates
        if metric_by_id[run["run_id"]]["validation_mse"] < control["validation_mse"]
        and metric_by_id[run["run_id"]]["validation_mae"] < control["validation_mae"]
    ]
    if not eligible:
        raise SystemExit("no WDAN+TIFO candidate improves both validation metrics")
    winner = min(
        eligible,
        key=lambda run: (
            metric_by_id[run["run_id"]]["validation_mse"],
            metric_by_id[run["run_id"]]["validation_mae"],
            run["run_id"],
        ),
    )
    selected = metric_by_id[winner["run_id"]]
    final_runs = []
    for seed in SEEDS:
        model_args = dict(winner["model_args"])
        model_args.pop("skip_final_test", None)
        final_runs.append(
            {
                **{
                    key: value
                    for key, value in winner.items()
                    if key not in {"run_id", "seed", "model_args"}
                },
                "run_id": f"final_wdan_tifo_{args.dataset.lower()}_h96_s{seed}",
                "seed": seed,
                "model_args": model_args,
            }
        )
    output = {
        "protocol_id": args.protocol,
        "selection_rule": (
            "Require sample-weighted validation MSE and MAE to both beat the "
            "matched WDAN control; among eligible candidates freeze the lowest "
            "validation MSE, then evaluate seeds 2021--2023 without reselection."
        ),
        "validation_selection": {
            f"{args.dataset}/H96": {
                "selected_run": winner["run_id"],
                "selected_validation_mse": selected["validation_mse"],
                "selected_validation_mae": selected["validation_mae"],
                "control_run": controls[0]["run_id"],
                "control_validation_mse": control["validation_mse"],
                "control_validation_mae": control["validation_mae"],
                "eligible_candidate_count": len(eligible),
            }
        },
        "defaults": matrix["defaults"],
        "runs": final_runs,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"froze {winner['run_id']} into {args.output}")


if __name__ == "__main__":
    main()
