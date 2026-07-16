# TIFO paper–code–evidence matrix

Updated: 2026-07-17

Overall state: `representative_gate_in_progress; coverage_experiments_open`

This is the control surface for deciding whether a manuscript claim can be
retained. A manuscript value is not verified merely because the same rounded
number appears in a text file; its configuration, seed set and code revision
must also be recoverable.

## Claimed benchmark contract versus implementation

| Field | Manuscript claim | Current implementation/artifact | Assessment | Required resolution |
|---|---|---|---|---|
| datasets | ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Traffic, Weather | All seven data files are present locally. | compatible at identity level | Hash and record each input file before reruns. |
| horizons | 96, 192, 336, 720 | Result directory names cover these horizons. | likely compatible | Parse configs/log commands, not directory names alone. |
| input length | Main setup says fixed `L=96`; later text says iTransformer 96 and DLinear 336. | DLinear scripts use 336 for ETT and 96 for custom data; PatchTST/iTransformer generally use 96. | contradiction | Correct the paper and freeze a per-backbone contract before comparison. |
| split | Main text says TSLib `7:2:1`; appendix algorithm says train/val/test `70/20/10`. | ETT loader uses fixed 12/4/4-month borders; custom loader uses 70/10/20. | critical mismatch | Adopt one implementation-accurate protocol and rerun every method under it. |
| scaling | Per-channel z-score normalization. | Dataset scaler is fit on training data. The recovered result-producing TIFO computes Stage-I full-FFT statistics on these scaled training windows, while the backbone path applies its existing per-window normalization before TIFO. | implementation recovered; paper under-specified | Document the two scaling locations without changing the frozen theory claims. |
| seeds/runs | Tables report mean ± standard deviation. | The new ETTm2/H96 gate retains seeds 2021/2022/2023, exact commands, logs, dataset hashes and mechanical aggregation. Historical full-table cells remain mostly single-run. | representative cell verified | Extend the same three-seed contract to the required matrix. |
| backbone baseline | Ori rows and normalization baselines are compared. | Native runner exposes `method={ori,tifo}`. On iTransformer/ETTm2/H96, recovered TIFO beats Ori in 3/3 seeds: mean MSE 0.181195 vs 0.184665. | representative gate passed | Repeat on PatchTST and additional datasets/horizons before broad claims. |
| PatchTST patching | Reproducible configuration implied. | PatchTST now consumes CLI `patch_len` and `stride`; defaults remain 16/8. | implementation aligned | Record both values in every evidence manifest. |
| metric | MSE/MAE and runtime comparisons. | MSE/MAE arrays and manifests are emitted; invalid DTW function-object logging is removed. | partially valid | Define and implement the runtime measurement protocol. |
| inverse mapping | The paper maps the weighted spectrum by iDFT and feeds the result into the forecasting backbone. | The recovered main path transforms only the input and does not inverse-filter predictions. Replaying the 2025 checkpoint matches saved predictions at mean absolute error 1.4e-6; adding prediction inverse filtering gives 0.78 error. | paper-aligned path verified | Keep prediction inverse filtering removed from all backbones. |

## Local artifact inventory

| Artifact | Observed | What it proves | What it does not prove |
|---|---:|---|---|
| `results/*/metrics.npy` | 102 | 84 base rows cover the complete 7 × 3 × 4 dataset/backbone/horizon grid; 18 explicit seed rows cover six selected cells. | Full multi-seed means, fair search budgets, or table provenance. |
| result directories by backbone | PatchTST 37; iTransformer 37; DLinear 28 | The three named backbones were executed. | Ori/RevIN/SAN/FAN coverage. |
| checkpoint directories | 102 | Checkpoint folders were created. | That each checkpoint matches the published table or is loadable. |
| log files | 84 | Some command/training histories are recoverable. | Complete command provenance for all 102 result directories. |
| result text | 402 lines | Historical metric lines exist. | Unique runs or valid DTW values. |

The detailed comparison in `table1_provenance_audit.md` finds that only the
ETTm2 PatchTST central value rounds to the paper's value. Traffic PatchTST has a
particularly large mismatch (paper 0.427 versus local mean 0.532318).

## Paper-facing experiment matrix

