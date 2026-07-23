#!/usr/bin/env python3
"""Assemble canonical evidence rows for the full plug-in comparison table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def json_rows(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"{path}: expected a JSON list")
    return value


def local_plugin_rows(path: Path, method: str) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "source": "local_matched_three_seed_final",
                    "backbone": "iTransformer",
                    "method": method,
                    "dataset": row["dataset"],
                    "pred_len": int(row["pred_len"]),
                    "seed": int(row["seed"]),
                    "mse": float(row["mse"]),
                    "mae": float(row["mae"]),
                    "run_id": row["run_id"],
                    "protocol_id": row["protocol_id"],
                }
            )
    return rows


def local_tifo_rows(path: Path, backbone: str) -> list[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "source": "local_validation_selected_final",
                    "backbone": backbone,
                    "method": "TIFO",
                    "dataset": row["dataset"],
                    "pred_len": int(row["pred_len"]),
                    "seed": int(row["seed"]),
                    "mse": float(row["mse"]),
                    "mae": float(row["mae"]),
                    "run_id": row["run_id"],
                    "protocol_id": row["protocol_id"],
                }
            )
    return rows


def apply_tifo_selection(rows: list[dict], path: Path) -> list[dict]:
    """Resolve cells with multiple frozen protocols using an explicit manifest."""
    selection = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(selection, dict):
        raise ValueError(f"{path}: expected a JSON object")

    grouped: dict[tuple[str, str, int], list[dict]] = {}
    for row in rows:
        key = (row["backbone"], row["dataset"], int(row["pred_len"]))
        grouped.setdefault(key, []).append(row)

    selected = []
    for key, cell_rows in grouped.items():
        manifest_key = "|".join((key[0], key[1], str(key[2])))
        protocols = {row["protocol_id"] for row in cell_rows}
        chosen_protocol = selection.get(manifest_key)
        if chosen_protocol is None:
            if len(protocols) != 1:
                raise ValueError(
                    f"{manifest_key}: multiple TIFO protocols {sorted(protocols)}; "
                    "add an explicit selection"
                )
            chosen_protocol = next(iter(protocols))
        elif chosen_protocol not in protocols:
            raise ValueError(
                f"{manifest_key}: selected protocol {chosen_protocol!r} is not "
                f"present; available={sorted(protocols)}"
            )
        chosen_rows = [
            row for row in cell_rows if row["protocol_id"] == chosen_protocol
        ]
        seeds = sorted(row["seed"] for row in chosen_rows)
        if seeds != [2021, 2022, 2023]:
            raise ValueError(
                f"{manifest_key}: selected protocol must have seeds 2021--2023; "
                f"found {seeds}"
            )
        selected.extend(chosen_rows)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--reported-recent", type=Path, required=True)
    parser.add_argument("--local-acn", type=Path)
    parser.add_argument("--local-wdan", type=Path)
    parser.add_argument("--tifo-itransformer", type=Path, nargs="*", default=[])
    parser.add_argument("--tifo-dlinear", type=Path, nargs="*", default=[])
    parser.add_argument(
        "--tifo-selection",
        type=Path,
        help="JSON map backbone|dataset|horizon -> frozen protocol_id",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = json_rows(args.legacy) + json_rows(args.reported_recent)
    if args.local_acn:
        rows.extend(local_plugin_rows(args.local_acn, "ACN"))
    if args.local_wdan:
        rows.extend(local_plugin_rows(args.local_wdan, "WDAN"))
    tifo_rows = []
    for path in args.tifo_itransformer:
        tifo_rows.extend(local_tifo_rows(path, "iTransformer"))
    for path in args.tifo_dlinear:
        tifo_rows.extend(local_tifo_rows(path, "DLinear"))
    if args.tifo_selection:
        tifo_rows = apply_tifo_selection(tifo_rows, args.tifo_selection)
    rows.extend(tifo_rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"assembled {len(rows)} canonical evidence rows at {args.output}")


if __name__ == "__main__":
    main()
