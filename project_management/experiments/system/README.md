# Unified experiment launcher

This layer launches native TIFO/Ori and pinned external baselines from one
canonical JSON matrix. It does not merge upstream source trees.

## Engines

| Engine | Entrypoint | Role |
|---|---|---|
| `native` | `/home/park/TS/FredNormer/run.py` | matched Ori/TIFO backbone experiments |
| `timeemb` | pinned TimeEmb checkout | selected NeurIPS 2025 model baseline |
| `tfps` | pinned TFPS checkout | selected NeurIPS 2025 distribution-shift baseline |

The launcher defaults to dry-run. It validates unique run IDs and data paths,
preflights each unique entrypoint, prints the exact commands, and only starts
jobs with `--execute`.

The two upstream repositories declare old, minimal dependency lists. The
current shared environment uses PyTorch 2.5; compatibility must therefore pass
the representative gate before any external result is promoted. TFPS also
imports `thop` without declaring it; the workspace environment pins
`thop==0.1.1.post2209072238` for that import.

```bash
python -m pip install -r \
  project_management/experiments/system/requirements-baselines.txt
```

```bash
python project_management/experiments/system/run_matrix.py \
  project_management/experiments/system/gate_ettm2_96.json

python project_management/experiments/system/run_matrix.py \
  project_management/experiments/system/gate_ettm2_96.json --execute
```

Use `--skip-entrypoint-check` only for inspecting commands on a machine where
the training environment has intentionally not been installed.

Executed runs write launch records and logs under ignored
`experiment_records/<run_id>/`. Native TIFO/Ori results additionally write
`run_manifest.json` beside `metrics.npy`, containing the full CLI arguments,
data SHA-256, source revision, dirty-state snapshot and metrics.

## Fairness boundary

- Dataset split, features, lengths, horizon, seed set and metric definitions are
  task fields and must match.
- Model-specific architecture parameters may differ but must be recorded.
- Validation selection and maximum training budget must be declared before an
  evidence run.
- Native training does not evaluate the test split during epoch selection.
  TimeEmb and TFPS upstream trainers currently do; their direct launcher rows
  are pipeline gates only until a reproducible test-isolation adapter is
  implemented without silently modifying the pinned sources.
- Dry-run success is not experiment evidence.
- The initial matrix is a representative gate, not the final 7 × 4 sweep.
