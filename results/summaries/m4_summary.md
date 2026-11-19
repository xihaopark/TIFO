# M4: TIFO with validation-selected settings on recent backbones vs official backbone alone

| backbone | pairs | Ori MSE | TIFO MSE | rel. Δ % (neg = TIFO better) | TIFO better | Wilcoxon p |
|---|---|---|---|---|---|---|
| sigma | 84 | 0.3383 | 0.3367 | -0.49 | 58/84 | 4.8e-05 |
| tqnet | 84 | 0.3324 | 0.3330 | +0.16 | 50/84 | 0.11 |
| filternet | 84 | 0.3401 | 0.3386 | -0.44 | 57/84 | 0.0019 |

Per dataset (rel. Δ %, TIFO better / n):

- sigma/etth1: -0.35% (11/12)
- sigma/etth2: -0.41% (9/12)
- sigma/ettm1: +0.06% (5/12)
- sigma/ettm2: -1.25% (10/12)
- sigma/electricity: +0.34% (6/12)
- sigma/traffic: -0.82% (11/12)
- sigma/weather: -0.80% (6/12)
- tqnet/etth1: -0.05% (8/12)
- tqnet/etth2: -0.02% (8/12)
- tqnet/ettm1: +0.24% (3/12)
- tqnet/ettm2: -0.30% (8/12)
- tqnet/electricity: -0.68% (10/12)
- tqnet/traffic: +1.24% (6/12)
- tqnet/weather: -0.21% (7/12)
- filternet/etth1: -0.41% (6/12)
- filternet/etth2: -0.71% (8/12)
- filternet/ettm1: +0.01% (6/12)
- filternet/ettm2: -0.92% (11/12)
- filternet/electricity: +0.96% (6/12)
- filternet/traffic: -0.96% (11/12)
- filternet/weather: -0.31% (9/12)
