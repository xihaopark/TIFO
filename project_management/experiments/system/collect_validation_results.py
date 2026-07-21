#!/usr/bin/env python3
"""Collect and rank validation-only experiment records without reading test metrics."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parents[1] / "results"
PATTERNS = (
    re.compile(r"Vali Loss:\s*(?P<value>[-+0-9.eE]+)"),
    re.compile(r"Val Epoch \d+: average loss:\s*(?P<value>[-+0-9.eE]+)"),
    re.compile(r"Best Validation MSE:\s*(?P<value>[-+0-9.eE]+)"),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    rows = []
    for record_path in sorted((ROOT / "experiment_records").glob("*/launch.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("protocol_id") != args.protocol or record.get("status") != "completed":
            continue
        log_text = Path(record["log_file"]).read_text(encoding="utf-8", errors="replace")
        values = [float(match.group("value")) for pattern in PATTERNS for match in pattern.finditer(log_text)]
        if not values:
            raise SystemExit(f"completed tuning run has no validation metric: {record_path}")
        cfg = record["resolved_config"]
        rows.append({
            "run_id": record["run_id"], "engine": record["engine"],
            "dataset": cfg["dataset"], "seed": cfg["seed"],
            "validation_mse": min(values),
            "model_args": json.dumps(cfg.get("model_args", {}), sort_keys=True),
            "log_file": record["log_file"],
        })
    rows.sort(key=lambda row: (row["dataset"], row["validation_mse"], row["run_id"]))
    RESULTS.mkdir(parents=True, exist_ok=True)
    stem = RESULTS / args.name
    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys() if rows else ())
        if rows:
            writer.writeheader(); writer.writerows(rows)
    stem.with_suffix(".json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    md = ["# Validation-only selection", "", "| Dataset | Run | Validation MSE |", "|---|---|---:|"]
    md.extend(f"| {row['dataset']} | {row['run_id']} | {row['validation_mse']:.8f} |" for row in rows)
    stem.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"collected {len(rows)} validation-only runs to {stem}.md")


if __name__ == "__main__":
    main()
