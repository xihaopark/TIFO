# KDD resubmission: full plug-in main-table contract

Status: active experiment contract, 2026-07-23.

## Reviewer-facing scope

The revised main result is one `table*` with two backbone panels:

1. iTransformer: TIFO, RevIN, SAN, FAN, ACN, and WDAN.
2. DLinear: TIFO, RevIN, SAN, and FAN. ACN/WDAN cells are included only when
   their source paper or official implementation provides a compatible DLinear
   result; otherwise they are shown as unavailable rather than inferred.

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
- ACN, WDAN at other horizons: prefer values explicitly reported by the source
  papers under iTransformer, labeled as reported rather than local. Missing or
  protocol-incompatible cells remain unavailable.
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

Replace the incorrect recent-baseline composition table and its accompanying
claims with the full standalone plug-in table. Keep the frequency-distribution
distance table, spectral figures, ablations, and efficiency tables unchanged
unless a consistency error is discovered.
