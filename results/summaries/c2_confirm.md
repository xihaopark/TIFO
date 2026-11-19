# C2 (pre-registered): submitted TIFO vs free filter (lr x100)

Δ = MSE(free) − MSE(TIFO); positive favours TIFO.

| backbone | pairs | mean Δ | mean rel % | TIFO better | two-sided Wilcoxon p |
|---|---|---|---|---|---|
| itransformer | 40 | -0.00309 | -0.76 | 15/40 | 1.83e-01 |
| dlinear | 40 | -0.00377 | -1.84 | 11/40 | 1.11e-03 |

Per cell (mean rel %, positive favours TIFO):

- dlinear/electricity/336: -2.52% (0/4)
- dlinear/electricity/96: -3.48% (0/4)
- dlinear/etth1/336: +0.71% (4/4)
- dlinear/etth1/96: +1.56% (4/4)
- dlinear/ettm2/336: +0.10% (3/4)
- dlinear/ettm2/96: -1.43% (0/4)
- dlinear/traffic/336: -0.31% (0/4)
- dlinear/traffic/96: -0.53% (0/4)
- dlinear/weather/336: -4.33% (0/4)
- dlinear/weather/96: -8.20% (0/4)
- itransformer/electricity/336: +0.39% (2/4)
- itransformer/electricity/96: -1.32% (0/4)
- itransformer/etth1/336: -0.71% (1/4)
- itransformer/etth1/96: -1.11% (0/4)
- itransformer/ettm2/336: +1.61% (4/4)
- itransformer/ettm2/96: +1.74% (4/4)
- itransformer/traffic/336: +4.54% (4/4)
- itransformer/traffic/96: -8.04% (0/4)
- itransformer/weather/336: -1.88% (0/4)
- itransformer/weather/96: -2.84% (0/4)
