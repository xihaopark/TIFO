# Experiment result summary

| Dataset | Horizon | Method | Seeds | MSE mean ± std | MAE mean ± std |
|---|---:|---|---:|---:|---:|
| ETTh1 | 96 | iTransformer+ORI | 3 | 0.393243 ± 0.001120 | 0.408597 ± 0.000726 |
| ETTh1 | 96 | iTransformer+TIFO[historical] | 3 | 0.390588 ± 0.001327 | 0.407667 ± 0.001099 |
| ETTh2 | 96 | iTransformer+ORI | 3 | 0.299868 ± 0.000291 | 0.349603 ± 0.000653 |
| ETTh2 | 96 | iTransformer+TIFO[historical] | 3 | 0.301797 ± 0.001777 | 0.349544 ± 0.000887 |
| ETTm1 | 96 | iTransformer+ORI | 3 | 0.341437 ± 0.000559 | 0.376441 ± 0.000454 |
| ETTm1 | 96 | iTransformer+TIFO[historical] | 3 | 0.342039 ± 0.001634 | 0.376050 ± 0.000708 |
| ETTm2 | 96 | TFPS | 3 | 0.172818 ± 0.001181 | 0.255664 ± 0.000283 |
| ETTm2 | 96 | TimeEmb | 3 | 0.164518 ± 0.000304 | 0.243307 ± 0.000275 |
| ETTm2 | 96 | iTransformer+ORI | 3 | 0.184665 ± 0.000829 | 0.269641 ± 0.002345 |
| ETTm2 | 96 | iTransformer+TIFO[historical] | 3 | 0.181195 ± 0.000742 | 0.265726 ± 0.001004 |
| ETTm2 | 96 | iTransformer+TIFO[identity_unregularized] | 3 | 0.187039 ± 0.001759 | 0.272709 ± 0.001624 |
| Electricity | 96 | iTransformer+ORI | 3 | 0.148206 ± 0.000076 | 0.239818 ± 0.000221 |
| Electricity | 96 | iTransformer+TIFO[historical] | 3 | 0.143338 ± 0.000477 | 0.236955 ± 0.000504 |
| Traffic | 96 | iTransformer+ORI | 3 | 0.392655 ± 0.000541 | 0.268414 ± 0.000096 |
| Traffic | 96 | iTransformer+TIFO[historical] | 3 | 0.493411 ± 0.003245 | 0.349921 ± 0.003068 |
| Weather | 96 | iTransformer+ORI | 3 | 0.174723 ± 0.001110 | 0.214277 ± 0.001244 |
| Weather | 96 | iTransformer+TIFO[historical] | 3 | 0.168588 ± 0.001269 | 0.212248 ± 0.001234 |

## Paired effect: ETTh1/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.002655 ± 0.000413; wins: 3/3
- Relative MSE reduction: 0.675247 ± 0.105907%
- MAE delta (TIFO - Ori): -0.000930 ± 0.000447

## Paired effect: ETTh2/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.001929 ± 0.001834; wins: 0/3
- Relative MSE reduction: -0.643463 ± 0.611508%
- MAE delta (TIFO - Ori): -0.000059 ± 0.001516

## Paired effect: ETTm1/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.000602 ± 0.001196; wins: 1/3
- Relative MSE reduction: -0.176077 ± 0.350095%
- MAE delta (TIFO - Ori): -0.000391 ± 0.000267

## Paired effect: ETTm2/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.003471 ± 0.001314; wins: 3/3
- Relative MSE reduction: 1.877667 ± 0.704346%
- MAE delta (TIFO - Ori): -0.003915 ± 0.002773

## Paired effect: ETTm2/H96/iTransformer+TIFO[identity_unregularized]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.002373 ± 0.002579; wins: 1/3
- Relative MSE reduction: -1.289424 ± 1.398879%
- MAE delta (TIFO - Ori): 0.003068 ± 0.003942

## Paired effect: Electricity/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.004868 ± 0.000549; wins: 3/3
- Relative MSE reduction: 3.284575 ± 0.368793%
- MAE delta (TIFO - Ori): -0.002863 ± 0.000713

## Paired effect: Traffic/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): 0.100756 ± 0.003088; wins: 0/3
- Relative MSE reduction: -25.660144 ± 0.780117%
- MAE delta (TIFO - Ori): 0.081507 ± 0.003052

## Paired effect: Weather/H96/iTransformer+TIFO[historical]

Matched seeds: 2021, 2022, 2023

- MSE delta (TIFO - Ori): -0.006135 ± 0.002368; wins: 3/3
- Relative MSE reduction: 3.505605 ± 1.332940%
- MAE delta (TIFO - Ori): -0.002029 ± 0.002469
