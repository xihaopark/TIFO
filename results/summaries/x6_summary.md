# X6 controlled high-frequency shift (evaluation only)

Relative MSE change vs Ori (negative = better), seed-matched; strength scales the upper half of non-DC rFFT bins.

| backbone | condition | strength | pairs | mean rel. Δ % | better than Ori | Wilcoxon p |
|---|---|---|---|---|---|---|
| dlinear | free_hist | 0 | 20 | -0.08 | 20/20 | 1.9e-06 |
| dlinear | free_hist | 0.25 | 20 | -0.07 | 20/20 | 1.9e-06 |
| dlinear | free_hist | 0.5 | 20 | -0.07 | 20/20 | 1.9e-06 |
| dlinear | free_hist | 1 | 20 | -0.05 | 16/20 | 1.0e-04 |
| dlinear | hist_data | 0 | 20 | -0.05 | 10/20 | 3.5e-01 |
| dlinear | hist_data | 0.25 | 20 | -0.18 | 10/20 | 2.2e-01 |
| dlinear | hist_data | 0.5 | 20 | -0.32 | 10/20 | 1.6e-01 |
| dlinear | hist_data | 1 | 20 | -0.62 | 10/20 | 1.1e-01 |
| dlinear | hist_ones | 0 | 20 | -0.37 | 11/20 | 4.8e-02 |
| dlinear | hist_ones | 0.25 | 20 | -0.49 | 12/20 | 3.3e-02 |
| dlinear | hist_ones | 0.5 | 20 | -0.63 | 14/20 | 1.7e-02 |
| dlinear | hist_ones | 1 | 20 | -0.92 | 14/20 | 4.2e-03 |
| dlinear | hist_permuted | 0 | 20 | -0.14 | 11/20 | 1.8e-01 |
| dlinear | hist_permuted | 0.25 | 20 | -0.26 | 11/20 | 1.4e-01 |
| dlinear | hist_permuted | 0.5 | 20 | -0.39 | 11/20 | 1.1e-01 |
| dlinear | hist_permuted | 1 | 20 | -0.67 | 11/20 | 5.8e-02 |
| dlinear | hist_random | 0 | 20 | -0.17 | 11/20 | 1.9e-01 |
| dlinear | hist_random | 0.25 | 20 | -0.29 | 11/20 | 1.4e-01 |
| dlinear | hist_random | 0.5 | 20 | -0.42 | 11/20 | 1.1e-01 |
| dlinear | hist_random | 1 | 20 | -0.70 | 12/20 | 7.0e-02 |
| dlinear | point_data | 0 | 20 | -0.06 | 20/20 | 1.9e-06 |
| dlinear | point_data | 0.25 | 20 | -0.06 | 20/20 | 1.9e-06 |
| dlinear | point_data | 0.5 | 20 | -0.06 | 17/20 | 6.3e-05 |
| dlinear | point_data | 1 | 20 | -0.06 | 14/20 | 7.3e-03 |
| dlinear | point_permuted | 0 | 20 | -0.06 | 15/20 | 2.0e-03 |
| dlinear | point_permuted | 0.25 | 20 | -0.06 | 13/20 | 4.9e-03 |
| dlinear | point_permuted | 0.5 | 20 | -0.06 | 13/20 | 8.3e-03 |
| dlinear | point_permuted | 1 | 20 | -0.07 | 13/20 | 3.3e-02 |
| itransformer | free_hist | 0 | 20 | -0.07 | 14/20 | 2.7e-03 |
| itransformer | free_hist | 0.25 | 20 | -0.07 | 14/20 | 3.2e-03 |
| itransformer | free_hist | 0.5 | 20 | -0.07 | 13/20 | 3.7e-03 |
| itransformer | free_hist | 1 | 20 | -0.07 | 13/20 | 3.7e-03 |
| itransformer | hist_data | 0 | 20 | -0.59 | 14/20 | 4.0e-02 |
| itransformer | hist_data | 0.25 | 20 | -0.73 | 15/20 | 2.0e-03 |
| itransformer | hist_data | 0.5 | 20 | -0.89 | 15/20 | 2.6e-04 |
| itransformer | hist_data | 1 | 20 | -1.21 | 19/20 | 3.8e-06 |
| itransformer | hist_ones | 0 | 20 | +0.13 | 8/20 | 2.5e-01 |
| itransformer | hist_ones | 0.25 | 20 | -0.06 | 11/20 | 6.5e-01 |
| itransformer | hist_ones | 0.5 | 20 | -0.27 | 12/20 | 7.8e-01 |
| itransformer | hist_ones | 1 | 20 | -0.76 | 17/20 | 1.2e-03 |
| itransformer | hist_permuted | 0 | 20 | -0.54 | 14/20 | 2.4e-02 |
| itransformer | hist_permuted | 0.25 | 20 | -0.68 | 15/20 | 4.9e-03 |
| itransformer | hist_permuted | 0.5 | 20 | -0.84 | 16/20 | 3.9e-04 |
| itransformer | hist_permuted | 1 | 20 | -1.17 | 18/20 | 1.3e-05 |
| itransformer | hist_random | 0 | 20 | -0.71 | 16/20 | 4.2e-03 |
| itransformer | hist_random | 0.25 | 20 | -0.85 | 16/20 | 1.2e-03 |
| itransformer | hist_random | 0.5 | 20 | -1.00 | 18/20 | 1.0e-04 |
| itransformer | hist_random | 1 | 20 | -1.32 | 20/20 | 1.9e-06 |
| itransformer | point_data | 0 | 20 | +0.00 | 12/20 | 2.6e-01 |
| itransformer | point_data | 0.25 | 20 | +0.00 | 12/20 | 2.6e-01 |
| itransformer | point_data | 0.5 | 20 | -0.00 | 11/20 | 2.8e-01 |
| itransformer | point_data | 1 | 20 | -0.01 | 11/20 | 2.6e-01 |
| itransformer | point_permuted | 0 | 20 | -0.03 | 14/20 | 2.1e-02 |
| itransformer | point_permuted | 0.25 | 20 | -0.02 | 14/20 | 2.4e-02 |
| itransformer | point_permuted | 0.5 | 20 | -0.02 | 13/20 | 3.0e-02 |
| itransformer | point_permuted | 1 | 20 | -0.02 | 11/20 | 6.4e-02 |

