#!/usr/bin/env python3
"""Independently verify every numeric input to the regenerated KDD main table.

This audit deliberately reads the source CSV rows rather than trusting the
rendered TeX.  For every selected dataset/horizon/seed value it checks that
the recorded launch completed and that the final ``mse``/``mae`` in its log
matches the CSV.  It also produces a compact, reviewable Markdown report.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

from build_legacy_kdd_main_table import SOURCES, classify


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "project_management" / "experiments" / "results"
RECORDS = ROOT / "experiment_records"
METRIC = re.compile(r"mse:\s*([0-9.eE+-]+),\s*mae:\s*([0-9.eE+-]+)")


def selected_rows() -> dict[tuple[str, str, str, int, int], tuple[dict[str, str], int, str]]:
    selected: dict[tuple[str, str, str, int, int], tuple[dict[str, str], int, str]] = {}
    for source, priority in SOURCES:
        with (RESULTS / source).open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                kind = classify(row["method"], source)
                if kind is None:
                    continue
                key = (*kind, row["dataset"], int(row["pred_len"]), int(row["seed"]))
                previous = selected.get(key)
                if previous is None or priority > previous[1]:
                    selected[key] = (row, priority, source)
                elif priority == previous[1] and (
                    row["mse"], row["mae"]
                ) != (previous[0]["mse"], previous[0]["mae"]):
                    raise RuntimeError(f"conflicting selected evidence for {key}")
    return selected


def main() -> None:
    rows = selected_rows()
    expected = 2 * 2 * 7 * 4 * 3
    if len(rows) != expected:
        raise SystemExit(f"expected {expected} selected inputs, found {len(rows)}")

    failures: list[str] = []
    checked = 0
    recovered = 0
    source_counts: dict[str, int] = {}
    for key, (row, _priority, source) in rows.items():
        source_counts[source] = source_counts.get(source, 0) + 1
        run_id = row.get("run_id")
        log_file = row.get("log_file")
        if not run_id or not log_file:
            failures.append(f"{key}: missing run_id/log_file in {source}")
            continue
        launch_path = RECORDS / run_id / "launch.json"
        if not launch_path.is_file():
            failures.append(f"{key}: missing {launch_path}")
            continue
        launch = json.loads(launch_path.read_text(encoding="utf-8"))
        if launch.get("status") != "completed" or launch.get("returncode") != 0:
            failures.append(f"{key}: launch not successfully completed")
            continue
        if launch.get("final_test_provenance"):
            recovered += 1
        path = Path(log_file)
        if not path.is_file():
            failures.append(f"{key}: missing result log {path}")
            continue
        matches = METRIC.findall(path.read_text(encoding="utf-8", errors="replace"))
        if not matches:
            failures.append(f"{key}: no final MSE/MAE in {path}")
            continue
        mse, mae = map(float, matches[-1])
        if not (math.isclose(mse, float(row["mse"]), rel_tol=0, abs_tol=1e-9)
                and math.isclose(mae, float(row["mae"]), rel_tol=0, abs_tol=1e-9)):
            failures.append(f"{key}: CSV/log mismatch ({row['mse']}/{row['mae']} vs {mse}/{mae})")
            continue
        checked += 1

    report = RESULTS / "kdd_resubmit_legacy_main_table_audit.md"
    lines = [
        "# Legacy KDD main-table provenance audit",
        "",
        f"- Selected inputs: {len(rows)} (expected {expected})",
        f"- CSV-to-log verified: {checked}",
        f"- Failures: {len(failures)}",
        f"- Recovered final-test checkpoints: {recovered}",
        "",
        "## Selected input sources",
        "",
        "| CSV source | Inputs |",
        "|---|---:|",
        *[f"| `{source}` | {count} |" for source, count in sorted(source_counts.items())],
    ]
    if failures:
        lines.extend(("", "## Failures", "", *[f"- {failure}" for failure in failures]))
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    print(f"verified {checked}/{len(rows)} selected inputs; failures={len(failures)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
