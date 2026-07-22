#!/usr/bin/env python3
"""Freeze the validation-balanced ETTh2/H96 WDAN+TIFO candidate."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_wdan_tifo_etth2_extended_loss_h96.json"
METRICS = HERE.parent / "results" / "etth2_extended_validation_metrics.json"
OUTPUT = HERE / "final_wdan_tifo_etth2_balanced_h96.json"


def main() -> None:
    matrix = json.loads(SOURCE.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    by_run = {row["run_id"]: row for row in metrics}
    control = by_run["wtext_etth2_h96_ctrl_s2022"]

    eligible = []
    for run in matrix["runs"]:
        if run["method"] != "wdan_tifo":
            continue
        row = by_run[run["run_id"]]
        if (
            row["validation_mse"] >= control["validation_mse"]
            or row["validation_mae"] >= control["validation_mae"]
        ):
            continue
        mse_gain = (
            control["validation_mse"] - row["validation_mse"]
        ) / control["validation_mse"]
        mae_gain = (
            control["validation_mae"] - row["validation_mae"]
        ) / control["validation_mae"]
        eligible.append((min(mse_gain, mae_gain), run, row, mse_gain, mae_gain))
    if not eligible:
        raise ValueError("no dual-metric validation winner")
    _, selected, selected_metrics, mse_gain, mae_gain = max(
        eligible, key=lambda item: item[0]
    )

    runs = []
    for seed in (2021, 2022, 2023):
        run = json.loads(json.dumps(selected))
        run["run_id"] = f"final_balanced_v2_etth2_h96_s{seed}"
        run["seed"] = seed
        run.pop("skip_final_test", None)
        run["model_args"].pop("skip_final_test", None)
        runs.append(run)
    output = {
        "protocol_id": "kdd_resubmit_wdan_tifo_etth2_balanced_h96_final_v2",
        "selection_rule": (
            "Among candidates that beat the matched WDAN control on both validation "
            "MSE and MAE, maximize the smaller relative improvement so neither metric "
            "is optimized at the expense of the other."
        ),
        "validation_selection": {
            "ETTh2/H96": {
                "selected_run": selected["run_id"],
                "selected_validation_mse": selected_metrics["validation_mse"],
                "selected_validation_mae": selected_metrics["validation_mae"],
                "control_validation_mse": control["validation_mse"],
                "control_validation_mae": control["validation_mae"],
                "relative_mse_gain": mse_gain,
                "relative_mae_gain": mae_gain,
                "eligible_candidate_count": len(eligible),
            }
        },
        "defaults": matrix["defaults"],
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"selected {selected['run_id']} and wrote {OUTPUT}")


if __name__ == "__main__":
    main()
