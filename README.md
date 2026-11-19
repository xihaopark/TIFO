# TIFO: Time-Invariant Frequency Operator

Official code for **"TIFO: Time-Invariant Frequency Operator for Stationarity-Aware Representation Learning in Time Series"** (KDD 2027).

TIFO is a plug-and-play input operator for time-series forecasting. From the
training windows it estimates, for every frequency and channel, how stable the
amplitude spectrum is (mean over standard deviation of the FFT amplitude). This
statistic initializes a set of frequency weights that are shared by the whole
dataset. Each input window is transformed to the frequency domain, reweighted,
transformed back and passed to an unchanged forecasting backbone, so stationary
components are emphasized and non-stationary ones are down-weighted.

This repository contains the TIFO operator, the backbones used in the paper, the
frozen run configurations of every reported experiment, and the per-run test
metrics we obtained.

## Repository layout

```text
run.py                         training / evaluation entry point (long-term forecasting)
utils/frequency_domain_filter.py   TIFO: dataset statistic + frequency operator
models/                        DLinear, iTransformer, PatchTST, FilterNet, TQNet, SiGMA (each with an optional TIFO input stage)
layers/official_norms.py       RevIN / SAN / FAN comparison plug-ins
layers/PluginNormalization.py  ACN comparison plug-in
configs/                       frozen run configurations (one JSON entry per run)
scripts/run_configs.py         launcher for config files
scripts/summarize_results.py   per-cell tables and seed-paired tests from per-run metrics
scripts/analysis/              analysis scripts (spectral shift, operator checks, synthetic data)
results/runs/                  our per-run test MSE/MAE for every config entry
results/summaries/             summary tables of each experiment
results/analysis/              outputs of the analysis scripts
```

## Installation

Python 3.10 and a CUDA build of PyTorch (we used PyTorch 2.11 with CUDA 12.8):

```bash
pip install -r requirements.txt
```

## Data

