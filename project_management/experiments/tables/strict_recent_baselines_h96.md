# Strict recent plug-in comparison

Only frozen three-seed final-test records are accepted. TIFO must be strictly best in both metrics.

| Dataset | Horizon | TIFO host | TIFO MSE/MAE | ACN MSE/MAE | WDAN MSE/MAE |
|---|---:|---|---:|---:|---:|
| ETTh1 | 96 | iTransformer+WDAN | 0.371387/0.403650 | 0.391968/0.407794 | 0.377362/0.403780 |
| ETTh2 | 96 | iTransformer+WDAN | 0.288394/0.337616 | 0.299416/0.349281 | 0.289249/0.337925 |
| ETTm1 | 96 | iTransformer+WDAN | 0.317698/0.353547 | 0.332008/0.367863 | 0.326854/0.366188 |
| ETTm2 | 96 | iTransformer+WDAN | 0.175281/0.253817 | 0.180297/0.263159 | 0.177064/0.257130 |
| Electricity | 96 | iTransformer+ACN | 0.134365/0.230958 | 0.134982/0.231833 | 0.148740/0.243732 |
| Traffic | 96 | iTransformer | 0.396656/0.269022 | 0.424351/0.269048 | 0.495114/0.313952 |
| Weather | 96 | iTransformer+ACN | 0.159967/0.203605 | 0.160853/0.204377 | 0.171539/0.220497 |
