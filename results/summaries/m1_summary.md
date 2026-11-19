# M1 gain attribution — summary (555 completed runs)

## Mean test MSE per cell (mean ± std over seeds; n)

| cell | free_herm | free_hist | free_hist_noise | hist_data | hist_nodropout | hist_ones | hist_permuted | hist_random | hist_zeros | noise_only | ori | point_data | point_ones | point_permuted |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dlinear/etth1/96 | 0.3765±0.0000 (5) | 0.3764±0.0000 (5) | 0.3763±0.0000 (5) | 0.3704±0.0001 (5) | 0.3726±0.0022 (5) | 0.3700±0.0002 (5) | 0.3709±0.0007 (5) | 0.3705±0.0002 (5) | 0.3752±0.0017 (5) | 0.3766±0.0000 (5) | 0.3767±0.0000 (5) | 0.3761±0.0002 (5) | 0.3759±0.0001 (5) | 0.3758±0.0002 (5) |
| dlinear/etth1/336 | 0.4310±0.0010 (5) | 0.4309±0.0010 (5) | 0.4309±0.0010 (5) | 0.4295±0.0014 (5) | 0.4277±0.0006 (5) | 0.4283±0.0007 (5) | 0.4295±0.0009 (5) | 0.4293±0.0008 (5) | 0.4306±0.0005 (5) | 0.4310±0.0010 (5) | 0.4310±0.0010 (5) | 0.4310±0.0009 (5) | 0.4310±0.0009 (5) | 0.4310±0.0009 (5) |
| dlinear/ettm2/96 | 0.1634±0.0004 (5) | 0.1633±0.0004 (5) | 0.1632±0.0004 (5) | 0.1658±0.0005 (5) | 0.1659±0.0013 (5) | 0.1649±0.0006 (5) | 0.1651±0.0003 (5) | 0.1652±0.0003 (5) | 0.1650±0.0002 (5) | 0.1635±0.0004 (5) | 0.1635±0.0004 (5) | 0.1634±0.0004 (5) | 0.1635±0.0004 (5) | 0.1635±0.0004 (5) |
| dlinear/ettm2/336 | 0.2723±0.0005 (5) | 0.2722±0.0005 (5) | 0.2721±0.0005 (5) | 0.2736±0.0003 (5) | 0.2735±0.0004 (5) | 0.2727±0.0002 (5) | 0.2734±0.0003 (5) | 0.2734±0.0003 (5) | 0.2730±0.0001 (5) | 0.2724±0.0005 (5) | 0.2724±0.0005 (5) | 0.2724±0.0005 (5) | 0.2724±0.0005 (5) | 0.2724±0.0005 (5) |
| itransformer/etth1/96 | 0.3930±0.0011 (5) | 0.3929±0.0011 (5) | 0.3929±0.0012 (5) | 0.3946±0.0013 (5) | 0.3922±0.0011 (5) | 0.3950±0.0020 (5) | 0.3946±0.0019 (5) | 0.3947±0.0020 (5) | 0.3991±0.0012 (5) | — | 0.3931±0.0011 (5) | 0.3930±0.0011 (5) | 0.3931±0.0011 (5) | 0.3929±0.0011 (5) |
| itransformer/etth1/336 | 0.4901±0.0024 (5) | 0.4897±0.0023 (5) | 0.4898±0.0022 (5) | 0.4855±0.0027 (5) | 0.4915±0.0016 (5) | 0.4962±0.0012 (5) | 0.4853±0.0028 (5) | 0.4854±0.0027 (5) | 0.4985±0.0016 (5) | 0.4908±0.0022 (5) | 0.4907±0.0024 (5) | 0.4898±0.0024 (5) | 0.4903±0.0025 (5) | 0.4904±0.0024 (5) |
| itransformer/ettm2/96 | 0.1844±0.0007 (5) | 0.1845±0.0007 (5) | 0.1836±0.0009 (5) | 0.1817±0.0009 (5) | 0.1800±0.0013 (5) | 0.1828±0.0019 (5) | 0.1821±0.0008 (5) | 0.1818±0.0008 (5) | 0.1795±0.0010 (5) | 0.1836±0.0009 (5) | 0.1844±0.0007 (5) | 0.1845±0.0007 (5) | 0.1844±0.0006 (5) | 0.1844±0.0007 (5) |
| itransformer/ettm2/336 | 0.3151±0.0026 (5) | 0.3151±0.0027 (5) | 0.3149±0.0026 (5) | 0.3145±0.0028 (5) | 0.3132±0.0015 (5) | 0.3145±0.0021 (5) | 0.3146±0.0026 (5) | 0.3128±0.0015 (5) | 0.3076±0.0024 (5) | 0.3150±0.0025 (5) | 0.3152±0.0025 (5) | 0.3158±0.0028 (5) | 0.3153±0.0026 (5) | 0.3153±0.0026 (5) |

