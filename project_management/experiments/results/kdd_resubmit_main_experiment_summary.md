# KDD resubmit main experiment summary

Updated: 2026-07-17

This is the paper-facing summary of completed, artifact-backed results. Values
are mean ± sample standard deviation over seeds 2021/2022/2023.

## Core result: PatchTST on ETTm2 across all horizons

| Horizon | Ori MSE | TIFO MSE | Relative MSE reduction | MSE wins | Ori MAE | TIFO MAE |
|---:|---:|---:|---:|---:|---:|---:|
| 96 | 0.182424 ± 0.001106 | **0.176413 ± 0.001118** | 3.30% | 3/3 | 0.265402 | **0.259284** |
| 192 | 0.248071 ± 0.001761 | **0.242920 ± 0.000787** | 2.07% | 3/3 | 0.308909 | **0.303448** |
| 336 | 0.311617 ± 0.003250 | **0.305713 ± 0.001658** | 1.89% | 3/3 | 0.349640 | **0.345460** |
| 720 | 0.416799 ± 0.001283 | **0.398872 ± 0.000629** | 4.30% | 3/3 | 0.411838 | **0.397847** |

Across all 12 matched horizon/seed pairs, TIFO wins 12/12. The mean relative
MSE reduction is 2.889% ± 1.191%; the mean absolute MSE delta (TIFO minus Ori)
is -0.008749 ± 0.005870. A two-sided sign test over the 12 matched pairs gives
`p=0.0004883`.

## Breadth result: iTransformer H96 on seven datasets

| Dataset | Ori MSE | TIFO MSE | Relative MSE reduction | MSE wins | Judgment |
|---|---:|---:|---:|---:|---|
| ETTh1 | 0.393243 | **0.390588** | 0.68% | 3/3 | stable gain |
| ETTh2 | **0.299868** | 0.301797 | -0.64% | 0/3 | small MSE loss; MAE tied |
| ETTm1 | **0.341437** | 0.342039 | -0.18% | 1/3 | near-neutral; MAE improves |
| ETTm2 | 0.184665 | **0.181195** | 1.88% | 3/3 | stable gain |
| Electricity | 0.148206 | **0.143338** | 3.28% | 3/3 | strong stable gain |
| Traffic | **0.392655** | 0.493411 | -25.66% | 0/3 | documented failure |
| Weather | 0.174723 | **0.168588** | 3.51% | 3/3 | strong stable gain |

The validation-selected filter-LR/residual stabilization reduces the Traffic
failure to 0.396480 MSE on the frozen seed-2022 gate, but Ori remains better at
0.392449. It is therefore supporting failure-analysis evidence, not a promoted
main result.

## Recent-baseline context on ETTm2 H96

| Method | MSE | MAE |
|---|---:|---:|
| TimeEmb (NeurIPS 2025) | **0.164518 ± 0.000304** | **0.243307 ± 0.000275** |
| TFPS (NeurIPS 2025) | 0.172818 ± 0.001181 | 0.255664 ± 0.000283 |
| PatchTST + TIFO | 0.176413 ± 0.001118 | 0.259284 ± 0.001161 |
| iTransformer + TIFO | 0.181195 ± 0.000742 | 0.265726 ± 0.001004 |
| PatchTST Ori | 0.182424 ± 0.001106 | 0.265402 ± 0.001717 |
| iTransformer Ori | 0.184665 ± 0.000829 | 0.269641 ± 0.002345 |

The recent baselines outperform TIFO on this representative cell. The paper
must present TIFO as a broadly applicable backbone enhancement with strong
matched gains on selected backbones/settings, not as the new absolute SOTA.

## Evidence files

- `kdd_resubmit_patchtst_ettm2_all_horizons.{md,csv,json}`
- `kdd_resubmit_h96_all_evidence.{md,csv,json}`
- `kdd_resubmit_ettm2_h192_two_backbones_gate.{md,csv,json}`
- `kdd_resubmit_tifo_traffic_tuning.md`

Every promoted number has a completed launch record, exact command, dataset
hash, seed, final-test log and checkpoint/result manifest under
`experiment_records/` and the repository's ignored raw output directories.
