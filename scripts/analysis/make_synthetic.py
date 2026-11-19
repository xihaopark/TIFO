#!/usr/bin/env python3
"""X5: synthetic series with known stationary / non-stationary frequency bins.

Window length L = 96. Stationary components: fixed sinusoids with periods
32, 24, 12 (rFFT bins 3, 4, 8). Non-stationary components live in bins 10-16:
a chirp whose period drifts slowly between 6 and 9.6 steps and an amplitude-
switching sinusoid (period 7.38, bin 13) with random on/off regimes. The
strength s scales the non-stationary part. Labels are written to a JSON file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def series(strength: float, n: int, channels: int, seed: int):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    data = []
    for c in range(channels):
        x = np.zeros(n)
        for period, amp in ((32, 1.0), (24, 0.8), (12, 0.6)):
            x += amp * (1 + 0.2 * c / channels) * np.sin(2 * np.pi * t / period + rng.uniform(0, 2 * np.pi))
        # chirp: instantaneous period drifts between 6.0 and 9.6 (bins 10-16) over ~3000-step cycles
        period = 7.8 + 1.8 * np.sin(2 * np.pi * t / (3000 + 400 * c))
        phase = 2 * np.pi * np.cumsum(1.0 / period)
        x += strength * 0.8 * np.sin(phase)
        # amplitude-switching sinusoid at bin 13 (period 96/13)
        regimes = np.repeat(rng.integers(0, 2, n // 500 + 1), 500)[:n]
        x += strength * 1.2 * regimes * np.sin(2 * np.pi * 13 * t / 96 + rng.uniform(0, 2 * np.pi))
        x += 0.1 * rng.standard_normal(n)
        data.append(x)
    return np.stack(data, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=20000)
    parser.add_argument("--channels", type=int, default=7)
    args = parser.parse_args()
    out = ROOT / "dataset" / "dataset_synthetic"
    out.mkdir(exist_ok=True)
    for strength in (0.5, 1.0, 2.0):
        values = series(strength, args.n, args.channels, seed=7)
        frame = pd.DataFrame(values, columns=[f"c{i}" for i in range(args.channels - 1)] + ["OT"])
        frame.insert(0, "date", pd.date_range("2020-01-01", periods=args.n, freq="h"))
        frame.to_csv(out / f"synthetic_s{str(strength).replace('.', 'p')}.csv", index=False)
    labels = {"window": 96, "stationary_bins": [3, 4, 8], "nonstationary_bins": list(range(10, 17)),
              "strengths": [0.5, 1.0, 2.0], "n": args.n, "channels": args.channels}
    (out / "labels.json").write_text(json.dumps(labels, indent=1) + "\n")
    print("written", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
