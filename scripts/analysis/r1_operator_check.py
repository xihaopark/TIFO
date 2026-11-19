"""Exact linear map of each trained TIFO filter of the main table: sign of weights, invertibility, PSD.

Needs the launch records and checkpoints of configs/main/tifo_final.json.
"""
import sys, json, glob, numpy as np, torch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_utils import ROOT, run_args, loaders
from utils.frequency_domain_filter import GlobalMaskCalculator, build_frequency_domain_filter
final = json.load(open(ROOT / 'configs/main/tifo_final.json'))
cells = sorted({(r['backbone'], r['dataset'], r['pred_len'], r['run_id'].rsplit('_s', 1)[0] + '_s2021') for r in final['runs']})
out = []
torch.set_num_threads(8)
log = open(ROOT / 'results/analysis/r1_operator_check.jsonl', 'a')
done = set()
for bb, ds, pl, t in cells:
    for seed in (2021, 2022, 2023):
        rid = t.replace('_s2021', f'_s{seed}')
        args = run_args(rid); args.batch_size = 256
        score = GlobalMaskCalculator(args, 'cpu').compute_global_statistics(loaders(args, 'train')[1])
        f = build_frequency_domain_filter(args, score)
        ck = glob.glob(f'{ROOT}/checkpoints/*_{rid}_*/checkpoint.pth'); assert len(ck) == 1, rid
        st = torch.load(ck[0], map_location='cpu')
        f.load_state_dict({k[7:]: v for k, v in st.items() if k.startswith('filter.')}); f.eval()
        with torch.no_grad():
            wr, wi = f.frequency_weights()
            L, C = args.seq_len, args.enc_in
            eye = torch.eye(L).unsqueeze(-1).expand(L, L, C).contiguous()
            T = f(eye).permute(2, 1, 0).double().numpy()  # [C, L_out, L_in]
        a = f.residual_alpha
        weff_r, weff_i = (1 - a) + a * wr.double().numpy(), (1 - a) + a * wi.double().numpy()
        sv = np.linalg.svd(T, compute_uv=False)
        cond = sv[:, 0] / sv[:, -1]
        sym = np.abs(T - T.transpose(0, 2, 1)).max() / np.abs(T).max()
        eig_min = np.linalg.eigvalsh((T + T.transpose(0, 2, 1)) / 2).min(axis=1) / sv[:, 0]
        r = dict(backbone=bb, dataset=ds, horizon=pl, seed=seed, variant=args.tifo_variant,
                 frac_neg=float(((weff_r < 0).mean() + (weff_i < 0).mean()) / 2),
                 frac_small=float(((np.abs(weff_r) < 0.05).mean() + (np.abs(weff_i) < 0.05).mean()) / 2),
                 median_cond=float(np.median(cond)), max_cond=float(cond.max()),
                 min_sv_rel=float((sv[:, -1] / sv[:, 0]).min()),
                 asym=float(sym), min_eig_sym_rel=float(eig_min.min()))
        out.append(r); print(json.dumps(r), flush=True); log.write(json.dumps(r) + '\n'); log.flush()
json.dump(out, open(ROOT / 'results/analysis/r1_operator_check.json', 'w'), indent=1)
