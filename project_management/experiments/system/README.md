# Unified experiment launcher

This layer launches native TIFO/Ori and pinned external baselines from one
canonical JSON matrix. It does not merge upstream source trees.

## Engines

| Engine | Entrypoint | Role |
|---|---|---|
| `native` | `/home/park/TS/FredNormer/run.py` | matched Ori/TIFO backbone experiments |
| `timeemb` | pinned TimeEmb checkout | selected NeurIPS 2025 model baseline |
| `tfps` | pinned TFPS checkout | selected NeurIPS 2025 distribution-shift baseline |
| `acn` | pinned Channel Normalization checkout | ICML 2025 adaptive channel-normalization plug-in |
| `wdan` | pinned WDAN checkout | 2025 wavelet adaptive-normalization plug-in |

The launcher defaults to dry-run. It validates unique run IDs and data paths,
preflights each unique entrypoint, prints the exact commands, and only starts
jobs with `--execute`.

The canonical Blackwell-capable interpreter is:

```text
/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python
```

It provides PyTorch 2.11.0+cu128 with `sm_120` kernels. The previous default
PyTorch 2.5.0+cu124 environment imports successfully but cannot execute kernels
on the RTX PRO 6000 Blackwell GPUs. The launcher performs a real CUDA backward
probe so an import-only false positive cannot start a matrix.

TimeEmb and TFPS require the recorded patches under `baseline_patches/`. They
remove per-epoch test evaluation while retaining validation early stopping and
replace the NumPy-2-incompatible `np.Inf` spelling. The official upstream
commits remain pinned and the patches are separately inspectable.

```bash
python -m pip install -r \
  project_management/experiments/system/requirements-baselines.txt
```

```bash
python project_management/experiments/system/run_matrix.py \
  project_management/experiments/system/gate_ettm2_96.json

/mnt/data1/park/Time\ Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python \
  project_management/experiments/system/run_matrix.py \
  project_management/experiments/system/gate_ettm2_96.json \
  --execute --gpus 0,1,2,3,4,5,6,7 --max-parallel 8
```

Jobs are serialized per physical GPU. Use `--only run_id_a,run_id_b` to rerun
a selected subset without editing the frozen matrix. Use `--skip-completed` to
resume a matrix without overwriting completed evidence records.

Use `--skip-entrypoint-check` only for inspecting commands on a machine where
the training environment has intentionally not been installed.

Executed runs write launch records and logs under ignored
`experiment_records/<run_id>/`. Native TIFO/Ori results additionally write
`run_manifest.json` beside `metrics.npy`, containing the full CLI arguments,
data SHA-256, source revision, dirty-state snapshot and metrics.

Every engine launch record also captures the orchestrator and engine Git HEAD,
dirty status, tracked-diff hash and status entries. The minimal recent-baseline
extension is `baseline_etth1_96.json`: TimeEmb and TFPS on ETTh1/H96 with seeds
2021/2022/2023, complementing the completed ETTm2/H96 gate.

The paper-facing plug-in matrix is `plugin_baselines_h96_itransformer.json`
(protocol v2): ACN and WDAN on all seven datasets at H96 and seeds
2021/2022/2023. ACN uses the official H96 temperatures; Traffic temperature
0.1 is frozen by `tune_acn_traffic_temperature.json`. WDAN uses the official
dataset-specific H96 statistics-network settings; Traffic uses the ECL-style
candidate frozen by `tune_wdan_traffic_config.json`. The earlier v1 launch
records used generic defaults and are retained as discarded audit evidence,
not paper results.

## Fairness boundary

- Dataset split, features, lengths, horizon, seed set and metric definitions are
  task fields and must match.
- Model-specific architecture parameters may differ but must be recorded.
- Validation selection and maximum training budget must be declared before an
  evidence run.
- Native training does not evaluate the test split during epoch selection.
  TimeEmb and TFPS now use recorded validation-only patches; test is evaluated
  once after the best validation checkpoint is restored.
- ACN and WDAN tuning gates expose the same validation-only behavior. Their
  final v2 matrix evaluates the test split once after the configuration is frozen.
- Dry-run success is not experiment evidence.
- The initial matrix is a representative gate, not the final 7 × 4 sweep.

## Checks and aggregation

```bash
/mnt/data1/park/Time\ Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python \
  project_management/experiments/system/test_native_gate.py

/mnt/data1/park/Time\ Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python \
  project_management/experiments/system/collect_results.py \
  --protocol kdd_resubmit_gate_v1,kdd_resubmit_tifo_historical_v2 \
  --name kdd_resubmit_ettm2_h96_gate
```

The native test verifies full-train-set statistics, real-valued output, finite
gradients, Ori/TIFO backbone initialization parity and a real ETTm2 optimizer
step. It also checks the server-25 candidate controls: `tifo_residual_alpha`
(the imported alpha-shrinkage design) and `tifo_zero_pad_ratio` (a corrected
zero-padding design whose statistics and learned weights use the same padded
FFT grid). Both options preserve the historical default at `1.0` and `0.0`,
respectively. The collector parses only completed final-test records and reports both
per-method seed statistics and matched TIFO-minus-Ori deltas.

## Controlled spectral-shift stress test

The frozen stress test coherently scales the upper half of non-DC rFFT bins
over each combined input/future window. It does not retrain or select a model,
and the zero-strength condition must reproduce the promoted main-table metric.

```bash
python project_management/experiments/system/run_spectral_shift_stress.py \
  --gpu 0 --datasets ETTh1 Traffic --methods ori tifo \
  --seeds 2021 2022 2023 --strengths 0.0 0.25 0.5 1.0

python project_management/experiments/system/collect_spectral_shift_stress.py
```

Evaluation outputs receive an `evaluation_tag`, so stress-test metrics cannot
overwrite the original frozen result directory. The paper-facing aggregate is
`project_management/experiments/results/spectral_shift_stress.md`.
