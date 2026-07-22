#!/usr/bin/env python3
"""Build same-engine iTransformer controls for the ACN and WDAN matrix.

The paper-facing comparison currently uses a native iTransformer control while
the plug-ins run in their official repositories.  These controls isolate the
effect of each plug-in from differences in data loaders, optimization code and
checkpoint selection across frameworks.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "plugin_baselines_h96_itransformer.json"
OUTPUT = HERE / "plugin_engine_controls_h96_itransformer.json"

ARCHITECTURE_KEYS = {"d_model", "d_ff", "e_layers", "n_heads", "factor"}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    controls = []
    for run in source["runs"]:
        engine = run["engine"]
        dataset_token = run["dataset"].lower()
        model_args = {
            key: value
            for key, value in run["model_args"].items()
            if key in ARCHITECTURE_KEYS
        }
        model_args["model"] = "iTransformer"
        controls.append(
            {
                **{key: value for key, value in run.items() if key not in {"run_id", "model_args"}},
                "run_id": (
                    f"plugin_control_h96_{dataset_token}_{engine}_itransformer_"
                    f"s{run['seed']}"
                ),
                "model_args": model_args,
            }
        )

    matrix = {
        "protocol_id": "kdd_resubmit_plugin_engine_controls_h96_v1",
        "defaults": source["defaults"],
        "runs": controls,
    }
    OUTPUT.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(controls)} runs to {OUTPUT}")


if __name__ == "__main__":
    main()
