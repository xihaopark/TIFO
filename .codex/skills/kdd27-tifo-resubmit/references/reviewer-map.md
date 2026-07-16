# Reviewer concern map

This is a routing index, not a substitute for the original reviews. Before drafting a response or declaring a concern resolved, inspect the immutable review export and the live OpenReview forum when access is available.

## Decision synthesis

### TH-1 — Theory–implementation correspondence

The decision and multiple reviewers identify a gap between the Bochner/Mercer/eigendecomposition narrative and the implemented MLP-produced scalar frequency weights. The revision must either establish the correspondence rigorously or narrow the theoretical claim.

Evidence expected: explicit definitions, assumptions, derivation, mapping from equations to code, and a claim whose strength matches the proof.

### TH-2 — Stationarity metric justification

The score based on `mu/sigma` lacks a first-principles justification and clear conditions under which it measures the desired cross-sample stationarity.

Evidence expected: definition, interpretation, edge cases, comparison with credible alternatives, and an ablation tied to artifacts.

### TH-3 — Coverage of temporal conditions

Claims about integrating over “all possible time structures” depend on the training set representing the relevant support. Reviewers ask what happens when test-time temporal structure lies outside the support of the training distribution.

Evidence expected: corrected scope, stated assumption, OOD limitation, and robustness evidence where available.

## Method and positioning

### MT-1 — Relationship to normalization and filtering

Explain precisely how TIFO differs from and complements RevIN, SAN, FAN, FilterNet, and related frequency-domain filtering or normalization methods. Do not rely on broad “normalization is insufficient” claims without evidence.

### MT-2 — Diagram/algorithm/implementation consistency

The figure appears to separate stationary and non-stationary components, while the described implementation produces a single modulation weight. Algorithm 1 and the actual steps must agree with the diagram, equations, and code.

### MT-3 — TIFO plus SAN

Clarify why TIFO and SAN can be applied together, whether they act on different mechanisms, and what the TIFO* comparison means. Avoid implying two identical normalization operations.

### MT-4 — Initialization and inference updates

Explain why the proposed starting point is preferable to random initialization, the robustness/variance trade-off, and whether online or EMA updates are needed under drift.

## Experimental evidence

### EX-1 — Fairness and large gains

Large reported gains, especially on ETTm2, require a transparent apples-to-apples setup, original-backbone rows, matched training protocol, uncertainty across runs, and an explanation of unusually weak baseline numbers where applicable.

### EX-2 — Strong and recent baselines

Multiple reviewers consider the baseline set weak and request stronger recent 2025–2026 methods. Select baselines by methodological relevance and reproducibility; do not add names without runnable or citable evidence.

### EX-3 — Evidence for reduced shift

Forecasting accuracy alone does not prove that TIFO reduces distribution shift or learns stationarity-aware representations. Connect the claim to direct train–test spectral-distance measurements, controlled ablations, and interpretable learned weights.

### EX-4 — Frequency-design ablations

Resolve concerns about FFT resolution, sampling-rate interpretation, windowing, overlap, zero padding, reconstruction, phase distortion, and boundary effects. Ensure every reported setting has a real result artifact.

### EX-5 — Generality

One reviewer asks about use beyond long-term forecasting. Treat broader classification/general feature-enhancement claims as optional unless supported by experiments; do not expand scope merely to answer the question.

## Presentation and reproducibility

### PR-1 — Tables and cross-references

Repair broken or placeholder references, include missing original-backbone results, and ensure bold/underline conventions match the actual best and second-best values.

### PR-2 — Structure and repetition

Reduce overlap in the distribution-shift and `p(x|t)` discussion. Keep problem definition, motivation, method, and theory roles distinct.

### PR-3 — Language and notation

Repair grammatical errors, incomplete sentences, undefined symbols, sampling-frequency terminology, and inconsistent naming.

### PR-4 — Reproducibility

Document datasets, splits, horizons, seeds/runs, hyperparameters, implementation, computational cost, and artifact locations sufficiently for verification.

## Reviewer routing

- Decision/meta-review: TH-1, TH-2, EX-2, PR-1.
- Reviewer JwDV: TH-1, TH-2, MT-1, EX-1.
- Reviewer 2Q34: MT-3, TH-3, EX-1, PR-1.
- Reviewer JIEp: TH-3, MT-4, EX-4, PR-1, PR-3.
- Reviewer 54Tf: MT-2, PR-2, EX-5.
- Reviewer eBmV: MT-1, TH-1, EX-2, EX-3.
