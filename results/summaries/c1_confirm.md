# C1 confirmatory test (pre-registered): pointwise data vs permuted

| backbone | pairs | mean Δ (perm − data) | median Δ | data better | one-sided Wilcoxon p (data < perm) |
|---|---|---|---|---|---|
| itransformer | 40 | +0.00100 | +0.00106 | 26/40 | 1.04e-02 |
| dlinear | 40 | +0.00107 | +0.00027 | 28/40 | 1.58e-04 |

Per cell (mean over seeds, Δ = perm − data):

- dlinear/electricity/96: +0.00016 (4/4)
- dlinear/electricity/336: +0.00114 (4/4)
- dlinear/etth1/96: -0.00027 (0/4)
- dlinear/etth1/336: -0.00016 (0/4)
- dlinear/ettm2/96: +0.00040 (4/4)
- dlinear/ettm2/336: +0.00032 (4/4)
- dlinear/traffic/96: +0.00050 (4/4)
- dlinear/traffic/336: -0.00012 (0/4)
- dlinear/weather/96: +0.00312 (4/4)
- dlinear/weather/336: +0.00560 (4/4)
- itransformer/electricity/96: +0.00313 (4/4)
- itransformer/electricity/336: +0.00465 (4/4)
- itransformer/etth1/96: +0.00082 (4/4)
- itransformer/etth1/336: -0.00165 (1/4)
- itransformer/ettm2/96: -0.00087 (0/4)
- itransformer/ettm2/336: -0.00093 (1/4)
- itransformer/traffic/96: +0.00075 (3/4)
- itransformer/traffic/336: -0.00100 (1/4)
- itransformer/weather/96: +0.00192 (4/4)
- itransformer/weather/336: +0.00319 (4/4)
