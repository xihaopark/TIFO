# TIFO theory rewrite: exact application map

Date: 2026-07-22

Status: **ready to apply after author approval; no theory text has been changed**.

This map converts the existing proposal into source anchors and acceptance checks.
It deliberately changes no experiment, result, title, or method implementation.

## 1. Abstract

Anchor: the six active `\reviewtext` sentences beginning with “Normalization
methods constitute” and ending with “implicitly induces eigen-decomposition.”

Replace the unsupported question/eigendecomposition chain with:

> We study frequency-domain input adaptation for non-stationary time-series
> forecasting. TIFO computes a frequency/channel statistic from training
> windows, maps it to globally shared spectral gains, and reweights each input
> before an unchanged forecasting backbone. The gains are fixed at inference
> and require no online test-time update. They are learned under forecasting
> loss and are not interpreted as kernel eigenvalues.

Keep the existing verified experimental sentence immediately after this block.

## 2. Introduction and contributions

Anchor A: the block beginning “In this work, we propose to address distributional
shift” and ending with the two eigenfunction/eigenvalue sentences.

Required replacement logic:

1. Stage I computes only the dataset statistic `S`; it does not learn the MLP.
2. Stage II maps fixed `S` to real/imaginary gains and applies them to each input.
3. “Time-invariant” means the gains are training-data-derived, shared across test
   samples, fixed at inference, and require no online update.
4. Remove “all possible time conditions,” induced-kernel, eigendecomposition,
   and guaranteed distribution-shift mitigation language.

Anchor B: contribution items beginning with `\ding{182}`.

Replace the theoretical-framework claim with:

> We formulate TIFO as a dataset-conditioned global spectral adapter and state
> its real-valued reconstruction and identity properties for the rFFT/iRFFT
> implementation.

Retain the methodological and verified experimental contributions, but change
“handle” or “mitigate” causal wording to “adapt to” or “evaluate under.”

## 3. Method wording

The equations in Stage I and Stage II already match the code and remain. Apply
only these terminology changes:

- call `S` an empirical energy-to-dispersion descriptor, not an optimal
  stationarity estimator;
- call `lambda_r` and `lambda_i` spectral gains or weights, never eigenvalues;
- do not assert that a high score is forced to receive a high gain; the current
  alignment experiment evaluates that behavior empirically;
- preserve the implemented equation
  `Z_tilde = g_r(S) Re(Z) + i g_i(S) Im(Z)` and iRFFT reconstruction.

## 4. Replace the entire active theory subsection

Source range: from `\subsection{Theoretical Analysis}` through the closing brace
immediately before `\section{Experiments}`. Remove the active Assumption,
Bochner theorem, Mercer theorem, kernel equations, Fourier-eigenfunction
construction, and every claim that learning gains equals learning a kernel.

Use the following compact structure.

### Dataset-conditioned spectral coordinates

For training-window amplitude `A_i(k,c)`, define
`S(k,c)=mu_i[A_i(k,c)]/(sigma_i[A_i(k,c)]+epsilon)`. Explain that the DFT is a
fixed coordinate system and `S` summarizes observed cross-window behavior. It
does not integrate over all possible time conditions.

### Global spectral adapter

Define `g_r(S)=MLP_r(S)` and `g_i(S)=MLP_i(S)`. These unconstrained gains are
optimized jointly with the backbone under forecasting MSE and shared across
samples. No positive-definite kernel or eigenproblem is constructed.

### Proposition: real reconstruction and identity

For real `X`, let `Z=rFFT(X)` and
`Z_tilde=g_r odot Re(Z)+i g_i odot Im(Z)`. Then
`iRFFT(Z_tilde,n=L)` is real-valued. If both gains are one, the operator returns
`X` up to numerical precision. This follows from the one-sided representation
used by rFFT/iRFFT and is directly covered by the implementation tests.

### Scope

The statistic and gains are estimated from training data, so arbitrary unseen
spectral shifts are not covered by a guarantee. Treat the score ablation,
weight alignment, and controlled intervention as empirical evidence only.

## 5. Experiments and conclusion

- Rename RQ2 from “Addressing Distribution Shift” to “Conditioning and Shift
  Sensitivity.”
- Replace “Does learning lambda mitigate the distribution shift?” with “Does
  data-conditioned spectral reweighting provide useful conditioning and bounded
  behavior under the controlled spectral intervention?”
- In RQ3, call lambda spectral gains.
- In the conclusion, define the method as a training-data-conditioned spectral
  adapter and retain the current mixed-result limitation.

## 6. Acceptance checks after application

The rewrite is complete only if all checks pass:

1. No active source line says `all possible time`, `eigenvalue`,
   `eigendecomposition`, `Bochner`, `Mercer`, or `learning the kernel` in relation
   to TIFO.
2. Stage I and Stage II agree between Introduction, Method, figure discussion,
   and algorithm text.
3. The operator equation matches the two separate real/imaginary MLP paths in
   code.
4. “Time-invariant” is defined at first use and never means invariance to unseen
   distributions.
5. The PDF remains exactly one Summary of Changes page plus eight content pages.
6. The response marks the theory concern completed only after the compiled PDF
   contains the replacement.
