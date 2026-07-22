#!/usr/bin/env python3
"""Build normalized bare-iTransformer controls for the WDAN engine."""

from __future__ import annotations

import json
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent
SOURCE = SOURCE_DIR / "coverage_h96_itransformer.json"
ETTM2_SOURCE = SOURCE_DIR / "gate_ettm2_96.json"
OUTPUT = SOURCE_DIR / "wdan_engine_controls_h96_itransformer.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    ettm2_source = json.loads(ETTM2_SOURCE.read_text(encoding="utf-8"))
    source_runs = source["runs"] + [
        {**ettm2_source["defaults"], **run}
        for run in ettm2_source["runs"]
        if run.get("engine") == "native" and run.get("method") == "ori"
    ]

    runs = []
    for native in source_runs:
        if native["method"] != "ori":
            continue
        shared = {
            key: value
            for key, value in native.items()
            if key not in {"run_id", "engine", "backbone", "method", "model_args"}
        }
        dataset_id = native["dataset"].lower()
        seed = native["seed"]
        runs.append(
            {
                **shared,
                "run_id": f"wdan_control_norm_h96_{dataset_id}_itransformer_s{seed}",
                "engine": "wdan",
                "model_args": {
                    **native["model_args"],
                    "model": "iTransformer",
                    "use_norm": 1,
                },
            }
        )

    matrix = {
        "protocol_id": "kdd_resubmit_wdan_engine_controls_h96_v2",
        "defaults": dict(source["defaults"]),
        "runs": runs,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
