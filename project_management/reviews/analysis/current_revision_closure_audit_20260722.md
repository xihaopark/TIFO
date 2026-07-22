# TIFO KDD resubmission: current reviewer-concern closure audit

Date: 2026-07-22

Scope: audit the current manuscript and verified experiment artifacts against the
original Area Chair and reviewer comments. This document supersedes the stale
readiness labels in `comment_inventory.md`; it does not change the manuscript.

## Executive conclusion

The revision is no longer blocked by formatting, missing original-backbone rows,
recent plug-in baselines, or a fictitious method diagram. The empirical story is
now defensible as a **robust model-agnostic plug-in**, rather than a universally
best forecaster. The remaining decision-driving risk is the theoretical section:
the current Bochner/Mercer argument still equates MLP-generated frequency gains
with kernel eigenvalues without an equation-to-code correspondence. This repeats
the central AC concern almost verbatim.

One additional experiment remains useful but secondary: a paired, three-seed
comparison of the stability statistic `S = mean / std` against a random or
uninformative conditioning vector. It should be run only after the theory claim
is narrowed, because it cannot repair the current kernel-eigendecomposition gap.

## Concern-by-concern status

| Concern | Current evidence or manuscript change | Status | Minimum remaining action |
|---|---|---|---|
| PC.1 / R1.1: MLP weights are not kernel eigendecomposition | Implementation is now described as global spectral reweighting, but the abstract, introduction, and theory still call the learned gains eigenvalues and claim equivalence to learning a kernel. | **Open, critical** | Replace the Bochner/Mercer claim with a code-faithful motivation and a narrow real-reconstruction property. |
| PC.2 / R1.3: novelty relative to FilterNet | Related work now identifies FilterNet as the closest architecture-level comparison and narrows novelty to dataset-statistic-conditioned input adaptation while leaving the backbone intact. | **Substantively closed** | In the response letter, explicitly state that frequency filtering itself is not claimed as novel. No extra FilterNet experiment is necessary for the minimal plan. |
| PC.3 / R1.4 / R5.4: missing 2025--2026 baselines | ACN (2025) and WDAN (2025) are included as recent model-agnostic plug-ins over seven datasets and three seeds. This is the relevant comparison class requested by the authors. | **Closed for the plug-in claim** | Explain why recent full forecasting architectures are out of scope: they confound backbone and plug-in effects. |
| PC.4 / R2.2 / R3.2 / R3.5 / R3.6: incomplete formatting and broken references | Historical unverified tables are excluded; current PDF compiles with no broken-reference error; bolding and generated result rows are controlled by verified artifacts. | **Closed** | Final clean-build and PDF preflight immediately before submission. |
| R1.2 / R3.1: why `mean/std`; no optimality basis | The method section now gives an operational interpretation and the weight-alignment table shows positive score/gain association on ETTh1 and ETTm2. It still lacks a matched alternative-statistic or random-conditioning test. | **Partial** | Run one paired three-seed `S` versus random/uninformative-vector ablation on ETTh1 and ETTm2, or explicitly present `S` as a heuristic and remove any optimality implication. |
| R1.5 / R2.1: tuning fairness and original backbone rows | Ori/TIFO uses matched seeds and protocol; ACN/WDAN are accompanied by each repository's bare-backbone control; TIFO selection is validation-only and the rejected ETTm2 configuration is documented. | **Closed** | Put the exact search-budget statement and provenance links in the response/supplement. |
| R2.3: simultaneous normalizers and TIFO* ambiguity | The historical TIFO* table is excluded from the compiled paper; current claims do not rely on an unimplemented SAN combination. | **Closed by removal** | State plainly in the response that the ambiguous variant was removed. |
| R2.4 / R4.1: Figure 2 discussion and figure/code mismatch | The pipeline now describes dataset-level statistics, globally shared gains, spectral reweighting, inverse transform, and forecasting. No fictitious stationary/non-stationary signal separation is claimed. | **Closed** | Final visual check that figure labels use the same symbols as the method text. |
| R2.5 / R3.3: time-invariance and unseen temporal structures | Global weights are correctly distinguished from per-sample adaptation; a controlled high-frequency intervention reports bounded behavior and explicitly disclaims arbitrary OOD robustness. However, phrases such as "all possible time structures" remain in the abstract/introduction/theory. | **Partial, tied to theory** | Replace universal time-support language with "training-distribution, dataset-level" language; define time-invariant as sample-independent inference parameters. |
| R3.4: `S` versus random initialization | Old result text remains, but the concern is not backed by a newly verified paired multi-seed artifact. | **Open, secondary** | Same two-dataset ablation proposed above; report mixed results without significance claims. |
| R4.2: amplitude and tensor dimensions | The method specifies `X in R^(L x C)`, spectra and scores in `R^(K x C)`, and transformed input in `R^(L x C)`. | **Closed** | None beyond final notation audit. |
| R4.3: overlapping early sections | The current structure is improved, but legacy prose remains repetitive and contains grammar defects. | **Partial, editorial** | Condense while rewriting the theory-facing motivation; do not add a new experiment. |
| R4.4: tasks beyond forecasting | The paper no longer needs a demonstrated universal-task claim. | **Closed by scope** | State as future work only. |
| R5.1 / R5.5: evidence linking stationarity scores, learned gains, and shift | Weight-alignment diagnostics show positive Spearman correlation and high/low gain ratios above one; controlled spectral shift shows the relative TIFO effect improves monotonically with intervention strength on ETTh1 and Traffic, while Traffic remains negative. | **Closed with bounded evidence** | Keep the current caveats; do not claim causal proof or arbitrary OOD robustness. |
| R5.2 / R5.3: spectral shift is only one kind of shift; theoretical guarantee unsupported | Scope/limitations now says the test is a controlled high-frequency intervention only. The theory still claims solved distributional shift through an induced kernel. | **Partial, tied to theory** | Remove theorem-like mitigation guarantees and label the mechanism as empirical spectral adaptation. |

## Minimal resubmission gate

Required before the paper is reviewer-ready:

1. Rewrite the theoretical section and every dependent abstract/introduction
   sentence so the claims match the implemented operator.
2. Run a final source/PDF claim and reference audit.

Strongly recommended, but not allowed to expand into a new experiment suite:

3. Run one two-dataset, three-seed `S` versus random/uninformative conditioning
   ablation using the already frozen ETTh1 and ETTm2 protocols.

No additional full-backbone SOTA sweep, task-generalization experiment, or broad
OOD benchmark is necessary for the minimal response plan.
