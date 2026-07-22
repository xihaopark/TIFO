# TIFO KDD resubmission: point-by-point response working package

Date: 2026-07-22

## Response strategy summary

- Decision type: revise-and-resubmit.
- Task mode: draft/triage hybrid.
- Package readiness: `draft_with_placeholders`.
- Overall posture: cooperative, evidence-forward, and explicit about mixed
  results and limitations.
- Major unresolved risk: the manuscript has not yet applied the proposed
  theory rewrite, so no response may claim that the theory--implementation gap
  is closed.
- Suggested ordering: AC decision-driving concerns first; then group repeated
  reviewer concerns by theory, score, novelty/baselines, implementation clarity,
  OOD scope, and presentation.

The current KDD PDF uses a one-page Summary of Changes rather than compiling
this full response package. This document is the internal audit trail used to
ensure that no reviewer concern is lost.

## Comment-response tracker

| IDs | Reviewer concern | Type | Severity | Current action/evidence | Readiness |
|---|---|---|---|---|---|
| PC.1, R1.1, R5.3 | MLP gains are not a kernel eigendecomposition; theory does not show that TIFO solves distribution shift | theory | critical | Code-faithful replacement drafted but not applied | `AUTHOR_INPUT_NEEDED` |
| PC.2, R1.3 | Similarity to FilterNet; novelty and possible complementarity | novelty | critical | Related Works narrows novelty; no direct FilterNet-enhancement claim is made | ready with scoped response |
| PC.3, R1.4, R5.4 | Missing 2025--2026 baselines / recent backbones | experiment | critical | ACN and WDAN added as recent plug-ins over seven datasets; full-backbone sweep scoped out | ready |
| PC.4, R2.2, R3.2, R3.5, R3.6 | Incomplete formatting, broken references, missing evidence, wrong bolding | presentation | critical | Verified tables mechanically generated; no unresolved PDF references; final preflight remains | partial |
| R1.2, R3.1, R3.4 | Why mean/std; comparison with random or uninformative conditioning; variance | metric/evidence | critical | Three-seed ETTh1/ETTm2 data/permuted/ones ablation; data beats Ones 6/6, permutation mixed | ready |
| R1.5, R2.1 | Tuning fairness and original-backbone rows | fairness | critical | Matched Ori/TIFO seeds; bare-backbone controls inside ACN/WDAN engines; validation-only selection | partial |
| R2.3 | Ambiguous TIFO* and simultaneous normalizers | method/fairness | major | Historical TIFO* removed; ACN+TIFO is separately named, ordered, and reported over the full preregistered scope | ready |
| R2.4 | Figure 2 lacks explanation | presentation | major | Pipeline prose now explains statistic, global gains, spectral transform, inverse transform, backbone | ready |
| R2.5, R3.3 | Meaning of time-invariant; unseen temporal structures | naming/OOD | critical | Global sample-independent gains stated; universal language still remains in theory-facing sections | `AUTHOR_INPUT_NEEDED` |
| R4.1 | Figure shows a separation not implemented in code | method consistency | critical | Figure replaced with code-consistent global spectral adapter | ready |
| R4.2 | Amplitude/tensor dimensions missing | notation | major | Shapes stated through input, spectrum/score, and transformed input | ready |
| R4.3, R3.7 | Repetition and language defects | presentation | major/minor | Structure improved, but visible theory-facing grammar defects remain | partial |
| R4.4 | Tasks beyond forecasting | scope | optional | Universal task claim removed; future work only | ready |
| R5.1, R5.5 | No evidence connecting score, gains, shift, and normalization | evidence | critical | Gain alignment, paired score controls, controlled spectral intervention, and paired plug-in effects | ready with caveats |
| R5.2 | Spectral shift is only one part of distribution shift | claim scope | critical | Controlled intervention explicitly scoped to one high-frequency shift; theory still overclaims | partial |

## Draft core responses

### AC / PC.1 and Reviewers R1.1, R5.3: theory--implementation gap

**Preserved concern.** “There is a notable theory-implementation gap:
directly predicting scalar weights with an MLP is not equivalent to rigorous
kernel eigendecomposition.” Related comments ask how the theoretical analysis
shows that TIFO solves distribution shift.

**Response -- pending manuscript approval.** We agree that the original text
overstated the connection between the implemented spectral adapter and kernel
eigendecomposition. The implementation does not construct a positive-definite
kernel or solve an eigenproblem. We therefore propose to replace the
Bochner/Mercer equivalence argument with a direct definition of the implemented
operator: a fixed training-set statistic conditions globally shared real and
imaginary spectral gains, which are optimized jointly with the forecasting
backbone. We will refer to these parameters as spectral gains rather than kernel
eigenvalues and will retain only the real-valued iRFFT reconstruction property.
We will also remove claims that the operator guarantees mitigation of arbitrary
distribution shift. The controlled intervention will remain an empirical,
bounded diagnostic rather than a theorem-like guarantee.

