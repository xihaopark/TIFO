#!/usr/bin/env python3
"""Build the paired three-seed TIFO stationarity-score ablation."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "final_tifo_hermitian_h96.json"
OUTPUT = HERE / "tifo_score_ablation_h96.json"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for base in source["runs"]:
        for mode in ("data", "permuted", "ones"):
            runs.append({
                **{key: value for key, value in base.items() if key not in {"run_id", "model_args"}},
                "run_id": f"score_ablation_{base['dataset'].lower()}_h96_{mode}_s{base['seed']}",
                "model_args": {
                    **base["model_args"],
                    "tifo_score_mode": mode,
                    "tifo_score_seed": 1729,
                },
            })
    OUTPUT.write_text(json.dumps({
        "protocol_id": "kdd_resubmit_tifo_score_ablation_h96_v1",
        "selection_rule": (
            "No model selection: rerun the frozen ETTh1/ETTm2 configurations with the data score, "
            "a fixed frequency-permuted score preserving per-channel marginals, and an all-ones score."
        ),
        "defaults": source["defaults"],
        "runs": runs,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(runs)} score-ablation runs to {OUTPUT}")


if __name__ == "__main__":
    main()