## Data score vs controls under shift (Δ = MSE(control) − MSE(data); positive favours data)

| backbone | data | control | strength | pairs | mean Δ | data better | Wilcoxon p |
|---|---|---|---|---|---|---|---|
| dlinear | hist_data | hist_permuted | 0 | 20 | -0.00009 | 7/20 | 3.5e-01 |
| dlinear | hist_data | hist_permuted | 0.25 | 20 | -0.00008 | 8/20 | 5.2e-01 |
| dlinear | hist_data | hist_permuted | 0.5 | 20 | -0.00006 | 8/20 | 6.0e-01 |
| dlinear | hist_data | hist_permuted | 1 | 20 | -0.00002 | 8/20 | 7.6e-01 |
| dlinear | hist_data | hist_ones | 0 | 20 | -0.00085 | 1/20 | 1.9e-05 |
| dlinear | hist_data | hist_ones | 0.25 | 20 | -0.00086 | 2/20 | 8.2e-05 |
| dlinear | hist_data | hist_ones | 0.5 | 20 | -0.00087 | 3/20 | 1.7e-04 |
| dlinear | hist_data | hist_ones | 1 | 20 | -0.00091 | 3/20 | 4.9e-03 |
| dlinear | hist_data | hist_random | 0 | 20 | -0.00023 | 7/20 | 4.4e-02 |
| dlinear | hist_data | hist_random | 0.25 | 20 | -0.00021 | 7/20 | 8.3e-02 |
| dlinear | hist_data | hist_random | 0.5 | 20 | -0.00019 | 8/20 | 1.8e-01 |
| dlinear | hist_data | hist_random | 1 | 20 | -0.00015 | 9/20 | 5.7e-01 |
| dlinear | hist_data | free_hist | 0 | 20 | +0.00090 | 10/20 | 4.7e-01 |
| dlinear | hist_data | free_hist | 0.25 | 20 | +0.00140 | 10/20 | 2.5e-01 |
| dlinear | hist_data | free_hist | 0.5 | 20 | +0.00199 | 10/20 | 1.8e-01 |
| dlinear | hist_data | free_hist | 1 | 20 | +0.00342 | 10/20 | 1.1e-01 |
| dlinear | point_data | point_permuted | 0 | 20 | -0.00003 | 11/20 | 6.2e-01 |
| dlinear | point_data | point_permuted | 0.25 | 20 | -0.00004 | 11/20 | 6.2e-01 |
| dlinear | point_data | point_permuted | 0.5 | 20 | -0.00004 | 12/20 | 6.2e-01 |
| dlinear | point_data | point_permuted | 1 | 20 | -0.00005 | 10/20 | 7.0e-01 |
| itransformer | hist_data | hist_permuted | 0 | 20 | +0.00008 | 9/20 | 7.0e-01 |
| itransformer | hist_data | hist_permuted | 0.25 | 20 | +0.00008 | 10/20 | 9.0e-01 |
| itransformer | hist_data | hist_permuted | 0.5 | 20 | +0.00007 | 10/20 | 9.9e-01 |
| itransformer | hist_data | hist_permuted | 1 | 20 | +0.00006 | 9/20 | 7.8e-01 |
| itransformer | hist_data | hist_ones | 0 | 20 | +0.00305 | 14/20 | 1.7e-02 |
| itransformer | hist_data | hist_ones | 0.25 | 20 | +0.00300 | 14/20 | 1.7e-02 |
| itransformer | hist_data | hist_ones | 0.5 | 20 | +0.00289 | 14/20 | 2.1e-02 |
| itransformer | hist_data | hist_ones | 1 | 20 | +0.00245 | 13/20 | 1.1e-01 |
| itransformer | hist_data | hist_random | 0 | 20 | -0.00041 | 10/20 | 2.9e-01 |
| itransformer | hist_data | hist_random | 0.25 | 20 | -0.00039 | 10/20 | 3.1e-01 |
| itransformer | hist_data | hist_random | 0.5 | 20 | -0.00038 | 10/20 | 3.3e-01 |
| itransformer | hist_data | hist_random | 1 | 20 | -0.00037 | 10/20 | 6.2e-01 |
| itransformer | hist_data | free_hist | 0 | 20 | +0.00144 | 14/20 | 4.8e-02 |
| itransformer | hist_data | free_hist | 0.25 | 20 | +0.00200 | 14/20 | 1.1e-02 |
| itransformer | hist_data | free_hist | 0.5 | 20 | +0.00265 | 15/20 | 4.8e-04 |
| itransformer | hist_data | free_hist | 1 | 20 | +0.00425 | 19/20 | 5.7e-06 |
| itransformer | point_data | point_permuted | 0 | 20 | -0.00004 | 7/20 | 6.2e-01 |
| itransformer | point_data | point_permuted | 0.25 | 20 | -0.00002 | 7/20 | 6.5e-01 |
| itransformer | point_data | point_permuted | 0.5 | 20 | -0.00000 | 7/20 | 7.6e-01 |
| itransformer | point_data | point_permuted | 1 | 20 | +0.00006 | 7/20 | 9.0e-01 |
