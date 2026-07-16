# Traffic H96 TIFO stabilization record

All tuning runs use iTransformer, Traffic/H96, seed 2022 and validation-only
selection (`--skip_final_test`). The test split was inspected only after both
hyperparameters were frozen.

## Filter learning-rate scale

| Scale | Best validation loss | Best epoch | Epochs run |
|---:|---:|---:|---:|
| 0.01 | 0.3647671 | 15 | 20 |
| 0.05 | 0.3648486 | 9 | 14 |
| 0.10 | 0.3648008 | 15 | 20 |
| **0.25** | **0.3597935** | 11 | 16 |
| 0.50 | 0.3617932 | 15 | 20 |
| 0.75 | 0.3687344 | 15 | 20 |

The matched Ori best validation loss is 0.3593674. Scale 0.25 removes the
original TIFO optimization divergence but does not beat Ori by itself.

## Residual strength at scale 0.25

| Alpha | Best validation loss | Best epoch | Epochs run |
|---:|---:|---:|---:|
| 0.10 | 0.3571267 | 15 | 20 |
| 0.25 | 0.3574660 | 15 | 20 |
| **0.50** | **0.3563943** | 15 | 20 |
| 0.75 | 0.3592258 | 15 | 20 |
| 0.90 | 0.3623620 | 15 | 20 |
| 1.00 | 0.3597935 | 11 | 16 |

Validation therefore freezes `tifo_lr_scale=0.25` and
`tifo_residual_alpha=0.5`.

## Frozen seed-2022 gate

The frozen setting was then rerun with one final test on all seven H96
datasets. It beats Ori on ETTh2, ETTm1, Electricity and Weather, but loses on
ETTh1, ETTm2 and Traffic. On Traffic it reduces the historical TIFO failure
from 0.489667 to 0.396480 MSE, while Ori remains better at 0.392449.

Conclusion: residual/filter-LR stabilization is a valid failure mitigation and
supporting ablation, but it does not pass the gate for promotion to a universal
main-method setting. Do not expand it to three seeds or claim a Traffic win.
