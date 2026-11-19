#!/usr/bin/env python3
"""X6: evaluate trained checkpoints under the controlled high-frequency shift.

Re-runs each training command with --is_training 0 and the repository's
evaluation-only --spectral_shift_strength (upper half of non-DC rFFT bins
scaled coherently over input and future windows). No retraining.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRIC = re.compile(r"mse:([-+0-9.eE]+),\s*mae:([-+0-9.eE]+)")


def command_for(launch, strength):
    cmd = list(launch["command"])
    cmd[cmd.index("--is_training") + 1] = "0"
    tag = "sh" + str(strength).replace(".", "p")  # short: long settings hit the 255-char path limit
    return cmd + ["--spectral_shift_strength", str(strength), "--evaluation_tag", tag], tag


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default=None, help="glob over experiment_records run ids")
    parser.add_argument("--records", type=Path, default=ROOT / "experiment_records",
                        help="experiment_records directory (another checkout is allowed)")
    parser.add_argument("--run-ids-file", type=Path, default=None, help="newline-separated run ids")
    parser.add_argument("--strengths", nargs="+", type=float, default=(0.0, 0.25, 0.5, 1.0))
    parser.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    parser.add_argument("--jobs-per-gpu", type=int, default=2)
    parser.add_argument("--output", type=Path, default=ROOT / "results/analysis/x6_shift.json")
    args = parser.parse_args()
    results = json.loads(args.output.read_text()) if args.output.exists() else {}
    jobs = queue.Queue()
    if args.run_ids_file:
        launch_paths = [args.records / rid / "launch.json" for rid in args.run_ids_file.read_text().split()]
    else:
        launch_paths = sorted(args.records.glob(f"{args.pattern}/launch.json"))
    for launch_path in launch_paths:
        if not launch_path.exists():
            continue
        launch = json.loads(launch_path.read_text())
        if launch.get("status") != "completed":
            continue
        for s in args.strengths:
            key = f"{launch['run_id']}|{s}"
            if key not in results:
                jobs.put((key, launch, s))
    lock = threading.Lock()
    print(f"{jobs.qsize()} evaluations", flush=True)

    def worker(gpu):
        while True:
            try:
                key, launch, s = jobs.get_nowait()
            except queue.Empty:
                return
            cmd, tag = command_for(launch, s)
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
            log = Path(launch["log_file"]).with_name(f"eval_{tag}.log")
            with log.open("w") as handle:
                rc = subprocess.run(cmd, cwd=launch["cwd"], env=env, stdout=handle, stderr=subprocess.STDOUT).returncode
            found = METRIC.findall(log.read_text(errors="replace"))
            with lock:
                if rc == 0 and found:
                    results[key] = {"mse": float(found[-1][0]), "mae": float(found[-1][1])}
                    args.output.write_text(json.dumps(results, indent=1) + "\n")
                print(f"{key} rc={rc} {results.get(key)}", flush=True)

    threads = [threading.Thread(target=worker, args=(int(g),)) for _ in range(args.jobs_per_gpu)
               for g in args.gpus.split(",")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
