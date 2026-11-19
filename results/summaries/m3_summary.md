# M3: additional backbones, Ori vs +TIFO (TIFO submitted default, no tuning)

| backbone | pairs | Ori MSE | TIFO MSE | rel. Δ % (neg = TIFO better) | TIFO better | Wilcoxon p | Ori MAE | TIFO MAE |
|---|---|---|---|---|---|---|---|---|
| filternet (tifo) | 84 | 0.3401 | 0.3540 | +3.61 | 41/84 | 1.4e-01 | 0.3454 | 0.3531 |
| filternet (tifo_tuned) | 84 | 0.3401 | 0.3415 | +0.20 | 53/84 | 1.2e-01 | 0.3454 | 0.3461 |
| tqnet (tifo) | 84 | 0.3324 | 0.3351 | +0.65 | 39/84 | 6.7e-02 | 0.3367 | 0.3394 |
| tqnet (tifo_tuned) | 84 | 0.3324 | 0.3353 | +0.61 | 37/84 | 2.3e-02 | 0.3367 | 0.3396 |

Per dataset (mean rel. Δ % over horizons and seeds):

- filternet/tifo/electricity: +0.40% (n=12, TIFO better 9)
- filternet/tifo/etth1: +2.73% (n=12, TIFO better 3)
- filternet/tifo/etth2: +0.70% (n=12, TIFO better 6)
- filternet/tifo/ettm1: +21.82% (n=12, TIFO better 3)
- filternet/tifo/ettm2: +0.13% (n=12, TIFO better 7)
- filternet/tifo/traffic: -0.75% (n=12, TIFO better 10)
- filternet/tifo/weather: +0.23% (n=12, TIFO better 3)
- filternet/tifo_tuned/electricity: +0.20% (n=12, TIFO better 8)
- filternet/tifo_tuned/etth1: +2.73% (n=12, TIFO better 3)
- filternet/tifo_tuned/etth2: +0.70% (n=12, TIFO better 6)
- filternet/tifo_tuned/ettm1: -0.50% (n=12, TIFO better 9)
- filternet/tifo_tuned/ettm2: -0.74% (n=12, TIFO better 11)
- filternet/tifo_tuned/traffic: -0.75% (n=12, TIFO better 10)
- filternet/tifo_tuned/weather: -0.21% (n=12, TIFO better 6)
- tqnet/tifo/electricity: +0.56% (n=12, TIFO better 7)
- tqnet/tifo/etth1: +1.93% (n=12, TIFO better 1)
- tqnet/tifo/etth2: +1.07% (n=12, TIFO better 4)
- tqnet/tifo/ettm1: -0.43% (n=12, TIFO better 8)
- tqnet/tifo/ettm2: -0.03% (n=12, TIFO better 7)
- tqnet/tifo/traffic: +1.49% (n=12, TIFO better 5)
- tqnet/tifo/weather: -0.04% (n=12, TIFO better 7)
- tqnet/tifo_tuned/electricity: -0.88% (n=12, TIFO better 11)
- tqnet/tifo_tuned/etth1: +1.93% (n=12, TIFO better 1)
- tqnet/tifo_tuned/etth2: +1.07% (n=12, TIFO better 4)
- tqnet/tifo_tuned/ettm1: +0.72% (n=12, TIFO better 2)
- tqnet/tifo_tuned/ettm2: -0.03% (n=12, TIFO better 7)
- tqnet/tifo_tuned/traffic: +1.49% (n=12, TIFO better 5)
- tqnet/tifo_tuned/weather: -0.04% (n=12, TIFO better 7)
