# TIFO versus ACN H96 ranking robustness audit

Date: 2026-07-22

## Overall assessment: Share with caveats

TIFO's seven-dataset macro MSE is 0.272629, compared with 0.275660 for ACN, a descriptive relative lead of 1.10%. The lead holds for 3/3 seed-indexed macro averages. It is not a universal dataset-wise advantage or a controlled cross-engine significance result.

## Dataset contributions

Positive ACN-TIFO values favor TIFO.

| Dataset | ACN MSE | TIFO MSE | ACN - TIFO |
|---|---:|---:|---:|
| ETTh1 | 0.388795 | 0.388955 | -0.000160 |
| ETTh2 | 0.301861 | 0.297241 | +0.004620 |
| ETTm1 | 0.334431 | 0.339394 | -0.004963 |
| ETTm2 | 0.180988 | 0.181120 | -0.000132 |
| Electricity | 0.134837 | 0.140968 | -0.006131 |
| Traffic | 0.427060 | 0.396656 | +0.030404 |
| Weather | 0.161651 | 0.164069 | -0.002418 |

Traffic supplies 86.8% of the positive contributions to the absolute macro gap. This concentration must remain visible when the macro ranking is interpreted.

## Seed-indexed macro check

| Seed | ACN macro MSE | TIFO macro MSE | ACN - TIFO |
|---:|---:|---:|---:|
| 2021 | 0.275336 | 0.273355 | +0.001980 |
| 2022 | 0.276193 | 0.272023 | +0.004171 |
| 2023 | 0.275453 | 0.272509 | +0.002944 |

## Leave-one-dataset-out check

| Omitted dataset | ACN macro MSE | TIFO macro MSE | ACN - TIFO |
|---|---:|---:|---:|
| ETTh1 | 0.256805 | 0.253241 | +0.003563 |
| ETTh2 | 0.271294 | 0.268527 | +0.002767 |
| ETTm1 | 0.265865 | 0.261501 | +0.004364 |
| ETTm2 | 0.291439 | 0.287881 | +0.003559 |
| Electricity | 0.299131 | 0.294572 | +0.004559 |
| Traffic | 0.250427 | 0.251958 | -0.001531 |
| Weather | 0.294662 | 0.290722 | +0.003940 |

TIFO remains ahead in 6/7 leave-one-dataset-out summaries; omitting Traffic reverses the ordering.

## Required reviewer-facing caveats

- State that TIFO has the lowest observed seven-dataset macro-average MSE, not that it is universally or significantly superior to ACN.
- Keep the within-engine paired-effect table as the causal plug-in comparison; absolute ACN and TIFO values come from different official engines.
- Preserve the dataset rows and the negative Traffic paired case rather than showing only the aggregate ranking.
- The final Electricity/Weather configuration was selected from eight validation-only candidates per dataset before the three final seeds were run.
