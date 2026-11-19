# C3 (pre-registered): does stability beyond energy help? (Δ = MSE(b) − MSE(a); positive favours a)

| backbone | a | b | role | pairs | mean Δ | a better | one-sided Wilcoxon p (a < b) |
|---|---|---|---|---|---|---|---|
| itransformer | stab_resid | permuted | H3 (primary) | 40 | +0.00191 | 31/40 | 8.36e-06 |
| itransformer | energy | permuted | secondary | 40 | +0.00054 | 18/40 | 1.81e-01 |
| itransformer | data | energy | secondary | 40 | +0.00046 | 26/40 | 1.55e-02 |
| itransformer | data | stab_resid | secondary | 40 | -0.00091 | 18/40 | 9.77e-01 |
| dlinear | stab_resid | permuted | H3 (primary) | 40 | -0.00022 | 23/40 | 6.18e-01 |
| dlinear | energy | permuted | secondary | 40 | +0.00119 | 19/40 | 9.16e-02 |
| dlinear | data | energy | secondary | 40 | -0.00012 | 17/40 | 7.54e-01 |
| dlinear | data | stab_resid | secondary | 40 | +0.00129 | 30/40 | 2.33e-03 |
