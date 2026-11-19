# X9: dataset + sample-conditioned TIFO vs submitted (same cells/seeds as C2)

Δ rel = (adaptive − submitted)/submitted; negative = adaptive better.

| backbone | pairs | rel. Δ % | adaptive better | Wilcoxon p |
|---|---|---|---|---|
| itransformer | 40 | -0.13 | 27/40 | 1.2e-01 |
| dlinear | 40 | -1.70 | 29/40 | 3.2e-04 |

Per dataset:

- itransformer/electricity: +0.08% (4/8)
- itransformer/etth1: -0.05% (6/8)
- itransformer/ettm2: -0.03% (6/8)
- itransformer/traffic: -0.56% (6/8)
- itransformer/weather: -0.10% (5/8)
- dlinear/electricity: -1.31% (8/8)
- dlinear/etth1: +0.98% (4/8)
- dlinear/ettm2: +0.08% (1/8)
- dlinear/traffic: -7.47% (8/8)
- dlinear/weather: -0.79% (8/8)
