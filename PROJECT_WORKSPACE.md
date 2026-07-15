# KDD 2027 resubmission workspace

This workspace manages the resubmission of **TIFO: Time-Invariant Frequency
Operator for Stationarity-Aware Representation Learning in Time Series**.

## Workspace layout

| Area | Location | Git branch / remote | Purpose |
|---|---|---|---|
| Code and experiments | `/home/park/TS/FredNormer` | local `main` | Models, training code, experiment scripts, and project records |
| Paper | `/home/park/TS/FredNormer_overleaf` | `overleaf-main` tracking `overleaf/main` | LaTeX manuscript and figures synchronized with Overleaf |
| Review record | `project_management/reviews/original/` | code workspace only | Immutable source reviews and decision records |

## Safety rules

1. Never push the code workspace's `main` branch to Overleaf.
2. Pull and push Overleaf only from `/home/park/TS/FredNormer_overleaf`.
3. Keep datasets, checkpoints, logs, and generated results out of Git.
4. Preserve files under `project_management/reviews/original/` unchanged; put
   derived review trackers and response drafts in sibling directories later.

## Paper synchronization

```bash
git -C /home/park/TS/FredNormer_overleaf pull --ff-only overleaf main
git -C /home/park/TS/FredNormer_overleaf push overleaf HEAD:main
```

Overleaf project: <https://www.overleaf.com/project/6979c817055a778f22c72582>

