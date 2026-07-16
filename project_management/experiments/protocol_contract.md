# Proposed matched experiment contract

Status: `gate_v1_implemented; full_contract_not_frozen`

Purpose: provide one auditable task definition for Ori, TIFO, normalization
baselines, closest methods and recent forecasting models.

## Recommended locked fields

| Field | Recommended contract | Rationale |
|---|---|---|
| datasets | ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Traffic, Weather | Preserve prior paper coverage. |
| horizons | 96, 192, 336, 720 | Preserve prior task grid and TSLib convention. |
| ETT split | canonical fixed 12/4/4-month train/validation/test borders | Matches the current loader and established ETT protocol; do not call it generic 7:2:1. |
| custom split | chronological 70/10/20 train/validation/test | Matches the current loader; correct the appendix's 70/20/10 description. |
| scaler | fit on training partition only, apply unchanged to validation/test | Prevent leakage; explicitly override legacy FAN defaults. |
| label length | 48 | Matches current runs and TSLib-style scripts. |
| PatchTST/iTransformer input length | 96 | Matches current main comparison contract. |
| DLinear input length | 336 on ETT, 96 on Electricity/Traffic/Weather | Matches current scripts; present as backbone-specific, never as fixed L=96 for the whole table. |
| seed set | 2021, 2022, 2023 initially; expand if variance is high | Minimum matched stability evidence and compatible with existing partial repeats. |
| selection | validation MSE only; test set evaluated once per frozen run | Avoid test-set tuning. |
| metrics | MSE and MAE, same implementation and aggregation for all methods | Matches paper; invalid DTW logging excluded. |
| early stopping | identical within each matched backbone/cell | Prevent method-dependent training budgets. |
| hardware | same GPU class for timing comparisons; accuracy may use any recorded equivalent device | Separates accuracy reproducibility from timing fairness. |

## Method comparison rule

Within a dataset/backbone/horizon/seed cell, every field above plus optimizer,
learning rate, scheduler, epochs, batch size, architecture and patch/stride must
match. Only the declared method module may change.

Required first comparison set:

- `ori`
- `tifo`
- `revin`
- `san`
- `fan`
- `tifo_san` only if ordering and composition are explicitly defined

FilterNet and recent forecasting baselines are model-level comparisons rather
than drop-in normalization modules. Give them the same data task and selection
budget, while retaining their documented architecture-specific defaults.

## Required run manifest

Every new run must record:

- run ID, timestamp and run class (`standard`, `tuned`, `ablation`,
  `sensitivity`, `supporting`);
- reviewer concern IDs and paper target;
- dataset path plus hash, split implementation and scaler scope;
- model, method, all lengths, patch/stride and frequency configuration;
- seed, optimizer, scheduler, epochs, patience and selection metric;
- source git revision, dirty-state flag, environment and hardware;
- exact command, checkpoint, log and metric paths;
- final status, MSE/MAE and failure reason when applicable.

## Freeze blockers

Before the full protocol becomes `frozen_v1`:

1. Confirm whether the authors want to preserve DLinear's backbone-specific
   length 336 or standardize it to 96 and rerun all DLinear comparisons.
2. Decide a uniform search/tuning budget for module baselines and model
   baselines. The representative ETTm2 gate is provisionally fixed at 30 epochs,
   patience 5, batch size 32 and learning rate 1e-4 for pipeline validation; it
   is not yet the final paper-wide optimization budget.

Completed prerequisites: the Ori/TIFO switch and all three native backbone
forward paths are smoke-tested; TimeEmb and TFPS (NeurIPS 2025) are selected,
pinned and forward-smoke-tested; the canonical 12-run ETTm2/96/three-seed gate
dry-runs successfully.

External-baseline blocker: the pinned TimeEmb and TFPS trainers evaluate the
test split each epoch. Before evidence execution, implement a recorded adapter
that removes this call while keeping validation-based early stopping and a
single final test evaluation.

Until those decisions are recorded, new exploratory runs must be labeled
`supporting` and cannot replace main-table evidence.
