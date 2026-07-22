# Minimal theory rewrite proposal for TIFO

Date: 2026-07-22

Status: **proposal only; not applied to the manuscript**. The current theory is
author-frozen and must not be edited without explicit approval.

## Why replacement is necessary

The implemented module computes a fixed training-set statistic per frequency and
channel, maps it through an MLP to globally shared spectral gains, applies those
gains to Fourier coefficients, and minimizes forecasting loss. It does not
construct a positive-definite kernel, solve an integral eigenproblem, constrain
the gains to be nonnegative ordered eigenvalues, or learn kernel eigenfunctions.
Consequently, these current claims are not supportable:

- applying a Fourier transform to the dataset guarantees an implicit kernel;
- the MLP outputs are kernel eigenvalues;
- learning those outputs is equivalent to learning a kernel;
- integrating over observed training times represents all possible time
  structures or guarantees shift robustness;
- the resulting representation should theoretically outperform normalization.

Bochner's and Mercer's theorems are valid mathematical results, but the current
manuscript does not satisfy the chain of assumptions needed to connect them to
the implemented loss and parameters. Keeping that chain is higher risk than
presenting a smaller, correct contribution.

## Proposed claim boundary

The theory should establish only what the implementation supports:

1. The DFT provides a fixed, orthogonal coordinate system in which variation can
   be measured per frequency.
2. `S(k,c) = mu(A(k,c)) / (sigma(A(k,c)) + epsilon)` is a dimensionless empirical
   energy-to-dispersion descriptor estimated from training windows. It is a
   heuristic conditioning feature, not an optimal stationarity estimator.
3. `lambda = MLP(S)` is a set of globally shared spectral gains optimized jointly
   with the forecasting backbone. The forecasting loss, not a kernel objective,
   determines whether high- or low-score components are emphasized.
4. With one-sided rFFT coefficients, TIFO applies separate real-valued gains to
   the real and imaginary coefficient arrays. Passing the resulting one-sided
   complex array to iRFFT produces a real-valued sequence by construction. This
   is the only clean formal property needed for the operator.
5. "Time-invariant" means that the learned gains are fixed across test samples
   and require no online update. It does not mean invariance to every unseen
   temporal distribution.

## Replacement text skeleton

### Motivation and definition

> Let `A_i(k,c)` denote the amplitude of frequency bin `k` and channel `c` in
> training window `i`. We summarize its cross-window behavior by
> `S(k,c)=mu_i[A_i(k,c)]/(sigma_i[A_i(k,c)]+epsilon)`. A large value indicates
> that a component has high average energy relative to its variation across the
> observed training windows. This ratio is used as a compact empirical descriptor,
> not as an optimal or complete measure of stationarity.

### Operator interpretation

> TIFO maps the fixed training statistic `S` to spectral gains
> `lambda_theta = MLP_theta(S)`. These gains are shared by all samples and are
> learned jointly with the forecasting backbone under the forecasting loss. The
> Fourier basis separates the input into frequency coordinates, while the learned
> gains determine how strongly each coordinate is passed to the backbone. TIFO
> therefore constitutes a dataset-conditioned global spectral adapter; it does
> not perform kernel eigendecomposition and its gains should not be interpreted
> as kernel eigenvalues.

### Narrow formal statement

> **Proposition (real-valued reconstruction).** Let `X` be real-valued and let
> `Z=rFFT(X)`. For real-valued gain arrays `g_r` and `g_i` with the same
> one-sided spectral shape, define
> `Z_tilde = g_r odot Re(Z) + i g_i odot Im(Z)`. Then
> `X_tilde=iRFFT(Z_tilde, n=L)` is real-valued. Moreover, if `g_r=g_i=1`, then
> `X_tilde=X` up to numerical precision.
>
> **Justification.** The one-sided rFFT representation implicitly specifies the
> conjugate-symmetric negative-frequency coefficients required for a real signal.
> The inverse rFFT constructs those omitted coefficients from any supplied
> one-sided complex array, so it maps the separately reweighted real and imaginary
> parts to a real sequence. Unit gains recover the original one-sided spectrum.

### Scope

> Because `S` and the gains are estimated from the training distribution, TIFO
> assumes that relevant test-time spectral behavior is sufficiently represented
> in training. The method provides no guarantee under arbitrary unseen shifts.
> The controlled spectral intervention and weight-alignment diagnostics test the
> intended behavior empirically and define, rather than remove, this limitation.

## Exact manuscript-level edits implied after approval

- Abstract: remove "all possible time structures" and "implicitly induces
  eigen-decomposition"; replace with dataset-level spectral conditioning.
- Introduction/contributions: remove kernel/eigenvalue claims and define the
  plug-in contribution narrowly.
- Method: retain the score, global MLP gains, DFT/rFFT, inverse transform, and
  end-to-end objective; consistently call `lambda` gains or weights.
- Theory subsection: replace the Bochner/Mercer material with the four short
  blocks above.
- Experiments/discussion: keep the weight-alignment and controlled-shift evidence
  as empirical diagnostics, with the existing Traffic and OOD caveats.
- Conclusion: avoid "solves distribution shift" and "universal" language.

This replacement should reduce page usage and directly answers the AC's central
theory--implementation concern without requiring a new theorem or experiment.
