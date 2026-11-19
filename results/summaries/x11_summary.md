# X11: TIFO vs free filter (lr x100) under shortened training

| backbone | fraction | pairs | TIFO MSE | free MSE | rel. (free vs TIFO, neg = free better) | TIFO better | two-sided p | free vs Ori rel. | TIFO vs Ori rel. |
|---|---|---|---|---|---|---|---|---|---|
| itransformer | f10 | 18 | 0.7228 | 0.7310 | +1.14% | 12/18 | 0.038 | -1.86% | -2.97% |
| itransformer | f25 | 18 | 0.4273 | 0.4168 | -2.47% | 3/18 | 0.00011 | -2.54% | -0.08% |
| itransformer | f50 | 18 | 0.3660 | 0.3632 | -0.78% | 6/18 | 0.034 | -1.46% | -0.69% |
| itransformer | f100 | 18 | 0.3028 | 0.3008 | -0.64% | 7/18 | 0.099 | -2.13% | -1.50% |
| dlinear | f10 | 18 | 0.6404 | 0.6415 | +0.17% | 6/18 | 0.93 | -4.15% | -4.31% |
| dlinear | f25 | 18 | 0.3883 | 0.3809 | -1.91% | 6/18 | 0.23 | -5.50% | -3.66% |
| dlinear | f50 | 18 | 0.3430 | 0.3390 | -1.16% | 7/18 | 0.25 | -3.95% | -2.82% |
| dlinear | f100 | 18 | 0.2835 | 0.2801 | -1.20% | 8/18 | 0.25 | -2.86% | -1.68% |
