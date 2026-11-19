# X5 synthetic: stationary-bin preference of learned gains

| backbone | strength | condition | AUC (mean over seeds) | test MSE | ΔMSE vs Ori % |
|---|---|---|---|---|---|
| dlinear | 0p5 | free_herm_lr10 | 0.571 (n=3) | 0.0737 | -3.46 |
| dlinear | 0p5 | hist_data | 0.649 (n=3) | 0.0700 | -8.34 |
| dlinear | 0p5 | hist_permuted | 0.726 (n=3) | 0.0677 | -11.35 |
| dlinear | 0p5 | ori | — | 0.0763 | +0.00 |
| dlinear | 0p5 | point_data_lr10 | 1.000 (n=3) | 0.0735 | -3.70 |
| dlinear | 0p5 | point_permuted_lr10 | 0.728 (n=3) | 0.0726 | -4.88 |
| dlinear | 1p0 | free_herm_lr10 | 0.533 (n=3) | 0.1849 | -4.86 |
| dlinear | 1p0 | hist_data | 0.651 (n=3) | 0.1733 | -10.81 |
| dlinear | 1p0 | hist_permuted | 0.739 (n=3) | 0.1720 | -11.50 |
| dlinear | 1p0 | ori | — | 0.1943 | +0.00 |
| dlinear | 1p0 | point_data_lr10 | 1.000 (n=3) | 0.1866 | -3.98 |
| dlinear | 1p0 | point_permuted_lr10 | 0.701 (n=3) | 0.1860 | -4.27 |
| dlinear | 2p0 | free_herm_lr10 | 0.526 (n=3) | 0.3370 | -5.67 |
| dlinear | 2p0 | hist_data | 0.633 (n=3) | 0.3135 | -12.23 |
| dlinear | 2p0 | hist_permuted | 0.732 (n=3) | 0.3132 | -12.33 |
| dlinear | 2p0 | ori | — | 0.3573 | +0.00 |
| dlinear | 2p0 | point_data_lr10 | 1.000 (n=3) | 0.3407 | -4.64 |
| dlinear | 2p0 | point_permuted_lr10 | 0.694 (n=3) | 0.3407 | -4.64 |
| itransformer | 0p5 | free_herm_lr10 | 0.728 (n=3) | 0.0775 | +0.71 |
| itransformer | 0p5 | hist_data | 0.810 (n=3) | 0.0822 | +6.81 |
| itransformer | 0p5 | hist_permuted | 0.841 (n=3) | 0.0828 | +7.64 |
| itransformer | 0p5 | ori | — | 0.0770 | +0.00 |
| itransformer | 0p5 | point_data_lr10 | 1.000 (n=3) | 0.0780 | +1.29 |
| itransformer | 0p5 | point_permuted_lr10 | 0.671 (n=3) | 0.0765 | -0.54 |
| itransformer | 1p0 | free_herm_lr10 | 0.871 (n=3) | 0.1853 | -1.15 |
| itransformer | 1p0 | hist_data | 0.782 (n=3) | 0.1902 | +1.46 |
| itransformer | 1p0 | hist_permuted | 0.791 (n=3) | 0.1906 | +1.71 |
| itransformer | 1p0 | ori | — | 0.1874 | +0.00 |
| itransformer | 1p0 | point_data_lr10 | 1.000 (n=3) | 0.1887 | +0.69 |
| itransformer | 1p0 | point_permuted_lr10 | 0.701 (n=3) | 0.1867 | -0.41 |
| itransformer | 2p0 | free_herm_lr10 | 0.991 (n=3) | 0.3257 | -1.84 |
| itransformer | 2p0 | hist_data | 0.916 (n=3) | 0.3207 | -3.34 |
| itransformer | 2p0 | hist_permuted | 0.893 (n=3) | 0.3228 | -2.72 |
| itransformer | 2p0 | ori | — | 0.3318 | +0.00 |
| itransformer | 2p0 | point_data_lr10 | 1.000 (n=3) | 0.3335 | +0.51 |
| itransformer | 2p0 | point_permuted_lr10 | 0.680 (n=3) | 0.3218 | -3.03 |
