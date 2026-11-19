#!/usr/bin/env python3
"""Aggregate per-run test metrics into a per-cell comparison table.

Input is one or more CSV files with the columns of ``results/runs/*.csv``
(``run_id, dataset, backbone, method, seq_len, pred_len, seed, test_mse,
test_mae``). Use ``--from-records`` to build the same rows from your own
``experiment_records/`` after running ``scripts/run_configs.py``.

Example (main comparison, released numbers)::

    python scripts/summarize_results.py results/runs/main/*.csv \
        results/runs/shared_config/m2_protocol.csv --reference tifo
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]


def rows_from_csv(paths):
    for path in paths:
        with open(path, newline="") as fh:
            yield from csv.DictReader(fh)


def rows_from_records(configs):
    for path in configs:
        for run in json.loads(Path(path).read_text())["runs"]:
            launch = ROOT / "experiment_records" / run["run_id"] / "launch.json"
            if not launch.is_file():
                continue
            rec = json.loads(launch.read_text())
            if "test_mse" in rec:
                yield {**{k: run[k] for k in ("run_id", "dataset", "backbone", "method", "seq_len", "pred_len", "seed")},
                       "test_mse": rec["test_mse"], "test_mae": rec["test_mae"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", type=Path, help="CSV files, or config JSON files with --from-records")
    parser.add_argument("--from-records", action="store_true")
    parser.add_argument("--reference", default="tifo", help="method used for paired seed-level comparisons")
    args = parser.parse_args()

    rows = list(rows_from_records(args.inputs) if args.from_records else rows_from_csv(args.inputs))
    data = {}
    for r in rows:
        key = (r["backbone"], r["dataset"], int(r["pred_len"]), r["method"], int(r["seed"]))
        data[key] = (float(r["test_mse"]), float(r["test_mae"]))
    methods = sorted({k[3] for k in data}, key=lambda m: (m != args.reference, m))
    for bb in sorted({k[0] for k in data}):
        cells = sorted({k[1:3] for k in data if k[0] == bb})
        cell_mean = defaultdict(dict)
        for c in cells:
            for m in methods:
                vals = [v for k, v in data.items() if k[:4] == (bb, *c, m)]
                if vals:
                    cell_mean[m][c] = (statistics.mean(v[0] for v in vals), statistics.mean(v[1] for v in vals))
        common = [c for c in cells if all(c in cell_mean[m] for m in methods)]
        print(f"\n## {bb}: {len(common)} dataset-horizon cells with every method\n")
        print("| method | mean MSE | mean MAE | best-MSE cells | " + f"{args.reference} better (seed pairs) | Wilcoxon p |")
        print("|---|---|---|---|---|---|")
        for m in methods:
            if not common:
                break
            best = sum(cell_mean[m][c][0] == min(cell_mean[x][c][0] for x in methods) for c in common)
            diffs = [data[(bb, *c, m, s)][0] - data[(bb, *c, args.reference, s)][0]
                     for c in common for s in {k[4] for k in data}
                     if (bb, *c, m, s) in data and (bb, *c, args.reference, s) in data]
            test = (f"{sum(d > 0 for d in diffs)}/{len(diffs)} | {wilcoxon(diffs).pvalue:.1e}"
                    if m != args.reference and len(diffs) > 5 and any(diffs) else "— | —")
            print(f"| {m} | {statistics.mean(cell_mean[m][c][0] for c in common):.4f} | "
                  f"{statistics.mean(cell_mean[m][c][1] for c in common):.4f} | {best} | {test} |")


if __name__ == "__main__":
    main()
