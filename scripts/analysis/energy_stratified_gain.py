#!/usr/bin/env python3
"""X4(b): energy-stratified relation between the score S and the learned gain.

Learned gain per (k, c): g = sqrt((w_r^2 + w_i^2) / 2).
Energy per (k, c): mean training amplitude mu (the numerator of S).
For each run: Spearman rho(S, g) overall and within mean-amplitude quintiles
(computed per channel), which separates stability from energy.
Permuted-score runs provide the null distribution. All quantities are ranked
within channel before pooling, so between-channel level differences cannot
create spurious correlation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_utils import ROOT, loaders, trained_filter  # noqa: E402


def mean_amplitude(args, filt):
    _, loader = loaders(args, "train")
    total, count = None, 0
    with torch.no_grad():
        for batch in loader:
            x = batch[0].float()
            if filt.variant not in {"historical", "free_historical"}:
                x = (x - x.mean(1, keepdim=True)) / torch.sqrt(x.var(1, keepdim=True, unbiased=False) + 1e-5)
                a = torch.fft.rfft(x, n=filt.fft_size, dim=1).abs()
            else:
                a = torch.fft.fft(x, n=filt.fft_size, dim=1).abs()
            total = a.sum(0) if total is None else total + a.sum(0)
            count += x.size(0)
    return (total / count).numpy()


def analyse(run_id):
    args, filt, score = trained_filter(run_id)
    with torch.no_grad():
        wr, wi = filt.frequency_weights()
    gain = torch.sqrt((wr ** 2 + wi ** 2) / 2).numpy()
    s = filt.stationarity_score.numpy()  # the score the filter actually saw (permuted if so)
    mu = mean_amplitude(args, filt)
    # The true (unpermuted) data score, for runs trained with a control score.
    from utils.frequency_domain_filter import GlobalMaskCalculator
    true_args = type(args)(**{**vars(args), "tifo_score_mode": "data"})
    s_true = GlobalMaskCalculator(true_args, "cpu").compute_global_statistics(loaders(args, "train")[1]).numpy()
    K, C = s.shape
    if filt.variant in {"historical", "free_historical"}:
        keep = slice(1, K // 2 + 1)  # non-redundant, non-DC half of the full FFT
        s, gain, mu, s_true = s[keep], gain[keep], mu[keep], s_true[keep]
    # Remove between-channel level differences (the permuted control keeps each
    # channel's score marginal): rank every quantity within its channel first.
    def within_channel_rank(a):
        return np.argsort(np.argsort(a, axis=0), axis=0) / max(a.shape[0] - 1, 1)
    s, gain, mu, s_true = (within_channel_rank(x) for x in (s, gain, mu, s_true))
    overall = spearmanr(s.flatten(), gain.flatten()).statistic
    strata_true = []
    for q in range(5):
        xs, ys = [], []
        for c in range(s.shape[1]):
            lo, hi = np.quantile(mu[:, c], [q / 5, (q + 1) / 5])
            m = (mu[:, c] >= lo) & (mu[:, c] <= hi)
            xs.append(s_true[m, c]); ys.append(gain[m, c])
        strata_true.append(float(spearmanr(np.concatenate(xs), np.concatenate(ys)).statistic))
    strata = []
    for q in range(5):
        xs, ys = [], []
        for c in range(s.shape[1]):
            lo, hi = np.quantile(mu[:, c], [q / 5, (q + 1) / 5])
            m = (mu[:, c] >= lo) & (mu[:, c] <= hi)
            xs.append(s[m, c]); ys.append(gain[m, c])
        strata.append(float(spearmanr(np.concatenate(xs), np.concatenate(ys)).statistic))
    return {"rho_overall": float(overall), "rho_by_energy_quintile": strata,
            "rho_true_overall": float(spearmanr(s_true.flatten(), gain.flatten()).statistic),
            "rho_true_by_energy_quintile": strata_true,
            "rho_energy_gain": float(spearmanr(mu.flatten(), gain.flatten()).statistic)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_ids", nargs="+")
    parser.add_argument("--output", type=Path, default=ROOT / "results/analysis/x4_energy_strata.json")
    args = parser.parse_args()
    out = {}
    for run_id in args.run_ids:
        out[run_id] = analyse(run_id)
        print(run_id, json.dumps(out[run_id]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