| Paper evidence | Backbones/methods | Local runnable status | Result provenance | Readiness | Next action |
|---|---|---|---|---|---|
| Main forecasting table | PatchTST/iTransformer Ori vs TIFO | Unified Ori/TIFO switch, historical operator recovery and mechanical seed aggregation implemented | iTransformer/ETTm2/H96: TIFO 0.181195 ± 0.000742 vs Ori 0.184665 ± 0.000829 MSE; 3/3 wins, 1.88% relative reduction. | one representative cell passed | Run PatchTST and expand datasets/horizons before replacing the full paper table. |
| Normalization comparison | DLinear/iTransformer with Ori, RevIN, SAN, FAN, TIFO, TIFO+SAN | RevIN layer present; official FAN/SAN source pinned; unified integration missing | No complete local matched matrix. | needs_experiment | Build one runner and run representative gate cells before full matrix. |
| Stationarity metric ablation | mu/sigma, alternatives | Current code implements mu/sigma only | Paper table not tied to an artifact ledger. | needs_experiment | Implement metric enum and paired seeds on ETTh1 plus a shift-heavy dataset. |
| S versus random initialization | TIFO variants | No audited variant switch | Existing claims are not traceable to complete per-seed results. | needs_experiment | Match everything except initialization and report paired deltas. |
| Shift reduction/representation | spectral distribution figures and learned weights | Figures exist in paper tree; generating configs/raw arrays are not yet mapped | Visual files alone are insufficient. | needs_experiment | Regenerate train/test spectral-distance and weight-correlation artifacts. |
| Efficiency | DLinear/PatchTST timings | Historical table exists | Timer boundary, warmup and hardware metadata not fully mapped. | needs_experiment | Use synchronized wall-clock protocol, same hardware/batch, report parameters/FLOPs separately. |
| Window/FFT/EMA ablations | Tables X/Y/Z/W/V | Narrative/table bodies exist with symbolic references | Artifact origins are not yet verified; one bolding error is known. | draft_with_gaps | Recover commands/results, assign real labels, regenerate formatting. |
| Recent baselines | TimeEmb and TFPS (NeurIPS 2025) | Official repositories pinned; recorded validation-only/NumPy-2 patches; Blackwell smoke and unified matrix pass. | ETTm2/H96 three-seed MSE: TimeEmb 0.164518 ± 0.000304; TFPS 0.172818 ± 0.001181. | representative_gate_complete | Freeze this table as new-baseline evidence and expand only the paper-required cells. |
| FilterNet relationship | FilterNet vs/complement with TIFO | Official source pinned | No matched result. | needs_experiment | First do method matrix; then a representative matched experiment. |
| Beyond forecasting | imputation/classification | Task branches exist but TIFO behavior is inconsistent | No evidence. | optional_needs_experiment | Keep as future work unless a clean low-cost experiment is run. |

## Reuse boundary for Fuji TKDE

Fuji TKDE is immediately reusable for governance, scripts, matched-pair design,
multi-seed aggregation, caveat language and artifact indexing. Its numeric
results are not automatically KDD evidence.

| Compatibility field | TKDE locked protocol | TIFO current/paper state | Numeric reuse |
|---|---|---|---|
| input/label lengths | `seq_len=96`, `label_len=48` | Mixed: paper claims 96, DLinear ETT scripts use 336 | fail/unknown |
| horizons | 96/192/336/720 | same set | pass |
| dataset split | TSLib-derived, locked by audited logs | paper and TIFO loader descriptions conflict | unknown |
| model | Fredformer/FredNormer | DLinear/PatchTST/iTransformer + TIFO | fail |
| seeds | documented matched 2021/2022/2023 for selected cells | mostly single-run and incompletely tagged | fail |
| metric governance | database, standard/tuned/supporting roles | unindexed result directories | fail |

Conclusion: import the TKDE evidence discipline now; classify TKDE numbers as
`design_reference` unless a deliberately matched TIFO experiment is created.

## Minimal credible rerun gate

Before launching a full benchmark, require these representative matched cells:

1. ETTm2, horizon 96: Ori/TIFO on iTransformer and PatchTST, seeds
   2021/2022/2023, to audit the headline 55.3%/33.3% gains.
2. ETTh1, horizon 96: Ori/TIFO plus score alternatives, same seeds.
3. One high-dimensional custom dataset (Electricity or Traffic), horizon 96:
   Ori/TIFO and one normalization baseline, same seeds.
4. Every run must emit config JSON, git revision, data hash, seed, metrics,
   runtime metadata and checkpoint/result paths.

Only after this gate passes should the full 7 × 4 matrix and recent baselines
be scheduled.
