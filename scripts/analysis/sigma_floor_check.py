"""sigma floor check: per (k,c) std of FFT amplitudes over training windows (dataset z-score), vs eps."""
import sys, json, numpy as np, torch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_utils import ROOT, run_args, loaders
# Uses the launch records of the M2 Ori runs (configs/shared_config/m2_protocol.json) to rebuild the data pipeline.
out = {}
for ds in ['etth1','etth2','ettm1','ettm2','electricity','traffic','weather']:
    for sl in (96, 336):
        args = run_args(f'm2_dlinear_{ds}_h96_ori_s2021'); args.seq_len = sl; args.batch_size = 256
        _, ld = loaders(args, 'train')
        s1 = s2 = None; n = 0
        with torch.no_grad():
            for b in ld:
                a = torch.fft.fft(b[0].float(), dim=1).abs().double()
                s1 = a.sum(0) if s1 is None else s1 + a.sum(0); s2 = (a**2).sum(0) if s2 is None else s2 + (a**2).sum(0); n += a.size(0)
        mu = s1/n; sd = (s2/n - mu**2).clamp_min(0).sqrt()
        S = mu/(torch.sqrt(sd**2+1e-5)+1e-5)
        nondc = sd[1:]
        r = dict(min_sd=float(sd.min()), min_sd_nondc=float(nondc.min()), p01_sd=float(torch.quantile(sd.flatten().float(),0.01)),
                 frac_sd_below_0p01=float((sd<0.01).float().mean()), min_mu=float(mu.min()),
                 spearman_logS_logmu_within_channel=float(np.mean([__import__('scipy.stats',fromlist=['x']).spearmanr(S[1:,c],mu[1:,c]).statistic for c in range(S.shape[1])])))
        out[f'{ds}_sl{sl}'] = r; print(ds, sl, json.dumps(r), flush=True)
json.dump(out, open(ROOT / 'results/analysis/sigma_floor.json','w'), indent=1)
