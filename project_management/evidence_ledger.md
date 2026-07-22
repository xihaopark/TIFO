# KDD resubmit evidence ledger

Updated: 2026-07-22

Status: `main_experiment_core_complete; broader_scientific_coverage_open`

This ledger is the cross-workspace link from reviewer concern to planned action,
experiment, manuscript target and inspectable evidence. `Planned` means neither
the experiment nor the manuscript response has been completed.

| Ledger ID | Concern routes / atomic comments | Action | Experiment or audit ID | Paper target | Current evidence | Readiness |
|---|---|---|---|---|---|---|
| EL-TH-01 | TH-1; PC.1, R1.1, R5.3 | Preserve the author-frozen theory; audit code/method consistency and flag any contradiction for explicit author decision. | AUDIT-THEORY-CODE-01 | Sec. 3.2 `sec:Theoretical Analysis`; method equations | Historical checkpoint replay identifies the exact result-producing raw-FFT, two-MLP, input-only operator; prediction inverse filtering is disproved by saved predictions. | frozen_code_path_verified |
| EL-TH-02 | TH-2; R1.2, R3.1 | Define mu/sigma, assumptions, failure cases and compare alternative stability scores. | EXP-METRIC-ETTH1-01 | Sec. 3.1; Appendix “Ablation Study on Stationarity Metrics” | mu/sigma implementation exists; table provenance missing | needs_experiment |
| EL-TH-03 | TH-3; R2.5, R3.3 | Restrict invariance to the represented training distribution and state OOD limits. | EXP-SUPPORT-SHIFT-01 | Sec. 2.3, theory assumptions, limitations/conclusion | A deterministic three-seed stress test coherently scales the upper half of non-DC rFFT bins over each input/future window. From strength 0 to 1, TIFO's relative effect improves from +1.09% to +1.97% on ETTh1 and from -1.02% to -0.51% on Traffic. This supports bounded high-frequency-shift robustness, not arbitrary OOD invariance. | controlled_shift_verified_theory_wording_open |
| EL-MT-01 | MT-1; PC.2, R1.3, R5.1 | Build exact comparison with RevIN/SAN/FAN/FilterNet and define complementarity. | AUDIT-CLOSEST-01; EXP-FILTERNET-01 | Background Sec. 2.2; Related Works; experiment settings | official sources pinned in `baselines/` | needs_experiment |
| EL-MT-02 | MT-2; R4.1, R4.2 | Make Figure 1, tensor dimensions, equations, algorithm and code describe one operator. | AUDIT-METHOD-MAP-01; EXP-HERMITIAN-01 | Sec. 3.1; `fig:model`; Algorithm 1 | The historical path is preserved; new Hermitian variants use rFFT/iRFFT, reconstruct real sequences without discarding an imaginary residual, and optionally compute statistics after the same per-window normalization seen by the backbone. GPU correctness tests and three-seed ETTh1/ETTm2 finals are complete. The current paper figure and shape text still describe a different decomposition. | implementation_verified_paper_open |
| EL-MT-03 | MT-3; R2.3 | Define TIFO+SAN composition/order and test whether it is additive; otherwise remove TIFO*. | EXP-COMPOSE-01 | Table `results of other methods`; setup text | official SAN source pinned; no local integration | needs_experiment |
| EL-MT-04 | MT-4; R3.4 | Compare S initialization with random initialization using paired seeds and report variance. | EXP-INIT-01 | Appendix “More Experiments” / metric ablation | historical prose only | needs_experiment |
| EL-EX-01 | EX-1; R1.5, R2.1 | Run the unified Ori/TIFO switch, reproduce headline cells and include original backbone rows. | EXP-GATE-ETTM2-01; EXP-H96-COVERAGE-01; EXP-PATCHTST-ETTM2-01 | Table `1st_results`; Table `results of other methods` | Seven-dataset iTransformer H96 coverage is complete at three seeds. Historical TIFO wins 3/3 on ETTh1, ETTm2, Electricity and Weather; ETTh2/ETTm1 are mixed or near-neutral; Traffic degrades sharply. PatchTST/ETTm2 is complete at H96/192/336/720 with 12/12 matched seed wins, 2.889% mean relative MSE reduction and sign-test p=0.0004883. Validation-selected Traffic stabilization is supporting-only. | main_experiment_core_verified |
| EL-EX-02 | EX-2; PC.3, R1.4, R5.4 | Run recent relevant plug-ins and audit their framework controls. | EXP-RECENT-01; EXP-PLUGIN-H96-01; EXP-PLUGIN-CONTROL-01 | Experiment settings, main/recent-baseline table | ACN and WDAN have complete seven-dataset, H96, three-seed results. Bare iTransformer controls were rerun inside each official engine; WDAN controls retain native `use_norm=1`. Paired plug-in effects are ACN 6/7, mean +2.44%, worst -7.47%; WDAN 5/7, mean -1.23%, worst -22.17%; TIFO 6/7, mean +1.47%, worst -1.02%. | plugin_matrix_and_controls_verified |
| EL-EX-03 | EX-3; R5.2, R5.5 | Directly measure train/test spectral discrepancy and learned-weight alignment. | EXP-SPECTRAL-EVIDENCE-01; AUDIT-WEIGHT-ALIGNMENT-01; EXP-SUPPORT-SHIFT-01 | Fig. `shift_radar`; Fig. `freq_results2`; analysis appendix | Final three-seed checkpoints show positive score-to-gain Spearman alignment: ETTh1 0.248 ± 0.075 and ETTm2 0.425 ± 0.019; high/low score-quartile gain ratios are 1.592 ± 0.226 and 1.807 ± 0.108. A controlled high-frequency intervention additionally shows monotonically improving TIFO-vs-Ori relative effects on ETTh1 and Traffic as shift strength increases. The old train/test-distance PDFs remain excluded because they lack generator/config provenance. | weight_alignment_and_controlled_shift_verified |
| EL-EX-04 | EX-4; R3.5 | Recover or rerun window, resolution, reconstruction, phase and EMA ablations. | EXP-FFT-ABLATION-01 | Appendix “More Experiments”, current Tables X/Y/Z/W/V | unverified table bodies; EMA bolding error known | needs_experiment |
| EL-EX-05 | EX-5; R4.4 | Keep beyond-forecasting scope as future work unless a clean task experiment is completed. | EXP-GENERALITY-OPTIONAL-01 | Discussion/Conclusion | no valid evidence | optional_needs_experiment |
| EL-PR-01 | PR-1; PC.4, R2.2, R3.2, R3.5, R3.6 | Replace placeholders, deduplicate labels, regenerate best-value formatting and compile. | AUDIT-LATEX-01 | Entire manuscript | preflight: 4 errors, 2 warnings | draft |
| EL-PR-02 | PR-2; R2.4, R4.3 | Explain Figure 2 and remove repeated motivation across Secs. 2.1–2.3. | AUDIT-STRUCTURE-01 | Sec. 2 and relevant figure discussion | outline not revised | draft |
| EL-PR-03 | PR-3/4; R3.7, R4.2 | Correct language/notation and fully document splits, lengths, seeds and artifacts. | AUDIT-REPRO-01 | Experiment settings and Appendix | code/paper split and length contradictions documented | draft |

## Experiment ID policy

- `AUDIT-*` is read-only analysis and can move to `verified` when its report is
  checked against source.
- `EXP-GATE-*` is a representative matched run required before a full sweep.
- `EXP-*` without `GATE` is planned evidence after the protocol gate.
- Every executed experiment must use a manifest derived from
  `experiments/run_manifest.template.json` and list the ledger IDs it supports.
- A run may support more than one concern, but one favorable run cannot by
  itself close a broad theoretical or generality concern.

## Promotion rule

An entry becomes `verified` only when all of the following are present:

1. source/code revision and clean/dirty status;
2. exact task and method configuration;
3. per-seed raw metrics and aggregation script/output;
4. artifact paths that still exist;
5. manuscript change location;
6. claim wording whose strength matches the evidence;
7. independent source/PDF check after Overleaf synchronization.
