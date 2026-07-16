# KDD resubmit reviewer comment inventory

Status: `triage_only`

Decision: `Resubmit`

Verbatim source: `../transcribed/openreview_decision_and_reviews_verbatim.md`

This file splits the decision and reviews into atomic concerns. Quoted text is
copied from the verified transcription; interpretation and planned work are
kept in separate columns. No row is considered resolved merely because a
manuscript passage is highlighted.

Readiness values:

- `verified`: action and supporting artifact have been checked.
- `draft`: prose/design work exists but is not final evidence.
- `needs_experiment`: a runnable matched experiment is required.
- `blocked`: an external decision or unavailable prerequisite prevents work.

## Decision-driving inventory

| Atomic ID | Route | Exact reviewer excerpt | Type | Severity | Required response | Evidence or experiment needed | Current finding | Readiness |
|---|---|---|---|---|---|---|---|---|
| PC.1 | TH-1 | “There is a notable theory-implementation gap: directly predicting scalar weights with an MLP is not equivalent to rigorous kernel eigendecomposition.” | theory | critical | Either prove a precise correspondence or narrow the eigendecomposition claim and present the theory as motivation/interpretation. | Equation-to-code map; assumptions; claim audit. | Code uses two MLPs to produce log-magnitude and phase masks; no eigendecomposition is implemented. | draft |
| PC.2 | MT-1, TH-1 | “Frequency reweighting after DFT appears close to existing spectral normalization/filtering ideas, and theoretical justification for novelty remains insufficiently developed.” | novelty/positioning | critical | Define the distinct object learned by TIFO, contrast it with normalization and filtering, and calibrate novelty. | Method matrix against FilterNet, FAN, SAN, RevIN; direct citations; optional matched FilterNet experiment. | Official FilterNet source is pinned locally; comparison has not been run. | needs_experiment |
| PC.3 | EX-2 | “Stronger baselines are missing from 2025-2026.” | experiment | critical | Add reproducible recent baselines selected by relevance, not chronology alone. | Frozen protocol; official implementations; matched seeds and budgets. | TSLib has been pinned as an implementation source, but recent baseline selection is not yet finalized. | needs_experiment |
| PC.4 | PR-1 | “Format issues, e.g., broken cross-references (Table ??).” | presentation | major | Repair every placeholder, duplicate label, reference and result-formatting error. | Static LaTeX audit and clean compile. | Live source still contains Table X/Y/Z/W/V placeholders and duplicate labels. | draft |
| R1.1 | TH-1 | “using an MLP to directly predict scalar weights is not fully equivalent to a rigorous kernel eigen-decomposition process” | theory | critical | Same resolution as PC.1, with explicit language correction. | Equation-to-code map and proof/claim boundary. | Same gap confirmed in `utils/frequency_domain_filter.py`. | draft |
| R1.2 | TH-2 | “the paper lacks first-principle derivations or deeper physical explanations as to why the simple ratio of low-order moments is the optimal representation of frequency stability.” | theory/metric | critical | Define what the score measures; remove “optimal” implications; give edge cases and alternative metrics. | Matched metric ablation with seeds; score distribution/interpretability artifact. | Code computes cross-window FFT-amplitude mean divided by standard deviation after per-window z-score. | needs_experiment |
| R1.3 | MT-1 | “The core idea of using an MLP to modulate frequency components is similar to existing Frequency-domain MLPs (e.g., FilterNet[1]).” | novelty | critical | Explain technical divergence and whether TIFO is complementary to FilterNet. | Component-level comparison; ideally TIFO on a frequency-filtering backbone or matched head-to-head result. | Official FilterNet repo is pinned at a fixed commit. | needs_experiment |
| R1.4 | EX-2 | “The backbones used (DLinear and PatchTST) no longer represent the recent state-of-the-art.” | baseline | critical | Retain legacy backbones for continuity but add strong recent reproducible models. | Shortlist and frozen configs; compute-aware coverage plan. | Current runnable local registry contains only DLinear, PatchTST and iTransformer. | needs_experiment |
| R1.5 | EX-1 | “clarify whether equivalent hyperparameter searches were conducted for all baseline models ... to rule out tuning bias” | fairness | critical | Explain the >50% ETTm2 gains with original-backbone rows and an auditable equal-budget protocol. | Same seeds, splits, lengths, backbone version, search space, early stopping and metric code. | Current scripts use one run; paper reports mean±std; unusually weak original rows are not yet traceable to matched multi-seed artifacts. | needs_experiment |
| R2.1 | EX-1, PR-1 | “It would be helpful if Table 2 could also include the original results of the backbone models.” | experiment/table | major | Add Ori rows for every Table 2 backbone under the identical protocol. | Disable-TIFO switch and matched runs. | Current experiment builder always injects TIFO; no clean original-backbone switch exists. | needs_experiment |
| R2.2 | PR-1 | “Some table references are not properly displayed and appear as ‘Table ??’.” | presentation | major | Resolve all references and validate the compiled PDF. | Static audit and visual PDF check. | Placeholder references remain. | draft |
| R2.3 | MT-3 | “I do not understand why two normalization methods are applied simultaneously ... What does the comparison between ‘TIFO *’ and ‘TIFO’ indicate?” | method/fairness | major | Define TIFO* precisely, explain ordering and orthogonality, or remove it if the combination cannot be justified and reproduced. | Module-composition diagram and matched TIFO/TIFO+SAN/SAN/Ori runs. | SAN is not integrated in the current TIFO code path. | needs_experiment |
| R2.4 | PR-2 | “The main text seems to lack discussion and explanation of Figure 2.” | presentation | major | Explain the figure’s variables, takeaway and link to the method. | Figure-to-claim audit. | Discussion location has not yet been repaired. | draft |
| R2.5 | TH-3, PR-3 | “I believe the method is actually time-variant.” | naming/concept | critical | Define the intended invariance precisely and avoid conflating a time-invariant operator with a time-independent data distribution. | Formal definition; naming decision; limitation statement. | Current “all possible time structures” language is stronger than the training-support assumption permits. | draft |
| R3.1 | TH-2, MT-1 | “Why use the deviation of the mean and the standard?” | metric/novelty | critical | Provide interpretation, alternatives and evidence for the score. | Same matched metric ablation as R1.2. | Existing manuscript table is not yet linked to inspectable result artifacts. | needs_experiment |
| R3.2 | PR-1 | “The manuscript appears to be in an incomplete state.” | presentation | critical | Eliminate all incomplete markers before scientific reassessment. | Static source/PDF audit. | Live paper still contains placeholders and review markup. | draft |
| R3.3 | TH-3 | “If the test set exhibits a temporal structure t_new that is outside the support of p(t), the ‘Time-Invariant’ property might fail.” | theory/OOD | critical | Restrict the guarantee to represented training conditions; state the OOD limitation; add controlled shift evidence if feasible. | Shift-stratified or support-stress experiment; assumption rewrite. | No current artifact establishes coverage outside training support. | needs_experiment |
| R3.4 | MT-4 | “the improvement brought by S compared to random initialization of weights is limited, and it also increased the standard deviation” | robustness | major | Report the mixed result honestly and test matched seeds. | Multi-seed S vs random initialization with paired statistics. | Existing table claim is not traceable to a complete matched seed set. | needs_experiment |
| R3.5 | PR-1, PR-4 | “multiple broken cross-references to critical evidence” | reproducibility | critical | Make every cited ablation and efficiency artifact present and reachable. | Table/appendix artifact ledger and clean compile. | Several manuscript claims point to symbolic Table X/Y/Z/W/V. | draft |
| R3.6 | PR-1 | “in Table 16, the MSE for ema_0.9 (0.3932) is better than the bolded value for no_update (0.3938).” | table correctness | major | Recompute best/second-best formatting mechanically. | Table-value checker. | Reviewer’s numerical comparison is correct; formatting must be regenerated. | draft |
| R3.7 | PR-3 | “... so it can sufficiently representation the distributions” | language | minor | Proofread after scientific revisions stabilize. | Language audit. | Known grammar defect recorded. | draft |
| R4.1 | MT-2 | “There is no separation operation as depicted in the diagram.” | method consistency | critical | Redraw the figure or implement the depicted decomposition; make figure, equations, algorithm and code identical. | Step-by-step code map and revised figure. | Implementation produces one complex mask and a residual output, not explicit f_s/f_n separation. | draft |
| R4.2 | PR-3 | “The dimension of the amplitude matrix A is not specified.” | notation | major | Define dimensions for every tensor through the pipeline. | Shape table tied to code. | Code mask has shape `[L, C]`; manuscript notation needs alignment. | draft |
| R4.3 | PR-2 | “Sections 2.1, 2.2, and 2.3 contain overlapping discussions” | structure | major | Separate problem definition, limitations of prior normalization and TIFO motivation. | Section outline. | No revision made yet. | draft |
| R4.4 | EX-5 | “What's the potential ... beyond long-term forecasting, such as imputation and classification?” | generality | optional | Answer as future scope unless matched evidence is added; do not claim demonstrated generality. | Optional imputation/classification experiment. | PatchTST contains task branches but TIFO is not consistently applied/inverted in them. | needs_experiment |
| R5.1 | MT-1 | “there are no evidence to support their relationship” | positioning/evidence | critical | Explain the mathematical and operational relationship between normalization and TIFO and test complementarity. | Direct distribution/spectral measurements and matched Ori/normalizer/TIFO combinations. | Current paper relies mostly on motivation and forecasting accuracy. | needs_experiment |
| R5.2 | EX-3 | “Maybe it only is one part of the distributional shift of datasets.” | claim scope | critical | State that spectral shift is one measurable view, not a replacement for all distribution shift. | Multiple shift metrics or calibrated claim. | Universal replacement is unsupported. | draft |
| R5.3 | TH-1, EX-3 | “How could TIFO could solve the distributional shift with the theoretical analysis? It lacks theoretical justification.” | theory/evidence | critical | Separate theoretical interpretation from empirical mitigation; avoid a theorem-like guarantee without proof. | Claim-evidence audit and direct shift experiment. | Forecast accuracy alone cannot establish solved distribution shift. | needs_experiment |
| R5.4 | EX-2 | “It lacks SOTA algorithms from 2025 and 2026.” | baseline | critical | Same recent-baseline plan as PC.3/R1.4. | Official runnable implementations under frozen protocol. | Not yet run. | needs_experiment |
| R5.5 | EX-3 | “Which experimental setting could support the statement?” | interpretability/evidence | critical | Add an experiment that directly connects learned weights with cross-condition spectral stability and forecasting effects. | Spectral-distance before/after; weight-vs-stability correlation; controlled ablation. | Current result artifacts do not directly verify the representation claim. | needs_experiment |

