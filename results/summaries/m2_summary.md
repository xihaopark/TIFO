# M2 unified-protocol comparison (1344 seed-level rows)

## DLinear: 28 dataset-horizon cells with all methods

| method | mean MSE | mean MAE | best-MSE cells | TIFO better (seed pairs) | Wilcoxon p (TIFO vs method) |
|---|---|---|---|---|---|
| TIFO | 0.3571 | 0.3527 | 5 | — | — |
| TIFO*(re-impl.) | 0.3486 | 0.3542 | 10 | 32/84 | 8.0e-04 |
| Ori | 0.3638 | 0.3581 | 1 | 68/84 | 5.7e-12 |
| RevIN | 0.3633 | 0.3572 | 0 | 68/84 | 1.1e-11 |
| SAN | 0.3516 | 0.3571 | 1 | 44/84 | 1.4e-01 |
| FAN | 0.3811 | 0.3822 | 0 | 66/84 | 1.5e-04 |
| ACN | 0.3570 | 0.3550 | 4 | 35/84 | 4.5e-01 |
| WDAN | 0.3401 | 0.3467 | 7 | 29/84 | 1.7e-05 |

## iTransformer: 28 dataset-horizon cells with all methods

| method | mean MSE | mean MAE | best-MSE cells | TIFO better (seed pairs) | Wilcoxon p (TIFO vs method) |
|---|---|---|---|---|---|
| TIFO | 0.3404 | 0.3465 | 1 | — | — |
| TIFO*(re-impl.) | 0.3506 | 0.3552 | 2 | 46/84 | 2.2e-01 |
| Ori | 0.3435 | 0.3484 | 3 | 61/84 | 7.6e-07 |
| RevIN | 0.3449 | 0.3477 | 0 | 61/84 | 1.5e-05 |
| SAN | 0.3517 | 0.3565 | 5 | 45/84 | 8.6e-02 |
| FAN | 0.3999 | 0.3928 | 0 | 81/84 | 3.4e-15 |
| ACN | 0.3439 | 0.3452 | 5 | 36/84 | 2.0e-01 |
| WDAN | 0.3440 | 0.3485 | 12 | 39/84 | 3.1e-01 |