**Location placeholder.** `[AUTHOR_APPROVAL_NEEDED: Abstract, Introduction,
Theoretical Analysis, RQ2, and Conclusion]`.

### PC.2 / R1.3: FilterNet and complementarity

**Preserved concern.** “The core idea of using an MLP to modulate frequency
components is similar to existing Frequency-domain MLPs (e.g., FilterNet).” The
reviewer asks for the technical divergence and whether TIFO can complement this
line of methods.

**Response.** We agree that frequency filtering itself is not novel, and we have
narrowed the claim accordingly. FilterNet replaces core temporal mappings with
learnable frequency filters, whereas TIFO is a compact input adapter conditioned
on cross-window training-set statistics and leaves the forecasting backbone
unchanged. This distinction is now stated in Related Works. We do not claim that
the present experiments establish improved FilterNet performance, because that
would change the forecasting architecture rather than isolate TIFO as a plug-in.
Instead, we delimit the contribution to the source and deployment of TIFO's
spectral gains and identify direct composition with frequency-filtering
architectures as future work.

**Location.** Related Works and the scoped contribution statement.

### PC.3 / R1.4 / R5.4: recent baselines

**Preserved concern.** “Stronger baselines are missing from 2025--2026,” and the
legacy forecasting backbones no longer represent recent state of the art.

**Response.** We added ACN (ICML 2025) and WDAN (2025), two recent methods in the
same model-agnostic plug-in comparison class, over all seven datasets at
`H=96` and three seeds. Because their official repositories use different
training engines, we also reran a bare iTransformer inside each engine and
report paired plug-in effects separately from absolute values. TIFO improves
6/7 paired datasets, has the smallest worst-case degradation and effect
variance, and obtains the lowest seven-dataset macro-average MSE. ACN retains
the best macro-average MAE. The updated TIFO macro MSE is 0.272629 versus
0.275660 for ACN; the ordering holds for all three seed-indexed macro averages,
although the absolute gap is concentrated in Traffic and is not presented as a
cross-engine significance result. We did not present unrelated full forecasting
architectures as plug-in controls because changing the backbone would confound
the effect under review.

**Location.** Summary of Changes item 3; Experiments, Tables 2 and 3; Related
Works.

### R1.2 / R3.1 / R3.4: statistic choice and uninformative controls

**Preserved concern.** The reviewers ask why mean/std represents frequency
stability and note that the original comparison with random initialization was
small and variable.

**Response.** We now describe mean/std as an empirical energy-to-dispersion
descriptor rather than an optimal stationarity estimator. We ran a frozen,
three-seed paired ablation on ETTh1 and ETTm2 using the data statistic, a
frequency-permuted control that preserves each channel's score distribution,
and an all-ones control that removes score variation. The data statistic
outperforms Ones in all six paired runs. Its mean MSE is also lower than the
permuted control on both datasets, but the paired seed ordering is mixed (2/3
on ETTh1 and 1/3 on ETTm2). We therefore conclude only that data-dependent
non-uniform conditioning is useful; we do not claim that the precise frequency
ordering is uniformly optimal.

**Location.** Experiments, Table 5 and accompanying paragraph; Summary of
Changes item 6.

### R1.5 / R2.1: tuning fairness and original backbone

**Preserved concern.** The reviewers request original backbone rows and ask
whether equivalent hyperparameter searches were conducted.

**Response.** We rebuilt the evaluation around matched Ori--TIFO switches,
identical splits and seeds, and validation-only configuration selection. Every
promoted run records the command, seed, dataset hash, code state, log, and final
metrics. For ACN and WDAN, we preserve official dataset-level configurations
and run the bare backbone in the same official engine. Missing Traffic settings
were each selected from four validation-only candidates. We do not claim an
identical search budget: the disclosed promoted TIFO validation lineages contain
4 candidates on ETTh1, 50 on ETTh2, 17 on ETTm1, 4 on ETTm2, 8 each on
Electricity and Weather, and 31 on Traffic. The Electricity and Weather gates
were the first new searches for those datasets; both independently selected the
same Hermitian-aligned, zero-pad-ratio-1.0 configuration before final testing.
We therefore separate absolute
cross-engine values from paired within-engine plug-in effects and retain all
negative cases. We removed earlier headline values that could not be traced to
complete multi-seed artifacts.

**Location.** Summary of Changes items 1--3 and 5; Experiment Settings; Tables
1--3; provenance record
`baseline_and_tifo_search_provenance_20260722.md`. Official base commits are ACN
`2d6ce2f2c771fec5296870416844d995c23e31a2` and WDAN
`f01994ada4980729eb6af14c35778f480f9c0c47`.

### R2.3 / R4.1 / R4.2: implementation clarity

**Preserved concern.** The reviewers note ambiguity in TIFO*, a figure/code
disconnect, and missing amplitude dimensions.

