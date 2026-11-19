# X6 full: 7 datasets × 4 horizons × 3 seeds (local TIFO finals vs M2 Ori), evaluation only

| backbone | strength | pairs | rel. Δ % (neg = TIFO better) | TIFO better | Wilcoxon p |
|---|---|---|---|---|---|
| itransformer | 0 | 84 | -1.30 | 61/84 | 7.6e-07 |
| itransformer | 0.25 | 84 | -1.26 | 62/84 | 1.2e-07 |
| itransformer | 0.5 | 84 | -1.19 | 64/84 | 1.1e-08 |
| itransformer | 1 | 84 | -0.93 | 69/84 | 1.7e-09 |
| dlinear | 0 | 84 | -2.44 | 68/84 | 5.7e-12 |
| dlinear | 0.25 | 84 | -2.55 | 69/84 | 3.4e-12 |
| dlinear | 0.5 | 84 | -2.66 | 69/84 | 2.3e-12 |
| dlinear | 1 | 84 | -2.90 | 71/84 | 1.4e-12 |

Per dataset, strength 0 → 1 (mean rel. Δ %):

- itransformer/electricity: -3.73% → +0.82%
- itransformer/etth1: -0.44% → -1.20%
- itransformer/etth2: -0.39% → -0.85%
- itransformer/ettm1: -0.51% → -0.85%
- itransformer/ettm2: -0.69% → -0.96%
- itransformer/traffic: +0.36% → +0.11%
- itransformer/weather: -3.70% → -3.54%
- dlinear/electricity: -7.45% → -10.76%
- dlinear/etth1: -0.54% → -0.96%
- dlinear/etth2: -0.53% → -0.57%
- dlinear/ettm1: -2.20% → -2.04%
- dlinear/ettm2: +0.41% → +0.50%
- dlinear/traffic: -0.44% → -0.37%
- dlinear/weather: -6.33% → -6.08%
