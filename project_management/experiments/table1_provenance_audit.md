# Main Table 1 provenance audit

Updated: 2026-07-16

Manuscript table: `sample-sigconf.tex`, label `table: 1st_results`

Local source: mean of the four `base` `metrics.npy` files for each
dataset/backbone, using horizons 96/192/336/720

The manuscript describes these values as averages over four horizons and also
prints a `±` value. The current local base inventory has one result per horizon,
not multiple seeds per horizon. Therefore this audit compares only the central
TIFO averages; it cannot reconstruct or validate the manuscript uncertainty.

## TIFO MSE central values

| Dataset | Backbone | Paper | Local four-horizon mean | Local − paper | Rounded match | Assessment |
|---|---|---:|---:|---:|---|---|
| ETTh1 | PatchTST | 0.438 | 0.446166 | +0.008166 | no | provenance missing |
| ETTh1 | iTransformer | 0.445 | 0.454555 | +0.009555 | no | provenance missing |
| ETTh2 | PatchTST | 0.379 | 0.385751 | +0.006751 | no | provenance missing |
| ETTh2 | iTransformer | 0.376 | 0.384541 | +0.008541 | no | provenance missing |
| ETTm1 | PatchTST | 0.390 | 0.388556 | -0.001444 | no at 3 decimals | near, still unverified |
| ETTm1 | iTransformer | 0.396 | 0.408323 | +0.012323 | no | provenance missing |
| ETTm2 | PatchTST | 0.280 | 0.280411 | +0.000411 | yes | central value only |
| ETTm2 | iTransformer | 0.283 | 0.290059 | +0.007059 | no | headline provenance missing |
| Electricity | PatchTST | 0.197 | 0.213463 | +0.016463 | no | provenance missing |
| Electricity | iTransformer | 0.169 | 0.177850 | +0.008850 | no | provenance missing |
| Traffic | PatchTST | 0.427 | 0.532318 | +0.105318 | no | critical mismatch |
| Traffic | iTransformer | 0.424 | 0.432910 | +0.008910 | no | provenance missing |
| Weather | PatchTST | 0.251 | 0.257013 | +0.006013 | no | provenance missing |
| Weather | iTransformer | 0.246 | 0.255125 | +0.009125 | no | provenance missing |

## Explicit seed coverage actually present

The 18 `r1stat` results form six complete 3-seed cells:

| Dataset | Horizon | Backbone | Seeds | Mean MSE | Population std MSE |
|---|---:|---|---|---:|---:|
| ETTh2 | 96 | PatchTST | 2021/2022/2023 | 0.301292 | 0.002883 |
| ETTh2 | 96 | iTransformer | 2021/2022/2023 | 0.299801 | 0.003201 |
| ETTh2 | 336 | PatchTST | 2021/2022/2023 | 0.427757 | 0.005734 |
| ETTh2 | 336 | iTransformer | 2021/2022/2023 | 0.420365 | 0.002716 |
| ETTm2 | 192 | PatchTST | 2021/2022/2023 | 0.247636 | 0.001144 |
| ETTm2 | 192 | iTransformer | 2021/2022/2023 | 0.247011 | 0.001157 |

These cells do not provide full multi-seed coverage for the seven dataset-level
averages in Table 1. They should be preserved as historical evidence, but not
used to infer uncertainty for unrun horizons or datasets.

## Naming anomalies

The inventory audit detects nine settings where the advertised length in the
model ID disagrees with the effective `_sl..._pl...` fields. Eight are DLinear
ETTh2/ETTm2 runs advertised with `seq_len=96` but executed with `_sl336`; one is
a Weather PatchTST result advertised as horizon 720 but executed with `_pl96`.
Metrics must be keyed by effective config fields, never by model ID alone.

Run the read-only audit with:

```bash
python project_management/scripts/audit_result_inventory.py --format summary
python project_management/scripts/audit_result_inventory.py --format csv
```

## Decision

Table 1 is `needs_experiment`. Preserve the manuscript values as historical
claims while auditing, but do not carry them into the clean resubmission until
each value is regenerated from a frozen protocol and a complete seed ledger.
