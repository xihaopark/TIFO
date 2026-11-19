# TIFO-v2 dev sweep (400 completed runs; seed 2022)

Relative change vs hist_data per cell (negative = better), averaged over cells present.

| backbone | config | cells | Δ vali % | Δ test % (reference only) |
|---|---|---|---|---|
| dlinear | free_hist_lr100 | 8 | -0.67 | -2.00 |
| dlinear | hist_data_lr100 | 8 | -0.51 | -1.06 |
| dlinear | hist_data_lr10 | 8 | -0.45 | -0.54 |
| dlinear | hermraw_permuted | 8 | -0.06 | +0.08 |
| dlinear | hist_data | 8 | +0.00 | +0.00 |
| dlinear | hermraw_data | 8 | +0.03 | +0.13 |
| dlinear | free_herm_lr100 | 8 | +0.30 | +0.28 |
| dlinear | free_hist_lr10 | 8 | +0.36 | -0.09 |
| dlinear | free_herm_lr10 | 8 | +0.56 | +0.67 |
| dlinear | pointri_lr10_data | 8 | +1.11 | +1.28 |
| dlinear | point_h16_lr100_data | 8 | +1.28 | +1.54 |
| dlinear | point_h64_lr100_data | 8 | +1.41 | +1.57 |
| dlinear | point_h64_lr10_data | 8 | +1.65 | +1.78 |
| dlinear | point_h16_lr10_data | 8 | +1.79 | +1.99 |
| dlinear | pointri_lr10_permuted | 8 | +2.31 | +1.79 |
| dlinear | point_h64_lr1_data | 8 | +2.43 | +2.49 |
| dlinear | point_h64_lr10_permuted | 8 | +2.66 | +2.19 |
| dlinear | free_herm_lr1 | 8 | +2.68 | +2.68 |
| dlinear | point_h16_lr10_permuted | 8 | +2.71 | +2.27 |
| dlinear | point_h16_lr100_permuted | 8 | +2.73 | +2.21 |
| dlinear | free_hist_lr1 | 8 | +2.78 | +2.66 |
| dlinear | point_h64_lr100_permuted | 8 | +2.79 | +2.27 |
| dlinear | point_h16_lr1_data | 8 | +3.07 | +2.98 |
| dlinear | point_h64_lr1_permuted | 8 | +3.25 | +2.70 |
| dlinear | point_h16_lr1_permuted | 8 | +3.75 | +3.19 |
| itransformer | free_hist_lr100 | 8 | -1.48 | -0.55 |
| itransformer | free_herm_lr100 | 8 | -1.09 | -0.34 |
| itransformer | free_hist_lr10 | 8 | -1.06 | -0.24 |
| itransformer | free_herm_lr10 | 8 | -0.89 | -0.10 |
| itransformer | hermraw_data | 8 | -0.15 | -0.14 |
| itransformer | hermraw_permuted | 8 | -0.14 | -0.14 |
| itransformer | hist_data | 8 | +0.00 | +0.00 |
| itransformer | free_herm_lr1 | 8 | +0.65 | +0.89 |
| itransformer | free_hist_lr1 | 8 | +0.73 | +1.02 |
| itransformer | point_h16_lr100_data | 8 | +0.90 | +1.75 |
| itransformer | point_h64_lr10_data | 8 | +0.96 | +1.24 |
| itransformer | pointri_lr10_data | 8 | +1.02 | +1.56 |
| itransformer | point_h16_lr10_data | 8 | +1.18 | +1.33 |
| itransformer | pointri_lr10_permuted | 8 | +1.18 | +1.71 |
| itransformer | point_h16_lr100_permuted | 8 | +1.37 | +1.84 |
| itransformer | point_h64_lr1_data | 8 | +1.45 | +1.36 |
| itransformer | point_h64_lr100_permuted | 8 | +1.53 | +1.87 |
| itransformer | point_h64_lr10_permuted | 8 | +1.56 | +2.08 |
| itransformer | point_h16_lr1_data | 8 | +1.57 | +1.56 |
| itransformer | point_h16_lr10_permuted | 8 | +1.79 | +1.92 |
| itransformer | point_h64_lr100_data | 8 | +1.83 | +1.77 |
| itransformer | hist_data_lr10 | 8 | +1.94 | +1.46 |
| itransformer | point_h64_lr1_permuted | 8 | +2.02 | +1.98 |
| itransformer | point_h16_lr1_permuted | 8 | +2.05 | +2.03 |
| itransformer | hist_data_lr100 | 8 | +6.34 | +6.52 |

## Pointwise: data vs permuted (Δ = permuted − data; positive favours data)

| backbone | setting | cells | mean Δ vali | data better (vali) | mean Δ test | data better (test) |
|---|---|---|---|---|---|---|
| dlinear | point_h16_lr1 | 8 | +0.00303 | 5/8 | +0.00045 | 6/8 |
| dlinear | point_h16_lr10 | 8 | +0.00411 | 5/8 | +0.00060 | 6/8 |
| dlinear | point_h16_lr100 | 8 | +0.00615 | 7/8 | +0.00149 | 6/8 |
| dlinear | point_h64_lr1 | 8 | +0.00360 | 5/8 | +0.00046 | 6/8 |
| dlinear | point_h64_lr10 | 8 | +0.00450 | 7/8 | +0.00097 | 6/8 |
| dlinear | point_h64_lr100 | 8 | +0.00580 | 6/8 | +0.00158 | 5/8 |
| itransformer | point_h16_lr1 | 8 | +0.00129 | 7/8 | +0.00088 | 5/8 |
| itransformer | point_h16_lr10 | 8 | +0.00294 | 6/8 | +0.00113 | 7/8 |
| itransformer | point_h16_lr100 | 8 | +0.00220 | 6/8 | -0.00059 | 4/8 |
| itransformer | point_h64_lr1 | 8 | +0.00195 | 7/8 | +0.00122 | 7/8 |
| itransformer | point_h64_lr10 | 8 | +0.00273 | 7/8 | +0.00163 | 7/8 |
| itransformer | point_h64_lr100 | 8 | -0.00169 | 4/8 | -0.00081 | 4/8 |
