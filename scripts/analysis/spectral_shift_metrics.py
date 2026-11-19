#!/usr/bin/env python3
"""X8: explicit train/test spectral-distance protocol for TIFO.

Windows: the model's input windows (length L) from the train and test splits,
after the same per-window normalization the backbone applies before TIFO.
Spectrum: FFT on the filter's grid; "after" amplitudes are recomputed from the
weighted complex coefficients |w_r Re + i w_i Im|.
Per (frequency, channel) distances between train and test amplitude samples:
  jsd_adapt  - squared JS distance (base 2), 50 equal-width bins over the pooled
               range of each condition (the paper's per-frequency algorithm)
  ks         - two-sample Kolmogorov-Smirnov statistic (max ECDF gap)
  w1_norm    - Wasserstein-1 divided by the pooled standard deviation
(v3: the fixed-bin JSD variant was dropped; KS added.)
Aggregation: unweighted mean over (k, c); also |w|-weighted for the TIFO case.
Controls: learned weights, the same weights randomly permuted over (k, c), ones.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.stats import ks_2samp, wasserstein_distance

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_utils import ROOT, loaders, trained_filter  # noqa: E402


def windows(args, flag, limit):
    dataset, _ = loaders(args, flag)
    idx = np.linspace(0, len(dataset) - 1, min(limit, len(dataset))).astype(int)
    x = torch.tensor(np.stack([dataset[i][0] for i in idx]), dtype=torch.float32)
    x = x - x.mean(1, keepdim=True)
    return x / torch.sqrt(x.var(1, keepdim=True, unbiased=False) + 1e-5)


def spectrum(filt, x):
    if filt.variant in {"historical", "free_historical"}:
        return torch.fft.fft(x, n=filt.fft_size, dim=1)
    return torch.fft.rfft(x, n=filt.fft_size, dim=1)


def jsd(p, q):
    p = p / p.sum(); q = q / q.sum(); m = 0.5 * (p + q)
    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def distances(a_tr, a_te):
    out = {"jsd_adapt": [], "ks": [], "w1_norm": []}
    K, C = a_tr.shape[1:]
    for k in range(K):
        for c in range(C):
            u, v = a_tr[:, k, c], a_te[:, k, c]
            pooled = np.concatenate([u, v])
            ea = np.linspace(pooled.min(), pooled.max() + 1e-12, 51)
            out["jsd_adapt"].append(jsd(np.histogram(u, ea)[0] + 1e-12, np.histogram(v, ea)[0] + 1e-12))
            out["ks"].append(ks_2samp(u, v).statistic)
            out["w1_norm"].append(wasserstein_distance(u, v) / (pooled.std() + 1e-12))
    return {k: np.array(v).reshape(K, C) for k, v in out.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_ids", nargs="+")
    parser.add_argument("--limit", type=int, default=3000)
    parser.add_argument("--output", type=Path, default=ROOT / "results/analysis/x8_spectral_shift.json")
    args_cli = parser.parse_args()
    results = {}
    for run_id in args_cli.run_ids:
        args, filt, _ = trained_filter(run_id)
        x_tr, x_te = windows(args, "train", args_cli.limit), windows(args, "test", args_cli.limit)
        s_tr, s_te = spectrum(filt, x_tr), spectrum(filt, x_te)
        with torch.no_grad():
            wr, wi = filt.frequency_weights()
        gen = torch.Generator().manual_seed(0)
        perm = torch.randperm(wr.numel(), generator=gen)
        conditions = {"before": (torch.ones_like(wr), torch.ones_like(wi)),
                      "tifo": (wr, wi),
                      "random_perm": (wr.flatten()[perm].view_as(wr), wi.flatten()[perm].view_as(wi))}
        entry = {}
        for name, (r, i) in conditions.items():
            a_tr = torch.complex(s_tr.real * r, s_tr.imag * i).abs().numpy()
            a_te = torch.complex(s_te.real * r, s_te.imag * i).abs().numpy()
            d = distances(a_tr, a_te)
            entry[name] = {k: float(v.mean()) for k, v in d.items()}
            if name == "tifo":
                w = (r.abs() + i.abs()).numpy() / 2
                entry["tifo_weighted"] = {k: float((v * w).sum() / w.sum()) for k, v in d.items()}
        results[run_id] = entry
        print(run_id, json.dumps(entry))
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    args_cli.output.write_text(json.dumps(results, indent=1) + "\n")


if __name__ == "__main__":
    main()
