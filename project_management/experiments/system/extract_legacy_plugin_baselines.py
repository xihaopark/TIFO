#!/usr/bin/env python3
"""Extract the complete submitted TIFO/TIFO*/RevIN/SAN/FAN result surface."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DATASETS = ("Electricity", "ETTh1", "ETTh2", "ETTm1", "ETTm2", "Traffic", "Weather")
HORIZONS = (96, 192, 336, 720)


def table_source(tex: str, label: str) -> str:
    label_pos = tex.index(f"\\label{{{label}}}")
    start = tex.rfind("\\begin{table", 0, label_pos)
    end = tex.index("\\end{table", label_pos)
    return tex[start:end]


def strip_comments(source: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in source.splitlines())


def parse_rows(source: str, expected_values: int) -> dict[tuple[str, int], list[float]]:
    source = strip_comments(source)
    parsed = {}
    for index, dataset in enumerate(DATASETS):
        marker = re.escape(f"\\multirow{{4}}{{*}}{{\\rotatebox{{90}}{{{dataset}}}}}")
        match = re.search(marker, source)
        if not match:
            raise ValueError(f"dataset block not found: {dataset}")
        next_positions = [
            found.start()
            for other in DATASETS[index + 1 :]
            if (found := re.search(
                re.escape(f"\\multirow{{4}}{{*}}{{\\rotatebox{{90}}{{{other}}}}}"),
                source[match.end() :],
            ))
        ]
        block_end = match.end() + min(next_positions) if next_positions else len(source)
        block = source[match.start() : block_end]
        for horizon in HORIZONS:
            row = re.search(rf"&\s*{horizon}\s*&(?P<body>.*?)\\\\", block, re.DOTALL)
            if not row:
                raise ValueError(f"row not found: {dataset}/H{horizon}")
            values = [float(value) for value in re.findall(r"0\.\d+", row.group("body"))]
            if len(values) != expected_values:
                raise ValueError(
                    f"{dataset}/H{horizon}: expected {expected_values} values, got {len(values)}"
                )
            parsed[(dataset, horizon)] = values
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex", type=Path, required=True)
    parser.add_argument("--output-stem", type=Path, required=True)
    args = parser.parse_args()

    tex = args.tex.read_text(encoding="utf-8")
    normal = parse_rows(
        table_source(tex, "app_table_detailed_results_other_methods"), 24
    )
    fan = parse_rows(table_source(tex, "app_table_detailed_results_FAN"), 16)

    records = []
    for dataset in DATASETS:
        for horizon in HORIZONS:
            normal_values = normal[(dataset, horizon)]
            fan_values = fan[(dataset, horizon)]
            for backbone, normal_offset, fan_offset in (
                ("DLinear", 0, 0),
                ("iTransformer", 16, 8),
            ):
                # Detailed table order: Ours*, Ours, SAN, RevIN.
                for method, offset in (
                    ("TIFO*", 0),
                    ("TIFO", 2),
                    ("SAN", 4),
                    ("RevIN", 6),
                ):
                    records.append(
                        {
                            "source": "submitted_manuscript_matched_run",
                            "backbone": backbone,
                            "method": method,
                            "dataset": dataset,
                            "pred_len": horizon,
                            "mse": normal_values[normal_offset + offset],
                            "mae": normal_values[normal_offset + offset + 1],
                        }
                    )
                # FAN table order: Ours*, Ours, FAN, RevIN.
                records.append(
                    {
                        "source": "submitted_manuscript_matched_run",
                        "backbone": backbone,
                        "method": "FAN",
                        "dataset": dataset,
                        "pred_len": horizon,
                        "mse": fan_values[fan_offset + 4],
                        "mae": fan_values[fan_offset + 5],
                    }
                )

    expected = 2 * 5 * len(DATASETS) * len(HORIZONS)
    if len(records) != expected:
        raise ValueError(f"expected {expected} records, got {len(records)}")

    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    args.output_stem.with_suffix(".json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    with args.output_stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f"wrote {len(records)} frozen legacy baseline records")


if __name__ == "__main__":
    main()
