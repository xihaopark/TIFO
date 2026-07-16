# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTm2 | 96 | PatchTST+ORI | 3 | 0.182424 ± 0.001106 | 0.265402 ± 0.001717 |
| ETTm2 | 96 | PatchTST+TIFO[historical] | 3 | 0.176413 ± 0.001118 | 0.259284 ± 0.001161 |

## Paired effect: ETTm2/H96/PatchTST+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.006011 ± 0.000087; wins: 3/3
- Relative MSE reduction: 3.295040 ± 0.053348%
- MAE delta (TIFO - Ori): -0.006118 ± 0.000943
