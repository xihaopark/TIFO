# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTm2 | 96 | PatchTST+ORI | 3 | 0.182424 ± 0.001106 | 0.265402 ± 0.001717 |
| ETTm2 | 96 | PatchTST+TIFO[historical] | 3 | 0.176413 ± 0.001118 | 0.259284 ± 0.001161 |
| ETTm2 | 192 | PatchTST+ORI | 3 | 0.248071 ± 0.001761 | 0.308909 ± 0.000930 |
| ETTm2 | 192 | PatchTST+TIFO[historical] | 3 | 0.242920 ± 0.000787 | 0.303448 ± 0.000572 |
| ETTm2 | 192 | iTransformer+ORI | 3 | 0.252853 ± 0.000934 | 0.312787 ± 0.000704 |
| ETTm2 | 192 | iTransformer+TIFO[historical] | 3 | 0.252052 ± 0.001847 | 0.312359 ± 0.001383 |
| ETTm2 | 336 | PatchTST+ORI | 3 | 0.311617 ± 0.003250 | 0.349640 ± 0.001919 |
| ETTm2 | 336 | PatchTST+TIFO[historical] | 3 | 0.305713 ± 0.001658 | 0.345460 ± 0.001684 |
| ETTm2 | 720 | PatchTST+ORI | 3 | 0.416799 ± 0.001283 | 0.411838 ± 0.001090 |
| ETTm2 | 720 | PatchTST+TIFO[historical] | 3 | 0.398872 ± 0.000629 | 0.397847 ± 0.000929 |

## Paired effect: ETTm2/H96/PatchTST+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.006011 ± 0.000087; wins: 3/3
- Relative MSE reduction: 3.295040 ± 0.053348%
- MAE delta (TIFO - Ori): -0.006118 ± 0.000943

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

## Paired effect: ETTm2/H336/PatchTST+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.005904 ± 0.004212; wins: 3/3
- Relative MSE reduction: 1.886056 ± 1.330512%
- MAE delta (TIFO - Ori): -0.004180 ± 0.003127

## Paired effect: ETTm2/H720/PatchTST+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.017927 ± 0.001062; wins: 3/3
- Relative MSE reduction: 4.300801 ± 0.243345%
- MAE delta (TIFO - Ori): -0.013992 ± 0.001227
