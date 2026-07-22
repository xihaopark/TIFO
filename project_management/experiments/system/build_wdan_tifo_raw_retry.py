#!/usr/bin/env python3
"""Reissue two WDAN+TIFO raw candidates with filesystem-safe run IDs."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tune_native_wdan_tifo_critical_h96.json"
OUTPUT = HERE / "retry_native_wdan_tifo_raw_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = [
        run for run in source["runs"] if "_hermitian_raw_a0p5_lr0p25_" in run["run_id"]
    ]
    if len(selected) != 2 or {run["dataset"] for run in selected} != {"ETTh1", "ETTh2"}:
        raise ValueError("expected exactly the ETTh1 and ETTh2 Hermitian-raw candidates")
    runs = []
    for run in selected:
        dataset_id = run["dataset"].lower()
        runs.append(
            {
                **run,
                "run_id": f"wdt_raw_{dataset_id}_h96_s2022",
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "protocol_id": "kdd_resubmit_wdan_tifo_raw_retry_h96_v1",
                "selection_rule": (
                    "Exact reissue of the two Hermitian-raw validation candidates "
                    "whose original checkpoint paths exceeded the filesystem name "
                    "limit; only run IDs are shortened and final testing stays disabled."
                ),
                "defaults": source["defaults"],
                "runs": runs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(runs)} retries to {OUTPUT}")


if __name__ == "__main__":
    main()
