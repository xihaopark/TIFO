# TIFO KDD resubmission: reviewer-style reassessment of the current PDF

Date: 2026-07-22

Artifacts reviewed:

- original decision and reviews: `reviews/original/KDD2027resubmit.pdf` and the
  verbatim transcription;
- current compiled manuscript: `FredNormer_overleaf/sample-sigconf.pdf` (9
  pages: one-page Summary of Changes plus eight manuscript pages);
- current LaTeX source and the verified experiment reports/ledgers.

This assessment treats the current PDF as the submission a returning AC or
reviewer would see. It does not give credit for changes that exist only in code
or planning documents.

## Overall verdict

**Current recommendation: weak reject / not yet reviewer-ready.**

The empirical revision is substantially stronger and is no longer the reason to
reject. Recent plug-in baselines, paired engine controls, multi-seed reporting,
negative cases, statistic controls, mechanism diagnostics, and a bounded shift
test now support a credible claim: TIFO is a relatively consistent
dataset-conditioned spectral input adapter, with the best seven-dataset
macro-average MSE among the compared plug-ins.

The decisive problem is that the abstract, introduction, contribution list, and
entire theoretical section still make essentially the same kernel/eigenvalue
equivalence rejected by the AC. The implementation learns unconstrained real
and imaginary spectral gains with MLPs under forecasting loss; it neither
constructs a positive-definite kernel nor solves a kernel eigenproblem. A
returning reviewer can therefore repeat the original central criticism verbatim.

If the theory and its dependent claims are replaced by a code-faithful operator
motivation, the expected recommendation moves to **weak accept / borderline
accept**, subject to a final presentation and provenance audit.

## Reviewer A: theory and technical soundness

### Strengths

- The method path is now much clearer: training-set frequency/channel statistic,
  globally shared MLP gains, rFFT-domain reweighting, iRFFT reconstruction, and
  forecasting loss.
- Shapes and the sample-independent nature of the gains are stated.
- The Hermitian implementation removes the old practice of discarding an
  unexplained imaginary reconstruction residual.
- Weight-alignment and conditioning-control experiments test the intended
  mechanism without claiming a proof.

### Decisive weakness

The current PDF still states all of the following:

- the Fourier transform of the dataset implies that a kernel exists in the
  frequency domain;
- the MLP-produced weights are eigenvalues;
- learning those weights is equivalent to learning the kernel;
- the finite training dataset sufficiently represents all temporal variation;
- the induced time-averaged kernel should perform better than normalization.

None follows from the implemented operator or training objective. The displayed
Bochner equation integrates a dataset symbol `X` as if it were a probability
measure, and the manuscript does not verify the positivity, compact-domain,
continuity, or integral-operator assumptions needed for the stated Mercer chain.
The learned gains are also unconstrained: they need not be positive, ordered, or
shared as one scalar multiplier for a Fourier eigenfunction.

### Minimum required revision

- Remove the Bochner/Mercer equivalence chain rather than trying to add another
  paragraph defending it.
- Call the MLP outputs real/imaginary spectral gains, not eigenvalues.
- Define the implemented operator directly:
  `Z=rFFT(X)`, `Z_tilde=g_r(S) Re(Z)+i g_i(S) Im(Z)`, followed by iRFFT and the
  optional residual interpolation.
- Retain only the narrow real-reconstruction/identity property supported by the
  implementation.
- Treat `mean/std` as a heuristic energy-to-dispersion descriptor. The new
  ablation supports usefulness, not optimality.

### Recommendation

**Reject in current form; weak accept after the above replacement.**

## Reviewer B: novelty, baselines, and empirical evidence

### Strengths

- ACN and WDAN are recent, relevant model-agnostic plug-ins. This is a better
  comparison class than adding unrelated large forecasting backbones.
- Each external repository has a bare-backbone control, so paired plug-in effects
  are separated from training-engine differences.
- TIFO improves its paired backbone on 6/7 datasets and has the smallest
  worst-case degradation and across-dataset effect variance.
- The seven-dataset macro-average MSE is best for TIFO (0.272629), ahead of ACN
  (0.275660), the original backbone (0.276399), and WDAN (0.284525).
- The paper discloses that TIFO wins no individual dataset and that ACN retains
  the best macro-average MAE. This is transparent and credible.
- The conditioning ablation is appropriately bounded: data beats Ones in 6/6
  paired runs, while the precise ordering versus permutation is mixed.
