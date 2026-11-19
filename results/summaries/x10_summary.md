# X10 robust score (median / 1.4826 MAD) vs mean/std score

| backbone | pairs | data MSE | robust MSE | rel. Δ % (neg = robust better) | robust better | two-sided Wilcoxon p | data re-run vs TIFO final (rel. %) |
|---|---|---|---|---|---|---|---|
| iTransformer | 84 | 0.3404 | 0.3402 | -0.05 | 54/84 | 0.039 | +0.00 |
| DLinear | 84 | 0.3571 | 0.3561 | -0.29 | 49/84 | 0.0086 | +0.00 |
