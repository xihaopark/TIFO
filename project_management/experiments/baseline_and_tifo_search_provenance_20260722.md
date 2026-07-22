# TIFO resubmission: baseline and selection provenance

Date: 2026-07-22

Purpose: provide the exact, auditable answer to the reviewers' tuning-fairness
question. This record distinguishes official configurations, validation-only
selection, frozen final testing, and later diagnostics. It must not be summarized
as an equal-search-budget experiment because the search budgets are not equal.

## Fixed evaluation contract

- Forecasting task: multivariate long-term forecasting, `H=96` for the recent
  plug-in comparison.
- Final seeds: 2021, 2022, and 2023.
- Configuration selection seed: 2022 validation data only.
- Selection matrices set `skip_final_test=true`; promoted matrices contain the
  three final seeds.
- Absolute ACN/WDAN/TIFO values are shown for completeness. Plug-in effects are
  isolated by rerunning the bare backbone inside each method's own engine.
- Dataset hashes, resolved commands, logs, physical GPU, and final metrics are
  stored in each `experiment_records/<run_id>/launch.json` and `run.log`.

## External implementation pins

| Method | Official base commit | Reproducible local adaptation |
|---|---|---|
| ACN | `2d6ce2f2c771fec5296870416844d995c23e31a2` | `baseline_patches/cn-validation-seeds.patch`; ACN+TIFO is isolated in `baseline_patches/acn-tifo-composition.patch` |
| WDAN | `f01994ada4980729eb6af14c35778f480f9c0c47` | `baseline_patches/wdan-matched-runner.patch` |
| FilterNet (positioning only) | `cdb321c4e338e0c07b45cee92f54b3c5bd5a809e` | No result from this repository is promoted into the main table |

Patch SHA-256 values are recorded in
`project_management/experiments/system/baseline_patches/README.md`; the pinned
repositories are not treated as clean source trees after execution because they
contain generated checkpoints/results and applied reproducibility patches.

## Recent plug-in baseline selection

| Method | Dataset scope | Selection source | New candidates evaluated | Final test |
|---|---|---|---:|---|
| ACN | ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Weather | Official dataset-specific temperatures encoded in `build_plugin_h96_matrix.py` | 0 | Three frozen seeds |
| ACN | Traffic | Validation-only temperature gate `{0.05, 0.1, 0.2, 0.5}` | 4 | Winner `0.1`, three frozen seeds |
| WDAN | ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Weather | Official H96 iTransformer statistics-network settings encoded in `build_plugin_h96_matrix.py` | 0 | Three frozen seeds |
| WDAN | Traffic | Validation-only gate `{generic, ecl, weather, sensor_deep}` because Traffic is absent upstream | 4 | Winner `ecl`, three frozen seeds |

The baseline main matrix is
`system/plugin_baselines_h96_itransformer.json`. The corresponding bare-backbone
matrix is `system/plugin_engine_controls_h96_itransformer.json`.

## Standalone TIFO selection lineage

The counts below report validation candidates considered in the promoted H96
lineage. They are intentionally disclosed rather than described as equal to the
baseline budget.

| Dataset | Validation-only candidate lineage | Candidate count | Promoted configuration |
|---|---|---:|---|
| ETTh1 | Hermitian gate: raw/aligned reconstruction and zero-padding choices | 4 | `hermitian_aligned`, zero-pad ratio 1.0 |
| ETTh2 | Weak-cell rounds 1, 2, and 3 | 8 + 12 + 30 = 50 | historical, LR scale 0.0625, residual alpha 0.5 |
| ETTm1 | Weak-cell rounds 1 and 2 | 8 + 9 = 17 | historical, zero-pad ratio 1.5 |
| ETTm2 | Hermitian gate: raw/aligned reconstruction and zero-padding choices | 4 | `hermitian_raw`, zero-pad ratio 0.0 |
| Electricity | Final untuned-dataset gate: historical control, learning-rate/residual variants, zero padding, compact filter, and Hermitian-aligned reconstruction | 8 | `hermitian_aligned`, zero-pad ratio 1.0 |
| Traffic | Weak-cell rounds 1 and 2, low-alpha, LR, and residual gates | 8 + 8 + 4 + 6 + 5 = 31 | historical, zero-pad ratio 1.5, LR scale 0.25, residual alpha 0.5 |
| Weather | Final untuned-dataset gate: historical control, learning-rate/residual variants, zero padding, compact filter, and Hermitian-aligned reconstruction | 8 | `hermitian_aligned`, zero-pad ratio 1.0 |

The ETTh1/ETTm2 Hermitian configurations were frozen before their reported
three-seed final matrix. A later ETTm2 validation refinement and three-seed
diagnostic were run but were not used to replace the preregistered main result;
the original frozen configuration remains the reported configuration. Electricity
and Weather had received no new TIFO search in the earlier matrix. Their final
eight-candidate gates therefore included the historical setting as an explicit
control, disabled final testing for every candidate, and independently selected
the same `hermitian_aligned`, zero-pad-ratio-1.0 configuration. Only then were
the three final seeds executed.

## ACN+TIFO composition selection

For each of ETTh1, ETTm2, and Traffic, six ACN+TIFO candidates plus one ACN
control were evaluated on validation seed 2022 with final testing disabled. A
composition was promoted only if the lowest-validation-MSE candidate beat the
ACN control. All three passed that rule and were frozen for seeds 2021--2023.
The final composition improves ACN's mean MSE on all three datasets and wins
8/9 paired seeds. It is reported as a bounded normalization-complementarity
diagnostic, not a replacement for standalone TIFO and not a FilterNet result.

## Reviewer-facing interpretation

The defensible statement is:

> We did not enforce an identical hyperparameter-search budget across different
> official plug-in repositories. ACN and WDAN use their official dataset-specific
> settings wherever available; each missing Traffic configuration was selected
> from four validation-only candidates. TIFO configurations were selected through
> the disclosed validation-only candidate lineages above. We therefore do not use
> absolute cross-engine values alone to claim a plug-in effect. Instead, we report
> each plug-in against a bare backbone rerun inside the same engine and retain all
> negative cases. Earlier large-gain claims whose provenance was incomplete were
> removed.

This is stronger and more accurate than claiming equal tuning. If the final
response requires exact page/line locations, they must be generated after the
theory rewrite and final PDF are frozen.