## Consolidated work packages

| Package | Atomic comments | Deliverable | Exit criterion |
|---|---|---|---|
| WP-THEORY | PC.1, PC.2, R1.1, R1.2, R2.5, R3.1, R3.3, R5.2, R5.3 | Calibrated theory and invariance definition | Every theoretical claim has an assumption, derivation or explicit empirical/interpretive label. |
| WP-METHOD | R1.3, R2.3, R4.1, R4.2, R5.1 | Figure–equation–algorithm–code map and closest-method comparison | One implementation-consistent pipeline; no fictitious decomposition. |
| WP-FAIR | PC.3, R1.4, R1.5, R2.1, R5.4 | Frozen protocol, Ori rows, recent baselines, seed repeats | Every compared method uses the same task and documented search budget. |
| WP-EVIDENCE | R3.4, R4.4, R5.5 | Metric, initialization, shift and optional generality evidence | Every table value has a result directory, config, seed and code revision. |
| WP-CLEAN | PC.4, R2.2, R2.4, R3.2, R3.5, R3.6, R3.7, R4.3 | Complete compilable manuscript | No placeholders, broken refs, incorrect bolding, undefined dimensions or internal markup in submission PDF. |

## Immediate gate

The project is currently `needs_experiment`, not response-ready. The first
scientific gate is to freeze one canonical protocol and implement a clean
Ori/TIFO switch before interpreting the current headline improvements.