- The FilterNet discussion now says that frequency filtering itself is not the
  novelty. The narrower distinction is dataset-statistic-conditioned input
  adaptation that leaves the forecasting backbone intact.

### Remaining risks

1. The absolute Table 2 entries come from different official engines. The paper
   correctly says they do not isolate plug-in effects, but the response and
   supplement must state the exact search budget, official commit, configuration,
   and paired-control construction. Otherwise the improved table can still look
   selectively tuned.
2. The macro-average advantage over ACN is descriptive rather than universal.
   It holds for all three seed-indexed macro averages and for 6/7
   leave-one-dataset-out summaries, but omitting Traffic reverses the ordering;
   Traffic supplies 86.8% of the positive contributions to the absolute gap.
   It should therefore be reported as an observed aggregate ranking, not a
   statistically significant or universally superior result.
3. ACN+TIFO is reported only as a complementarity diagnostic. It retains the
   predeclared ETTh1/ETTm2/Traffic scope, shows all three datasets, defines the
   order `normalization -> TIFO -> ACN encoder`, and states that it does not
   establish complementarity with FilterNet. This avoids reviving the ambiguous
   historical `TIFO*` claim.
4. The controlled spectral intervention is one synthetic shift, not general OOD
   evidence. The current caveat is appropriate and must remain.

### Recommendation

**Weak accept on experiments**, provided provenance is explicit and the theory
does not overclaim what these results establish.

## Reviewer C: presentation, reproducibility, and resubmission compliance

### Strengths

- The PDF has exactly one Summary of Changes page followed by eight manuscript
  pages.
- The main result tables are generated from verified artifacts and present means
  and sample standard deviations over three seeds.
- Untraceable historical headline tables and the ambiguous `TIFO*` table are not
  compiled.
- Figure and implementation now agree on a global spectral adapter rather than a
  fictitious stationary/non-stationary signal separation.
- No unresolved citation or reference marker appears in the current PDF.

### Remaining presentation defects

- The abstract still contains the strongest unsupported claims: “all possible
  time structures,” “mitigating the distribution shift,” and Fourier transform
  “implicitly induces eigen-decomposition.”
- The introduction repeats the same claims and describes TIFO as a “principled
  new solution” before the invalid theoretical chain.
- “Time-Invariant” is not defined early and operationally. It should mean that
  gains are learned from training data, fixed at inference, shared across test
  samples, and require no online update—not invariance to unseen distributions.
- Stage-I/Stage-II prose is not fully aligned: the introduction places neural
  weight learning in Stage-I, whereas the method computes the statistic in
  Stage-I and applies the MLP in Stage-II.
- Several visible grammar/wording defects remain, including “consistes,”
  “correspond eigenvalues,” “sufficiently representation,” “statioanrity,” and a
  missing full stop in the opening introduction paragraph.
- The source contains much dead historical text and internal comments. They do
  not render, but they increase the risk of reviving stale claims during final
  edits. A clean source pass is advisable after the content rewrite.
- The anonymous code URL and exact reproducibility ledger availability must be
  checked from a clean external context immediately before submission.

### Recommendation

**Major revision for presentation in current form.** Most defects become a
single compact edit once the theory-facing abstract/introduction prose is
rewritten.

## Cross-review synthesis: minimum acceptance gate

### Required

1. Replace the current Bochner/Mercer section and every dependent claim in the
   abstract, introduction, RQ2 wording, and contribution list with the
   code-faithful global spectral-adapter formulation.
2. Define “time-invariant” narrowly and remove universal temporal/OOD language.
3. Run a clean source-to-PDF claim, grammar, reference, and anonymous-link audit.
4. In the response, give exact provenance/search-budget statements for ACN,
   WDAN, TIFO tuning, rejected configurations, and final frozen seeds.

### Completed supporting evidence

5. All nine frozen ACN+TIFO final runs are complete. The manuscript reports all
   three selected datasets: mean MSE improves over ACN on ETTh1, ETTm2, and
   Traffic, with 8/9 paired-seed wins, while preserving the standalone TIFO row.

### Not required

- another recent plug-in baseline;
- a full forecasting-backbone SOTA sweep;
- a broad OOD benchmark;
- more score-statistic variants;
- tuning on final test results to obtain more per-dataset wins.

The paper already has enough empirical material. Acceptance now depends mainly
on removing the theory-implementation contradiction and presenting the existing
evidence with exact provenance.
