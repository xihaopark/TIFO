#!/usr/bin/env python3
"""Materialize ACN/WDAN source-paper iTransformer results with provenance."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parent / "results" / "reported_recent_plugin_baselines"
HORIZONS = (96, 192, 336, 720)

SOURCES = {
    "ACN": {
        "url": "https://arxiv.org/pdf/2506.00432",
        "table": "Table M.1",
        "protocol_note": "iTransformer, input length 96, source-paper reported values",
        "values": {
            "ETTh1": ((.381, .400), (.431, .429), (.471, .450), (.470, .469)),
            "ETTh2": ((.299, .350), (.375, .396), (.409, .427), (.413, .436)),
            "ETTm1": ((.328, .364), (.370, .387), (.407, .411), (.474, .446)),
            "ETTm2": ((.181, .262), (.247, .307), (.315, .349), (.410, .404)),
            "Electricity": ((.132, .228), (.150, .244), (.164, .260), (.187, .280)),
            "Weather": ((.160, .204), (.210, .250), (.266, .290), (.345, .341)),
        },
    },
    "WDAN": {
        "url": "https://arxiv.org/pdf/2506.05857",
        "table": "Table 5",
        "protocol_note": "iTransformer, input length 720, source-paper reported values",
        "values": {
            "ETTh1": ((.368, .397), (.406, .421), (.428, .444), (.452, .470)),
            "ETTh2": ((.269, .334), (.331, .376), (.358, .403), (.377, .429)),
            "ETTm1": ((.291, .350), (.330, .375), (.362, .396), (.412, .422)),
            "ETTm2": ((.162, .253), (.217, .292), (.273, .331), (.353, .382)),
            "Electricity": ((.128, .225), (.146, .242), (.156, .256), (.182, .281)),
            "Weather": ((.147, .199), (.196, .248), (.242, .282), (.312, .337)),
        },
    },
}


def main() -> None:
    records = []
    for method, source in SOURCES.items():
        for dataset, values in source["values"].items():
            if len(values) != len(HORIZONS):
                raise ValueError(f"{method}/{dataset}: incomplete horizon values")
            for horizon, (mse, mae) in zip(HORIZONS, values):
                records.append(
                    {
                        "source": "source_paper_reported",
                        "source_url": source["url"],
                        "source_table": source["table"],
                        "protocol_note": source["protocol_note"],
                        "backbone": "iTransformer",
                        "method": method,
                        "dataset": dataset,
                        "pred_len": horizon,
                        "mse": mse,
                        "mae": mae,
                    }
                )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.with_suffix(".json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    with OUTPUT.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f"wrote {len(records)} source-paper baseline records")


if __name__ == "__main__":
    main()
