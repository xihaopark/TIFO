# TIFO paper–code–evidence matrix

Updated: 2026-07-16

Overall state: `needs_experiment`

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
| scaling | Per-channel z-score normalization. | Dataset scaler is fit on training data; TIFO additionally applies per-window z-score before global FFT statistics. | under-specified | Document both transformations and their order. |
| seeds/runs | Tables report mean ± standard deviation. | Main shell scripts use `itr=1`; 102 result directories are unique configs, with only a few explicitly seed-tagged runs. | not verified | Run a declared seed set, retain per-seed metrics/config/checkpoint logs and aggregate mechanically. |
| backbone baseline | Ori rows and normalization baselines are compared. | Model builder always computes/injects the TIFO mask; no clean disable flag. | not reproducible | Add a single code path with `method={ori,tifo,revin,san,fan,...}` and matched configs. |
| PatchTST patching | Reproducible configuration implied. | `models/PatchTST.py` hardcodes `patch_len=16`, `stride=8`; CLI values are ignored. | hidden fixed setting | Expose and record patch/stride or explicitly document the fixed values. |
| metric | MSE/MAE and runtime comparisons. | MSE/MAE arrays exist; DTW logging prints a Python function object because computation is commented. | partially valid | Remove invalid DTW output and define runtime measurement protocol. |
| inverse mapping | TIFO is presented as a general operator. | DLinear/iTransformer use inverse filtering; PatchTST forecast returns without `inverse_filter`. | implementation divergence | Decide intended operator semantics, then align all backbones or disclose difference. |

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
| Main forecasting table | PatchTST/iTransformer Ori vs TIFO | TIFO code exists; Ori switch missing | Some rounded values appear in local outputs, but aggregation is unknown. | needs_experiment | Implement matched switch, rerun 3 seeds, then regenerate table. |
| Normalization comparison | DLinear/iTransformer with Ori, RevIN, SAN, FAN, TIFO, TIFO+SAN | RevIN layer present; official FAN/SAN source pinned; unified integration missing | No complete local matched matrix. | needs_experiment | Build one runner and run representative gate cells before full matrix. |
| Stationarity metric ablation | mu/sigma, alternatives | Current code implements mu/sigma only | Paper table not tied to an artifact ledger. | needs_experiment | Implement metric enum and paired seeds on ETTh1 plus a shift-heavy dataset. |
| S versus random initialization | TIFO variants | No audited variant switch | Existing claims are not traceable to complete per-seed results. | needs_experiment | Match everything except initialization and report paired deltas. |
| Shift reduction/representation | spectral distribution figures and learned weights | Figures exist in paper tree; generating configs/raw arrays are not yet mapped | Visual files alone are insufficient. | needs_experiment | Regenerate train/test spectral-distance and weight-correlation artifacts. |
| Efficiency | DLinear/PatchTST timings | Historical table exists | Timer boundary, warmup and hardware metadata not fully mapped. | needs_experiment | Use synchronized wall-clock protocol, same hardware/batch, report parameters/FLOPs separately. |
| Window/FFT/EMA ablations | Tables X/Y/Z/W/V | Narrative/table bodies exist with symbolic references | Artifact origins are not yet verified; one bolding error is known. | draft_with_gaps | Recover commands/results, assign real labels, regenerate formatting. |
| Recent baselines | 2025–2026 methods | TSLib pinned as source pool | No selected/rerun baseline evidence. | needs_experiment | Choose 2–4 relevant runnable models after protocol gate. |
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
