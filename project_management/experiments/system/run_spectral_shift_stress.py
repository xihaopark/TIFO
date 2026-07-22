#!/usr/bin/env python3
"""Evaluate frozen Ori/TIFO checkpoints under a preregistered spectral shift."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_SPECS = {
    "ETTh1": {
        "ori": "coverage_h96_etth1_itransformer_ori_s{seed}",
        "tifo": "final_etth1_h96_tifo_hermitian_s{seed}",
    },
    "Traffic": {
        "ori": "coverage_h96_traffic_itransformer_ori_s{seed}",
        "tifo": "final_traffic_h96_tifo_zpad150_s{seed}",
    },
}


def evaluation_command(launch: dict, strength: float) -> list[str]:
    command = list(launch["command"])
    training_index = command.index("--is_training") + 1
    command[training_index] = "0"
    strength_tag = str(strength).replace(".", "p")
    command.extend(
        (
            "--spectral_shift_strength",
            str(strength),
            "--evaluation_tag",
            f"spectral_high_s{strength_tag}",
        )
    )
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--datasets", nargs="+", choices=sorted(RUN_SPECS), default=sorted(RUN_SPECS))
    parser.add_argument("--methods", nargs="+", choices=("ori", "tifo"), default=("ori", "tifo"))
    parser.add_argument("--seeds", nargs="+", type=int, default=(2021, 2022, 2023))
    parser.add_argument("--strengths", nargs="+", type=float, default=(0.0, 0.25, 0.5, 1.0))
    args = parser.parse_args()

    for dataset in args.datasets:
        for method in args.methods:
            for seed in args.seeds:
                run_id = RUN_SPECS[dataset][method].format(seed=seed)
                launch_path = ROOT / "experiment_records" / run_id / "launch.json"
                launch = json.loads(launch_path.read_text(encoding="utf-8"))
                for strength in args.strengths:
                    command = evaluation_command(launch, strength)
                    env = dict(os.environ)
                    env["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
                    print(f"[{dataset} {method} seed={seed} strength={strength}]", flush=True)
                    subprocess.run(command, cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
