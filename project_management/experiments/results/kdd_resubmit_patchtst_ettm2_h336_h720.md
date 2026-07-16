# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTm2 | 336 | PatchTST+ORI | 3 | 0.311617 ± 0.003250 | 0.349640 ± 0.001919 |
| ETTm2 | 336 | PatchTST+TIFO[historical] | 3 | 0.305713 ± 0.001658 | 0.345460 ± 0.001684 |
| ETTm2 | 720 | PatchTST+ORI | 3 | 0.416799 ± 0.001283 | 0.411838 ± 0.001090 |
| ETTm2 | 720 | PatchTST+TIFO[historical] | 3 | 0.398872 ± 0.000629 | 0.397847 ± 0.000929 |

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
