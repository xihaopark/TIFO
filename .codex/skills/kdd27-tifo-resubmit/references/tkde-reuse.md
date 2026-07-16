# Fuji TKDE evidence reuse

The Fuji TKDE workspace contains related Fredformer/FredNormer experiments, reviewer discussions, code, response drafts, and audit tooling. Use it as a secondary evidence and design source for TIFO, not as automatically interchangeable results.

## Workspace entrypoints

- TKDE workspace: `/mnt/data1/park/Time Series/Forecasting/TKDE`
- Equivalent home path: `/home/park/Time Series/Forecasting/TKDE`
- Core experiment code named by that workspace: `/home/park/Time Series/Forecasting/Fredformer-33`
- TKDE manuscript copy: `/home/park/Time Series/Forecasting/TKDE/overleaf/source`
- Original TKDE decision/reviews: `rebuttal/review_decision_raw.txt`
- Response letter: `rebuttal/response.tex`

Start with:

1. `README.md`
2. `wiki/Experiment-Database-Index.md`
3. `wiki/Rebuttal-Evidence-Table.md`
4. `wiki/Rebuttal-Experiment-Assessment.md`
5. `wiki/Reviewer-Experiment-Checklist-2026-06-16.md`
6. `wiki/Statistical-Comparison.md`
7. `wiki/Interpretability-Artifacts.md`
8. `wiki/Robustness-Results.md`
9. `wiki/Figure-Table-Audit.md`

Use the CSV artifacts under `tables/` rather than copying numbers from prose. In particular, inspect `master_results.csv`, `rebuttal_main_candidates.csv`, `rebuttal_evidence_table.csv`, `best_matrix.csv`, and `incomplete_runs.csv`.

## Prior Codex work on Fuji

When Codex task/thread tools are available, search the Fuji host for recent tasks containing `TKDE`, `Fredformer`, `rebuttal`, `claim calibration`, `supplement sync`, or `response audit`. Read the task rather than relying only on its title.

Known historical task IDs that may help recovery:

- `019f03e5-eca2-79a0-879a-37bdb519c3d9`: response audit, rebuttal package, and manuscript upload validation.
- `019eee11-798d-76b1-b002-5d4640f3dd84`: supplement synchronization, fairness framing, and reference fixes.
- `019ed582-3b3a-7d81-a1bc-d44d506ebdf8`: claim-strength calibration against evidence and caveats.

Treat thread conclusions as leads. Reopen the cited files and results before importing a claim.

## High-value reusable material

- Experiment-governance and completeness-audit scripts.
- Matched ablation design for FredNormer versus original Fredformer.
- Multi-seed stability reporting and statistical comparisons.
- Spectral interpretability and prediction artifact generation.
- Robustness experiment design.
- Reviewer-facing structure: concern, added/rerun experiment, result, evidence location, limitation.
- Claim calibration: state strong wins positively and mixed results with an explicit caveat.
- Static LaTeX audit and clean compilation practices.

## Compatibility gate for numeric reuse

Do not import a TKDE number into the KDD paper until all relevant fields match or the difference is explicitly disclosed:

- dataset identity and preprocessing;
- train/validation/test split;
- `seq_len`, `label_len`, and `pred_len`;
- seed set and number of runs;
- backbone/model version and enabled modules;
- patch size, stride, frequency resolution, and windowing;
- optimizer, learning rate, scheduler, epochs, and early stopping;
- metric code and aggregation convention;
- checkpoint and source-code revision.

If any field is unknown, classify the result as `design_reference` or `needs_rerun`, not manuscript evidence.

## Important known boundary

The TKDE database documents a locked benchmark protocol with `seq_len=96`, `label_len=48`, horizons `96/192/336/720`, and eight datasets. It also separates standard-main, tuned-main, supporting-only, ablation, and stability results. Preserve those roles. Never promote tuned or supporting-only evidence into a standard KDD comparison without transparent labeling and a protocol decision.

Matched comparisons are mandatory. A valid FredNormer/TIFO claim requires matched dataset, horizon, seed, lengths, patch/stride, architecture, optimizer, and early-stopping policy. Unmatched favorable cells are useful for hypothesis generation only.
