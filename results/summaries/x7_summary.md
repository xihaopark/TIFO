# X7 shortened training period: TIFO (submitted default) vs Ori

| backbone | train fraction | pairs | Ori MSE | TIFO MSE | rel. Δ % (neg = TIFO better) | TIFO better | Wilcoxon p |
|---|---|---|---|---|---|---|---|
| itransformer | 10% | 18 | 0.7449 | 0.7228 | -2.40 | 15/18 | 3.4e-03 |
| itransformer | 25% | 18 | 0.4276 | 0.4273 | +0.02 | 8/18 | 1.0e+00 |
| itransformer | 50% | 18 | 0.3685 | 0.3660 | -0.72 | 15/18 | 8.4e-04 |
| itransformer | 100% | 18 | 0.3074 | 0.3028 | -1.97 | 15/18 | 6.7e-04 |
| dlinear | 10% | 18 | 0.6693 | 0.6404 | -4.21 | 18/18 | 7.6e-06 |
| dlinear | 25% | 18 | 0.4031 | 0.3883 | -2.77 | 12/18 | 3.4e-03 |
| dlinear | 50% | 18 | 0.3529 | 0.3430 | -2.18 | 12/18 | 3.4e-03 |
| dlinear | 100% | 18 | 0.2883 | 0.2835 | -1.85 | 11/18 | 2.4e-02 |
