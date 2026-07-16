# Pinned third-party baseline sources

These repositories are reproducible source references. They are intentionally
ignored by the parent repository; use `bootstrap_baselines.sh` to recreate the
exact checkouts. Do not cite or import results merely because code is present.

| Local directory | Upstream | Pinned commit | License | Intended role | Evidence status |
|---|---|---|---|---|---|
| `third_party/Time-Series-Library` | <https://github.com/thuml/Time-Series-Library> | `4e938a1767106324dd753b2a44832bf870a0252e` | MIT | Canonical loader/model implementation pool and protocol reference | source_only |
| `third_party/FAN-official` | <https://github.com/icannotnamemyself/FAN> | `838e1b002aa0e8cbc3889dfb69967c40c0c15761` | Apache-2.0 | Official FAN, SAN and RevIN implementations | source_only |
| `third_party/FilterNet-official` | <https://github.com/aikunyi/FilterNet> | `cdb321c4e338e0c07b45cee92f54b3c5bd5a809e` | Apache-2.0 | Closest-method code inspection and matched baseline candidate | source_only |

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

## Integration states

`source_only` → `adapter_implemented` → `smoke_tested` → `matched_gate_passed` →
`full_matrix_verified`.

No source above has progressed beyond `source_only` yet.
