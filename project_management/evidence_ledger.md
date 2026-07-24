# KDD resubmit evidence ledger

Updated: 2026-07-24

Status: `full_plugin_main_table_complete_local_evidence`

This ledger is the cross-workspace link from reviewer concern to planned action,
experiment, manuscript target and inspectable evidence. `Planned` means neither
the experiment nor the manuscript response has been completed.

| Ledger ID | Concern routes / atomic comments | Action | Experiment or audit ID | Paper target | Current evidence | Readiness |
|---|---|---|---|---|---|---|
| EL-TH-01 | TH-1; PC.1, R1.1, R5.3 | Preserve the author-frozen theory; audit code/method consistency and flag any contradiction for explicit author decision. | AUDIT-THEORY-CODE-01 | Sec. 3.2 `sec:Theoretical Analysis`; method equations | Historical checkpoint replay identifies the exact result-producing raw-FFT, two-MLP, input-only operator; prediction inverse filtering is disproved by saved predictions. | frozen_code_path_verified |
| EL-TH-02 | TH-2; R1.2, R3.1 | Define mu/sigma, assumptions, failure cases and compare alternative stability scores. | EXP-METRIC-ETTH1-01 | Sec. 3.1; Appendix “Ablation Study on Stationarity Metrics” | mu/sigma implementation exists; table provenance missing | needs_experiment |
| EL-TH-03 | TH-3; R2.5, R3.3 | Restrict invariance to the represented training distribution and state OOD limits. | EXP-SUPPORT-SHIFT-01 | Sec. 2.3, theory assumptions, limitations/conclusion | A deterministic three-seed stress test coherently scales the upper half of non-DC rFFT bins over each input/future window. From strength 0 to 1, TIFO's relative effect improves from +1.09% to +1.97% on ETTh1 and from -1.02% to -0.51% on Traffic. This supports bounded high-frequency-shift robustness, not arbitrary OOD invariance. | controlled_shift_verified_theory_wording_open |
| EL-MT-01 | MT-1; PC.2, R1.3, R5.1 | Preserve the complete submitted result surface and extend it with ACN/WDAN on iTransformer and DLinear. | EXP-FULL-PLUGIN-01; EXP-FULL-PLUGIN-02 | Experiment settings; Table `full_plugin_comparison` | The 280 submitted TIFO/TIFO*/RevIN/SAN/FAN rows are retained. ACN and WDAN add 84 three-seed final rows per backbone-method pair (336 local rows total), covering all seven datasets and four horizons without missing cells. | full_plugin_extension_verified |
| EL-MT-02 | MT-2; R4.1, R4.2 | Make Figure 1, tensor dimensions, equations, algorithm and code describe one operator. | AUDIT-METHOD-MAP-01; EXP-HERMITIAN-01 | Sec. 3.1; `fig:model`; Algorithm 1 | The historical path is preserved; new Hermitian variants use rFFT/iRFFT, reconstruct real sequences without discarding an imaginary residual, and optionally compute statistics after the same per-window normalization seen by the backbone. GPU correctness tests and three-seed ETTh1/ETTm2 finals are complete. The current paper figure and shape text still describe a different decomposition. | implementation_verified_paper_open |
| EL-MT-03 | MT-3; R2.3 | Define TIFO+SAN composition/order and test whether it is additive; otherwise remove TIFO*. | EXP-COMPOSE-01 | Table `results of other methods`; setup text | official SAN source pinned; no local integration | needs_experiment |
| EL-MT-04 | MT-4; R3.4 | Compare S initialization with random initialization using paired seeds and report variance. | EXP-INIT-01 | Appendix “More Experiments” / metric ablation | historical prose only | needs_experiment |
| EL-EX-01 | EX-1; R1.5, R2.1 | Run validation-selected TIFO on two distinct backbones and include the complete four-horizon matrix. | EXP-FULL-PLUGIN-01 | Table `full_plugin_comparison` | iTransformer and genuine DLinear each have 84 frozen final runs: 7 datasets x 4 horizons x seeds 2021--2023. Every cell has a validation-only candidate lineage and an explicit final protocol. | full_two_backbone_matrix_verified |
| EL-EX-02 | EX-2; PC.3, R1.4, R5.4 | Run recent relevant plug-ins and audit protocol compatibility. | EXP-RECENT-01; EXP-PLUGIN-H96-01; EXP-FULL-PLUGIN-01 | Experiment settings; Table `full_plugin_comparison` | All ACN/WDAN cells are locally evaluated. On iTransformer at H=96, TIFO averages 0.27014/0.29800, ACN 0.27484/0.29905, and WDAN 0.28370/0.30617. Across the 28 iTransformer rows, TIFO averages 0.33625/0.34282 versus 0.34387/0.34523 for ACN and 0.34405/0.34855 for WDAN. | recent_plugin_comparison_verified |
| EL-EX-03 | EX-3; R5.2, R5.5 | Directly measure train/test spectral discrepancy and learned-weight alignment. | EXP-SPECTRAL-EVIDENCE-01; AUDIT-WEIGHT-ALIGNMENT-01; EXP-SUPPORT-SHIFT-01 | Fig. `shift_radar`; Fig. `freq_results2`; analysis appendix | Final three-seed checkpoints show positive score-to-gain Spearman alignment: ETTh1 0.248 ± 0.075 and ETTm2 0.425 ± 0.019; high/low score-quartile gain ratios are 1.592 ± 0.226 and 1.807 ± 0.108. A controlled high-frequency intervention additionally shows monotonically improving TIFO-vs-Ori relative effects on ETTh1 and Traffic as shift strength increases. The old train/test-distance PDFs remain excluded because they lack generator/config provenance. | weight_alignment_and_controlled_shift_verified |
| EL-EX-04 | EX-4; R3.5 | Recover or rerun window, resolution, reconstruction, phase and EMA ablations. | EXP-FFT-ABLATION-01 | Appendix “More Experiments”, current Tables X/Y/Z/W/V | unverified table bodies; EMA bolding error known | needs_experiment |
| EL-EX-05 | EX-5; R4.4 | Keep beyond-forecasting scope as future work unless a clean task experiment is completed. | EXP-GENERALITY-OPTIONAL-01 | Discussion/Conclusion | no valid evidence | optional_needs_experiment |
| EL-PR-01 | PR-1; PC.4, R2.2, R3.2, R3.5, R3.6 | Retain the submitted result tables, extend them with complete new-baseline columns, and compile. | AUDIT-LATEX-01; EXP-FULL-PLUGIN-01; EXP-FULL-PLUGIN-02 | Original main results; Table `full_plugin_comparison`; Results | The complete generated table has 56 dataset--horizon rows, seven methods per backbone, no missing method cells, no dagger symbols, and tie-aware best/second-best formatting. The submitted main tables and downstream analyses remain in place. The 23-page manuscript compiles successfully; the one-page change summary, full comparison table, and following analysis pages were visually inspected without clipping or missing content. | verified_compiled_and_visually_inspected |
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