## Relative MSE gain vs Ori, averaged over cells with both (per backbone)

**dlinear**: hist_ones +0.37% (n_cells=4), hist_random +0.17% (n_cells=4), hist_permuted +0.14% (n_cells=4), free_hist_noise +0.10% (n_cells=4), free_hist +0.08% (n_cells=4), point_data +0.06% (n_cells=4), point_permuted +0.06% (n_cells=4), point_ones +0.06% (n_cells=4), hist_data +0.05% (n_cells=4), free_herm +0.05% (n_cells=4), noise_only +0.02% (n_cells=4), ori +0.00% (n_cells=4), hist_nodropout -0.00% (n_cells=4), hist_zeros -0.16% (n_cells=4)

**itransformer**: hist_nodropout +0.78% (n_cells=4), hist_random +0.71% (n_cells=4), hist_data +0.59% (n_cells=4), hist_permuted +0.54% (n_cells=4), hist_zeros +0.49% (n_cells=4), free_hist_noise +0.20% (n_cells=4), noise_only +0.17% (n_cells=3), free_hist +0.07% (n_cells=4), free_herm +0.05% (n_cells=4), point_permuted +0.03% (n_cells=4), point_ones +0.02% (n_cells=4), ori +0.00% (n_cells=4), point_data -0.00% (n_cells=4), hist_ones -0.12% (n_cells=4)

## Paired contrasts (seed-matched within cell; Δ = MSE(b) − MSE(a), positive favours a)

| backbone | a | b | pairs | mean Δ | median Δ | a wins | Wilcoxon p |
|---|---|---|---|---|---|---|---|
| dlinear | point_data | point_permuted | 20 | -0.00003 | +0.00003 | 11/20 | 6.22e-01 |
| dlinear | point_data | point_ones | 20 | -0.00002 | +0.00002 | 11/20 | 9.85e-01 |
| dlinear | point_data | free_herm | 20 | +0.00008 | -0.00002 | 9/20 | 8.41e-01 |
| dlinear | point_data | ori | 20 | +0.00021 | +0.00008 | 20/20 | 1.91e-06 |
| dlinear | hist_data | hist_permuted | 20 | -0.00009 | -0.00017 | 7/20 | 3.49e-01 |
| dlinear | hist_data | hist_ones | 20 | -0.00085 | -0.00076 | 1/20 | 1.91e-05 |
| dlinear | hist_data | hist_random | 20 | -0.00023 | -0.00025 | 7/20 | 4.41e-02 |
| dlinear | hist_data | free_hist | 20 | +0.00090 | -0.00051 | 10/20 | 4.75e-01 |
| dlinear | hist_data | hist_nodropout | 20 | +0.00012 | -0.00013 | 9/20 | 8.12e-01 |
| dlinear | hist_data | ori | 20 | +0.00110 | -0.00038 | 10/20 | 3.49e-01 |
| dlinear | free_hist_noise | free_hist | 20 | +0.00008 | +0.00009 | 18/20 | 1.68e-04 |
| dlinear | noise_only | ori | 20 | +0.00007 | +0.00008 | 18/20 | 2.10e-04 |
| dlinear | point_data | hist_data | 20 | -0.00089 | +0.00041 | 10/20 | 3.88e-01 |
| itransformer | point_data | point_permuted | 20 | -0.00004 | -0.00006 | 7/20 | 6.22e-01 |
| itransformer | point_data | point_ones | 20 | -0.00001 | +0.00007 | 12/20 | 5.71e-01 |
| itransformer | point_data | free_herm | 20 | -0.00012 | -0.00003 | 8/20 | 5.22e-01 |
| itransformer | point_data | ori | 20 | +0.00009 | +0.00010 | 12/20 | 2.61e-01 |
| itransformer | hist_data | hist_permuted | 20 | +0.00008 | -0.00007 | 9/20 | 7.01e-01 |
| itransformer | hist_data | hist_ones | 20 | +0.00305 | +0.00113 | 14/20 | 1.72e-02 |
| itransformer | hist_data | hist_random | 20 | -0.00041 | -0.00002 | 10/20 | 2.94e-01 |
| itransformer | hist_data | free_hist | 20 | +0.00144 | +0.00138 | 14/20 | 4.84e-02 |
| itransformer | hist_data | hist_nodropout | 20 | +0.00014 | -0.00068 | 7/20 | 6.74e-01 |
| itransformer | hist_data | ori | 20 | +0.00178 | +0.00147 | 14/20 | 4.00e-02 |
| itransformer | free_hist_noise | free_hist | 20 | +0.00022 | +0.00004 | 11/20 | 3.12e-01 |
| itransformer | noise_only | ori | 15 | +0.00032 | +0.00012 | 9/15 | 1.69e-01 |
| itransformer | point_data | hist_data | 20 | -0.00169 | -0.00165 | 5/20 | 1.72e-02 |