Download the standard long-term forecasting datasets (for example from the
[Time-Series-Library](https://github.com/thuml/Time-Series-Library) data
release) and place them as follows:

```text
dataset/
  ETT-small/{ETTh1,ETTh2,ETTm1,ETTm2}.csv
  electricity/electricity.csv
  traffic/traffic.csv
  weather/weather.csv
```

The synthetic series of the controlled experiment are generated with
`python scripts/analysis/make_synthetic.py` (written to `dataset/dataset_synthetic/`).

The ETT data use the fixed 12/4/4-month split; the other datasets use a
70/10/20 chronological split. The scaler is fitted on the training split only.

## Quick start

TIFO on iTransformer, ETTh1, horizon 96, seed 2021 (the main-table configuration):

```bash
python scripts/run_configs.py configs/main/tifo_final.json \
    --filter backbone=iTransformer dataset=ETTh1 pred_len=96 seed=2021 --execute --gpus 0
```

Without `--execute` the launcher only prints the `python run.py ...` commands.
`--filter` accepts any run field or `model_args` field. Each run writes its log
and a launch record to `experiment_records/<run_id>/`, its checkpoint to
`checkpoints/`, and prints the test MSE/MAE at the end of the log.

The matched backbone without TIFO uses `--method ori`; the ori path does not
consume random numbers for TIFO, so Ori and TIFO start from the same backbone
initialization.

### Main TIFO options

| Flag | Meaning |
|---|---|
| `--method tifo` / `ori` | with / without the TIFO input stage |
| `--tifo_variant` | `historical` (full FFT); `hermitian_raw` / `hermitian_aligned` (one-sided rFFT/iRFFT, statistic on raw or backbone-normalized windows); `hermitian_shared` (one real gain per complex coefficient, phase-preserving). The main table uses the validation-selected variant of each setting; the remaining choices are controls. |
| `--filter_dim` | hidden width of the MLPs that produce the frequency weights |
| `--tifo_dropout` | dropout inside the weight MLPs |
| `--tifo_lr_scale` | learning-rate multiplier for TIFO parameters |
| `--tifo_residual_alpha` | interpolation between identity (0) and the learned operator (1) |
| `--tifo_zero_pad_ratio` | zero padding of the FFT grid, as a fraction of the input length |
| `--tifo_score_mode` | statistic used to initialize the weights (`data` = mean/std; the other modes are controls) |

## Reproducing the experiments

Every experiment is a config file; `results/runs/` holds our metrics for the
same run IDs. All runs use seeds 2021–2023 unless stated otherwise. Model
selection uses the validation split only; the test split is evaluated once
after training.

| Config | Runs | Content |
|---|---:|---|
| `configs/main/tifo_final.json` | 168 | TIFO on DLinear and iTransformer, 7 datasets × 4 horizons × 3 seeds, validation-selected configuration per setting |
| `configs/main/acn_final.json`, `configs/main/wdan_final.json` | 168 each | ACN and WDAN in the same runner, same settings and seeds |
| `configs/shared_config/m2_protocol.json` | 840 | Ori, RevIN, SAN, FAN and SAN+TIFO under the backbone configuration of each TIFO setting |
| `configs/recent_backbones/m4_search.json` → `m4_final.json` | 672 → 252 | TIFO on SiGMA, TQNet and FilterNet with their official hyper-parameters: validation-only search (seed 2022), then frozen winners on seeds 2021–2023 |
| `configs/recent_backbones/m3_*.json` | 268 / 216 / 192 | SiGMA / FilterNet / TQNet, Ori vs +TIFO with a fixed TIFO setting |
| `configs/patchtst/patchtst_coverage.json` | 162 | PatchTST, Ori vs TIFO |
| `configs/analysis/*.json` | — | attribution controls, permuted/constant statistics, free learnable filter, alternative statistics, synthetic data, shortened training, robust statistic |

The full main comparison (TIFO, Ori, RevIN, SAN, FAN, ACN, WDAN) can be
recomputed from the released metrics with

```bash
python scripts/summarize_results.py results/runs/main/*.csv results/runs/shared_config/m2_protocol.csv
```

and from your own runs with `--from-records configs/main/tifo_final.json ...`.

Notes:

- `configs/main/wdan_final.json` needs the official WDAN code
  (`git clone https://github.com/MonBG/WDAN.git third_party/WDAN-official`, commit `f01994a`); only its `nns/models/WDAN.py` module is imported.
- Runs on different GPUs or PyTorch versions do not reproduce our numbers bit for bit; expect small seed-level differences.
- The validation-only search configs (`m4_search`, `m3_dev_lr`, `analysis/v2_dev`) have no test metrics by design; their selections are in `results/summaries/*selection.json`.

### Analysis scripts

`scripts/analysis/` reads the launch records and checkpoints written by
`run_configs.py`:

- `x6_shift_eval.py`: evaluates trained checkpoints under a controlled high-frequency spectral shift (`--spectral_shift_strength`).
- `spectral_shift_metrics.py`: train/test spectral distance per frequency.
- `energy_stratified_gain.py`: relation between the TIFO statistic, spectral energy and the learned gains.
- `r1_operator_check.py`: exact linear map of each trained TIFO operator (sign, conditioning, symmetry).
- `sigma_floor_check.py`: magnitude of the amplitude standard deviation relative to the numerical floor.
- `make_synthetic.py`: synthetic series with known stationary and non-stationary frequency bands.

## Acknowledgements

The data pipeline and the DLinear / iTransformer / PatchTST implementations
build on [Time-Series-Library](https://github.com/thuml/Time-Series-Library).
FilterNet, TQNet, SiGMA and the RevIN/SAN/FAN modules are adapted from their
official implementations; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Citation

```bibtex
@inproceedings{piao2027tifo,
  title     = {TIFO: Time-Invariant Frequency Operator for Stationarity-Aware Representation Learning in Time Series},
  author    = {Piao, Xihao and Chen, Zheng and Zhu, Lingwei and Matsubara, Yasuko and Sakurai, Yasushi},
  booktitle = {Proceedings of the 33rd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)},
  year      = {2027}
}
```

## License

MIT, see [LICENSE](LICENSE). Adapted third-party code keeps its original license.
