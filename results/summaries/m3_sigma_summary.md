# M3c: SiGMA (ICML 2026) Ori vs +TIFO

| variant | pairs | Ori MSE | TIFO MSE | rel. Δ % (neg = TIFO better) | TIFO better | two-sided Wilcoxon p |
|---|---|---|---|---|---|---|
| TIFO default | 84 | 0.3383 | 0.3495 | +2.82 | 31/84 | 0.00077 |
| TIFO, lr multiplier selected on validation | 84 | 0.3383 | 0.3387 | +0.02 | 45/84 | 0.59 |

Selected lr multipliers: {'etth1': 0.1, 'etth2': 0.1, 'ettm1': 0.1, 'ettm2': 0.01, 'electricity': 0.1, 'traffic': 1.0, 'weather': 0.1}

Per dataset (selected variant; mean rel. Δ %, TIFO better / n):

- etth1: +0.43% (5/12)
- etth2: +1.08% (4/12)
- ettm1: -0.14% (7/12)
- ettm2: -1.10% (11/12)
- electricity: +0.23% (4/12)
- traffic: -0.50% (10/12)
- weather: +0.13% (4/12)
