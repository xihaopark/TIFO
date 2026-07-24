# KDD resubmission: full plug-in main-table contract

Status: revised active experiment contract, 2026-07-24.

## Reviewer-facing scope

The revised main result is one `table*` with two backbone panels:

1. Preserve the complete submitted-paper result surface, including its
   original-backbone, TIFO, TIFO*, RevIN, SAN, and FAN results.
2. Add ACN and WDAN on iTransformer without deleting or replacing submitted
   results.
3. Add ACN and WDAN on DLinear through explicit native adapters. ACN operates
   on DLinear's normalized channel-by-time representation; WDAN wraps the
   DLinear input and output with its learned normalization/de-normalization.

Rows cover ETTh1, ETTh2, ETTm1, ETTm2, Electricity, Traffic, and Weather at
prediction horizons 96, 192, 336, and 720. Each cell reports MSE/MAE. TIFO is
always standalone; compositions such as TIFO+SAN, TIFO+ACN, and TIFO+WDAN are
excluded from the main comparison.

## Frozen baseline sources

- RevIN, SAN, FAN: reuse the detailed matched-backbone values already present
  in the submitted manuscript. These methods were run in the original project
  environment on both DLinear and iTransformer.
- ACN, WDAN at iTransformer/H96: reuse the completed local three-seed official-
  engine runs. Do not rerun them.
- ACN, WDAN at other horizons: run validation-selected local matrices,
  including all Traffic horizons, so the final table has no source-protocol
  symbols or missing cells.
- ACN, WDAN on DLinear: run eight-candidate validation-only gates per cell and
  freeze one configuration for seeds 2021--2023.
- Never select among duplicate baseline runs using final-test performance.

## TIFO selection and final testing

- Tune independently for every dataset-backbone-horizon cell.
- Candidate selection uses seed 2022 validation MSE only.
- Every tuning run sets `skip_final_test=true`.
- Freeze one configuration per cell before the final test.
- Final evidence uses seeds 2021, 2022, and 2023 and reports the mean MSE/MAE.
- If a frozen final TIFO cell is weaker than a baseline, open a new, local
  validation-only refinement around that cell. Do not use final-test values to
  choose the refinement winner.

## Backbone protocols

- iTransformer: input length 96 for all datasets.
- DLinear: preserve the original scripts so the frozen RevIN/SAN/FAN numbers
  remain comparable: input length 336 on ETTh1, ETTh2, and ETTm2; input length
  96 on ETTm1, Electricity, Traffic, and Weather.
- Prediction horizons are 96, 192, 336, and 720 for both panels.

## Manuscript change boundary

Retain the original result tables and extend them; do not replace the author's
submitted result surface with a narrower regenerated table. Remove per-cell
source symbols once every new-baseline cell is locally complete. Keep the
frequency-distribution distance table, spectral figures, ablations, and
efficiency tables unchanged unless a consistency error is discovered.
