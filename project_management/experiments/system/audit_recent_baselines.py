#!/usr/bin/env python3
"""Verify the exact 24 run-level values used by the recent-baseline table."""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

from build_recent_baseline_table import DATASETS, SOURCES, TARGETS, SEEDS


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "project_management" / "experiments" / "results"
RECORDS = ROOT / "experiment_records"
METRIC = re.compile(r"mse:\s*([0-9.eE+-]+),\s*mae:\s*([0-9.eE+-]+)")


def main() -> None:
    selected: dict[tuple[str, str, int], dict[str, str]] = {}
    for source in SOURCES:
        with (RESULTS / source).open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (row["dataset"], row["method"], int(row["seed"]))
                if row["dataset"] in DATASETS and int(row["pred_len"]) == 96 and row["method"] in TARGETS:
                    prior = selected.get(key)
                    if prior and (prior["mse"], prior["mae"]) != (row["mse"], row["mae"]):
                        raise SystemExit(f"conflicting evidence for {key}")
                    selected[key] = row
    expected = {(d, m, s) for d in DATASETS for m in TARGETS for s in SEEDS}
    if set(selected) != expected:
        raise SystemExit(f"incomplete evidence: missing={sorted(expected - set(selected))}")
    failures: list[str] = []
    for key, row in selected.items():
        launch = RECORDS / row["run_id"] / "launch.json"
        log = Path(row["log_file"])
        if not launch.is_file() or not log.is_file():
            failures.append(f"{key}: missing launch/log")
            continue
        record = json.loads(launch.read_text(encoding="utf-8"))
        matches = METRIC.findall(log.read_text(encoding="utf-8", errors="replace"))
        if record.get("status") != "completed" or record.get("returncode") != 0 or not matches:
            failures.append(f"{key}: unsuccessful run or no metrics")
            continue
        mse, mae = map(float, matches[-1])
        if not (math.isclose(mse, float(row["mse"]), abs_tol=1e-9)
                and math.isclose(mae, float(row["mae"]), abs_tol=1e-9)):
            failures.append(f"{key}: CSV/log mismatch")
    report = RESULTS / "kdd_resubmit_recent_baselines_audit.md"
    report.write_text(
        "# Recent-baseline provenance audit\n\n"
        f"- Selected inputs: {len(selected)} (expected {len(expected)})\n"
        f"- CSV-to-log verified: {len(selected) - len(failures)}\n"
        f"- Failures: {len(failures)}\n"
        + ("\n## Failures\n\n" + "\n".join(f"- {x}" for x in failures) + "\n" if failures else ""),
        encoding="utf-8",
    )
    print(report)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
