# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTm2 | 96 | TFPS | 3 | 0.172818 ± 0.001181 | 0.255664 ± 0.000283 |
| ETTm2 | 96 | TimeEmb | 3 | 0.164518 ± 0.000304 | 0.243307 ± 0.000275 |
| ETTm2 | 96 | iTransformer+ORI | 3 | 0.184665 ± 0.000829 | 0.269641 ± 0.002345 |
| ETTm2 | 96 | iTransformer+TIFO[historical] | 3 | 0.181195 ± 0.000742 | 0.265726 ± 0.001004 |
| ETTm2 | 96 | iTransformer+TIFO[identity_prior] | 3 | 0.184899 ± 0.001854 | 0.269309 ± 0.002842 |
| ETTm2 | 96 | iTransformer+TIFO[identity_unregularized] | 3 | 0.187039 ± 0.001759 | 0.272709 ± 0.001624 |

## Paired effect: iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.003471 ± 0.001314; wins: 3/3
- Relative MSE reduction: 1.877667 ± 0.704346%
- MAE delta (TIFO - Ori): -0.003915 ± 0.002773

## Paired effect: iTransformer+TIFO[identity_prior]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.000234 ± 0.001603; wins: 1/3
- Relative MSE reduction: -0.126525 ± 0.870027%
- MAE delta (TIFO - Ori): -0.000331 ± 0.000713

## Paired effect: iTransformer+TIFO[identity_unregularized]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.002373 ± 0.002579; wins: 1/3
- Relative MSE reduction: -1.289424 ± 1.398879%
- MAE delta (TIFO - Ori): 0.003068 ± 0.003942
