# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTm2 | 192 | PatchTST+ORI | 3 | 0.248071 ± 0.001761 | 0.308909 ± 0.000930 |
| ETTm2 | 192 | PatchTST+TIFO[historical] | 3 | 0.242920 ± 0.000787 | 0.303448 ± 0.000572 |
| ETTm2 | 192 | iTransformer+ORI | 3 | 0.252853 ± 0.000934 | 0.312787 ± 0.000704 |
| ETTm2 | 192 | iTransformer+TIFO[historical] | 3 | 0.252052 ± 0.001847 | 0.312359 ± 0.001383 |

## Paired effect: ETTm2/H192/PatchTST+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.005152 ± 0.001210; wins: 3/3
- Relative MSE reduction: 2.074640 ± 0.473416%
- MAE delta (TIFO - Ori): -0.005461 ± 0.000783

## Paired effect: ETTm2/H192/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.000802 ± 0.002671; wins: 2/3
- Relative MSE reduction: 0.314611 ± 1.056884%
- MAE delta (TIFO - Ori): -0.000429 ± 0.001950
