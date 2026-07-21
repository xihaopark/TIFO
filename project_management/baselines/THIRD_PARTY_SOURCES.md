# Pinned third-party baseline sources

These repositories are reproducible source references. They are intentionally
ignored by the parent repository; use `bootstrap_baselines.sh` to recreate the
exact checkouts. Do not cite or import results merely because code is present.

| Local directory | Upstream | Pinned commit | License | Intended role | Evidence status |
|---|---|---|---|---|---|
| `third_party/Time-Series-Library` | <https://github.com/thuml/Time-Series-Library> | `4e938a1767106324dd753b2a44832bf870a0252e` | MIT | Canonical loader/model implementation pool and protocol reference | source_only |
| `third_party/FAN-official` | <https://github.com/icannotnamemyself/FAN> | `838e1b002aa0e8cbc3889dfb69967c40c0c15761` | Apache-2.0 | Official FAN, SAN and RevIN implementations | source_only |
| `third_party/FilterNet-official` | <https://github.com/aikunyi/FilterNet> | `cdb321c4e338e0c07b45cee92f54b3c5bd5a809e` | Apache-2.0 | Closest-method code inspection and matched baseline candidate | source_only |
| `third_party/DDN-official` | <https://github.com/Hank0626/DDN> | `72b8d9c595ca81e70500919689f8715ed133e6d2` | MIT | NeurIPS 2024 direct normalization backup | source_only |
| `third_party/PIR-official` | <https://github.com/icantnamemyself/PIR> | `fc372bb02090da887d4a20b614a6cfecbfd813d0` | MIT | NeurIPS 2025 post-hoc robustness backup | source_only |
| `third_party/TimeEmb-official` | <https://github.com/showmeon/TimeEmb> | `9adf3fba801b34642e7191b45e08aff224b26e67` | no license file found | Selected NeurIPS 2025 recent non-stationary forecasting baseline | smoke_tested; license_review_required |
| `third_party/TFPS-official` | <https://github.com/syrGitHub/TFPS> | `83a11827e27e6617e8c8a8771f0a1dd7e10976a5` | no license file found | Selected NeurIPS 2025 patch-level distribution-shift baseline | smoke_tested; license_review_required |
| `third_party/CN-official` | <https://github.com/seunghan96/CN> | `2d6ce2f2c771fec5296870416844d995c23e31a2` | no license file found | ICML 2025 Channel Normalization / ACN plug-in baseline | source_only; license_review_required |
| `third_party/WDAN-official` | <https://github.com/MonBG/WDAN> | `f01994ada4980729eb6af14c35778f480f9c0c47` | no license file found | 2025 wavelet-based normalization plug-in baseline | source_only; license_review_required |

## Use policy

- Preserve each upstream license and attribution when copying code.
- Prefer adapters around pinned upstream code to unrecorded copy-and-edit forks.
- Freeze the TIFO task contract first; upstream defaults are not a fair
  comparison protocol.
- Record every adaptation in a manifest with original file, local file and
  semantic change.
- The existing `/home/park/TS/FAN-main` is not the authority for new results:
  it is not a git checkout and differs from the pinned official FAN source.
- FAN documentation warns that its legacy default scaling can use all splits;
  enforce train-only scaler fitting for matched KDD experiments.
- TSLib remains useful as an implementation source, but its current README
  cautions that older benchmark collections may no longer represent current
  state of the art. Baseline selection still requires a paper-level rationale.
- TimeEmb and TFPS do not currently contain a repository license file. They may
  be executed as pinned upstream checkouts for research comparison, but their
  source must not be copied into this repository without permission review.
- CN and WDAN also lack repository license files at the pinned revisions. Keep
  their source as ignored, pinned upstream checkouts and implement any required
  fairness changes as separately recorded patches rather than copied modules.

## Integration states

`source_only` → `adapter_implemented` → `smoke_tested` → `matched_gate_passed` →
`full_matrix_verified`.

TimeEmb and TFPS have passed import, argument-parser and CPU forward smoke tests
in the current shared environment. This does not constitute matched experiment
evidence; both remain below `matched_gate_passed`. Both official training loops
evaluate test loss each epoch. Their values must not be promoted until a
recorded adapter removes that evaluation and leaves selection validation-only.
