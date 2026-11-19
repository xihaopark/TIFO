# Third-party code

| Files | Source | License |
|---|---|---|
| `run.py`, `exp/`, `data_provider/`, `layers/` (Embed, SelfAttention_Family, Transformer_EncDec, Autoformer_EncDec, StandardNorm), `utils/` (metrics, tools, timefeatures, masking, losses, augmentation, dtw), `models/DLinear.py`, `models/iTransformer.py`, `models/PatchTST.py` | [Time-Series-Library](https://github.com/thuml/Time-Series-Library) (commit 4e938a1), modified | MIT, Copyright (c) 2021 THUML @ Tsinghua University |
| `layers/official_norms.py` (RevIN, SAN, FAN) | [FAN](https://github.com/icannotnamemyself/FAN) (commit 838e1b0) | Apache-2.0 |
| `models/FilterNet.py` | [FilterNet](https://github.com/aikunyi/FilterNet) (commit cdb321c) | Apache-2.0 |
| `models/TQNet.py` | [TQNet](https://github.com/ACAT-SCUT/TQNet) (commit 15e19cb) | Apache-2.0 |
| `models/SiGMA.py` | [SiGMA](https://github.com/cheonwoolee/SiGMA) (commit b4ac7c9) | MIT |

Each adapted file states its origin and the changes made in its header.
`layers/PluginNormalization.py` is our re-implementation of adaptive channel
normalization (ACN, [CN](https://github.com/seunghan96/CN)) for the matched
comparison. WDAN is not redistributed; `utils/wdan_adapter.py` imports it from
an official checkout of [WDAN](https://github.com/MonBG/WDAN).

Copies of the Apache-2.0 license: https://www.apache.org/licenses/LICENSE-2.0
