#!/usr/bin/env python3
"""Check that every promoted iTransformer TIFO setting was validation-selected.

For H=96 and the remaining horizons independently, this verifies the complete
validation matrix, the declared lowest-MSE winner, and equality of the frozen
winner's model arguments to all three final-test runs.  Test metrics are never
consulted for configuration selection.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SYSTEM = ROOT / "project_management" / "experiments" / "system"
RESULTS = ROOT / "project_management" / "experiments" / "results"
RECORDS = ROOT / "experiment_records"


def audit_protocol(filename: str) -> tuple[int, int, list[str]]:
    protocol = json.loads((SYSTEM / filename).read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / protocol["source_matrix"]).read_text(encoding="utf-8"))
    # The protocol points to the machine-readable JSON collection; the CSV
    # counterpart is the row-level validation ledger needed for this audit.
    validation_path = (ROOT / protocol["validation_evidence"]).with_suffix(".csv")
    validation = list(csv.DictReader(validation_path.open(newline="", encoding="utf-8")))
    by_cell: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in validation:
        by_cell[(row["dataset"], int(row["pred_len"]))].append(row)
    candidates: dict[str, dict] = {r["run_id"]: r for r in matrix["runs"]}
    finals: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for run in protocol["runs"]:
        finals[(run["dataset"], int(run.get("pred_len", protocol["defaults"].get("pred_len"))))].append(run)

    failures: list[str] = []
    candidate_total = 0
    for cell, selection in protocol["validation_selection"].items():
        dataset, horizon_text = cell.split("/H")
        horizon = int(horizon_text)
        rows = by_cell[(dataset, horizon)]
        candidate_total += len(rows)
        winner = min(rows, key=lambda r: float(r["validation_mse"]))
        selected = selection["selected_run"]
        if winner["run_id"] != selected:
            failures.append(f"{cell}: selected {selected}, validation minimum is {winner['run_id']}")
            continue
        if not math.isclose(float(winner["validation_mse"]), float(selection["selected_validation_mse"]), abs_tol=1e-7):
            failures.append(f"{cell}: stored validation score disagrees")
        candidate = candidates.get(selected)
        if candidate is None:
            failures.append(f"{cell}: selected candidate not in matrix")
            continue
        candidate_record = RECORDS / selected / "launch.json"
        if not candidate_record.is_file() or json.loads(candidate_record.read_text()).get("status") != "completed":
            failures.append(f"{cell}: selected validation run incomplete")
        expected_args = {k: v for k, v in candidate["model_args"].items() if k != "skip_final_test"}
        final_runs = finals[(dataset, horizon)]
        if len(final_runs) != 3:
            failures.append(f"{cell}: expected 3 final seeds, found {len(final_runs)}")
        for final in final_runs:
            if final["model_args"] != expected_args:
                failures.append(f"{cell}: final {final['run_id']} arguments differ from selected validation winner")
            path = RECORDS / final["run_id"] / "launch.json"
            if not path.is_file() or json.loads(path.read_text()).get("status") != "completed":
                failures.append(f"{cell}: final {final['run_id']} incomplete")
    return len(protocol["validation_selection"]), candidate_total, failures


def main() -> None:
    cells = candidates = 0
    failures: list[str] = []
    for file in ("final_tifo_itransformer_h96_full.json", "final_tifo_itransformer_remaining_horizons.json"):
        n_cells, n_candidates, errors = audit_protocol(file)
        cells += n_cells
        candidates += n_candidates
        failures.extend(f"{file}: {error}" for error in errors)
    report = RESULTS / "kdd_resubmit_tifo_selection_audit.md"
    report.write_text(
        "# TIFO validation-selection audit\n\n"
        f"- Dataset-horizon cells: {cells}\n"
        f"- Validation candidates checked: {candidates}\n"
        f"- Validation winner and frozen final configuration checks: {cells - len({x.split(': ', 1)[0] for x in failures})}/{cells}\n"
        f"- Failures: {len(failures)}\n"
        + ("\n## Failures\n\n" + "\n".join(f"- {x}" for x in failures) + "\n" if failures else ""),
        encoding="utf-8",
    )
    print(report)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