**Response.** We removed the historical TIFO* result because the simultaneous
normalizer ordering was not sufficiently specified. The revised figure and
method now describe the implemented path without claiming an explicit
stationary/non-stationary signal separation. For an input in `R^(L x C)`, the
one-sided spectrum and score have shape `R^(K x C)`, and iRFFT returns the
transformed input in `R^(L x C)`. The real and imaginary spectral gains are
global parameters conditioned on the training statistic and shared by all test
samples.

**Location.** Proposed Method overview and Stage-I/Stage-II; revised method
figure.

### R2.5 / R3.3: time invariance and unseen temporal structures

**Preserved concern.** The reviewers question the use of “Time-Invariant” and
ask what happens when test conditions lie outside the support observed in
training.

**Response -- pending manuscript approval.** We agree that the original wording
could be read as invariance to arbitrary unseen temporal distributions. Our
intended operational meaning is narrower: the statistic and learned spectral
gains are estimated from training data, fixed at inference, shared across test
samples, and require no online update. TIFO assumes that relevant test spectral
behavior is sufficiently represented in training and provides no guarantee for
arbitrary unsupported shifts. We will replace “all possible time structures”
and equivalent universal wording throughout the manuscript.

**Location placeholder.** `[AUTHOR_APPROVAL_NEEDED: Abstract, Introduction,
Theoretical Analysis, and limitation language]`.

### R5.1 / R5.2 / R5.5: direct mechanism and shift evidence

**Preserved concern.** The reviewers request evidence connecting normalization,
stationarity scores, learned weights, and distribution shift, and caution that
spectral shift is only one part of distribution shift.

**Response.** We added three bounded diagnostics. First, learned gains are
positively associated with the training-set score on frozen ETTh1 and ETTm2
checkpoints, with positive Spearman correlations and high/low-score gain ratios
above one. Second, data-dependent conditioning outperforms the all-ones control
in all six paired runs. Third, a controlled high-frequency intervention shows
that TIFO's relative effect improves monotonically with intervention strength
on ETTh1 and Traffic. Traffic remains an absolute negative case. We therefore
present the intervention as one controlled spectral shift, not as evidence of
general OOD robustness or complete resolution of distribution shift.
Separately, a preregistered ACN+TIFO composition evaluates whether TIFO can
complement a recent normalization plug-in in the explicit order normalization,
TIFO spectral adaptation, and ACN encoding. All nine final runs are complete:
mean MSE improves over ACN on ETTh1 (0.388795 to 0.385508, 3/3 paired wins),
ETTm2 (0.180988 to 0.179959, 3/3), and Traffic (0.427060 to 0.425896, 2/3).
We report this as normalization complementarity, not as a new standalone method
or evidence that TIFO improves FilterNet.

**Location.** Experiments, Tables 4 and 5 and controlled-shift paragraph;
Summary of Changes item 6.

### Presentation comments PC.4 / R2.2 / R2.4 / R3.2 / R3.5 / R3.6 / R3.7 / R4.3

**Response.** We removed unverified historical tables, regenerated promoted
tables from traceable result artifacts, corrected best/second-best formatting,
added an implementation-consistent figure explanation, and compiled the revised
PDF without unresolved cross-references. The current PDF contains one Summary
of Changes page followed by eight manuscript pages. A final grammar and clean
build audit remains necessary after the theory-facing prose is replaced.

**Location.** Throughout; Summary of Changes items 2, 4, and 5.

## Manuscript change checklist

- [ ] Apply the code-faithful theory replacement after author approval.
- [ ] Replace universal/guarantee language in the Abstract and Introduction.
- [ ] Define “time-invariant” at first use.
- [ ] Align the Introduction's Stage-I/Stage-II description with the Method.
- [ ] Change every active “eigenvalue” reference for MLP outputs to “spectral
  gain” or “weight.”
- [x] Add exact ACN/WDAN/TIFO search counts and pinned source commits to the
  response/provenance statement.
- [x] Report all nine frozen ACN+TIFO runs as a bounded normalization
  complementarity diagnostic without replacing standalone TIFO.
- [ ] Run final visible-grammar, reference, anonymous-link, and clean-build
  checks.

## Missing information / risk flags

- `AUTHOR_INPUT_NEEDED`: approval to replace the current Bochner/Mercer theory
  and dependent abstract/introduction claims.
- Exact final manuscript page/line references must be generated only after the
  theory rewrite is frozen.
- The anonymous code URL must be externally checked before submission.

## 中文核对

- 理论回复目前只能标为“拟修改”，不能写成“已经解决”；需要作者明确同意后才能落到正文。
- ACN+TIFO 的 9/9 运行已结束，正文完整报告三个数据集；它只作为 normalization 互补性证据，不替代独立 TIFO，也不回答 FilterNet 组合效果。
- baseline 回复还需补最终的搜索候选数量、官方仓库 commit 和冻结配置位置。
- 最终提交前需要重新生成页码/行号，不能沿用当前工作稿的位置。
