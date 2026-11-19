"""Dataset-level TIFO stationarity statistics and input transformation.

The historical operator is preserved for result reproducibility.  The
Hermitian variants use the non-redundant real FFT so independently learned
real/imaginary coefficient scales reconstruct a real sequence without dropping
an imaginary residual.  TIFO does not transform the backbone prediction.
"""

from __future__ import annotations

import torch
import torch.nn as nn


def _tifo_fft_size(args) -> int:
    """Return the FFT size after optional right-side zero padding."""

    ratio = float(getattr(args, "tifo_zero_pad_ratio", 0.0))
    if ratio < 0:
        raise ValueError("tifo_zero_pad_ratio must be non-negative")
    return int(args.seq_len) + int(int(args.seq_len) * ratio)


class GlobalMaskCalculator:
    """Compute S(k, c) = mean_i A_i(k, c) / std_i A_i(k, c)."""

    def __init__(self, args, device):
        self.args = args
        self.device = torch.device(device)

    def compute_global_statistics(self, loader):
        channels = self.args.enc_in
        variant = getattr(self.args, "tifo_variant", "historical")
        fft_size = _tifo_fft_size(self.args)
        frequencies = fft_size if variant in {"historical", "historical_adaptive", "free_historical"} else fft_size // 2 + 1
        amp_sum = torch.zeros(frequencies, channels, device=self.device)
        amp2_sum = torch.zeros_like(amp_sum)
        sample_count = 0
        # Robust control: median / scaled MAD over a sample of
        # training windows (the training loader is shuffled).
        robust = getattr(self.args, "tifo_score_mode", "data") == "robust"
        robust_windows, robust_amps, kept = 2048, [], 0

        with torch.no_grad():
            for data in loader:
                x = data[0].float().to(self.device)  # [B, L, C]
                if variant in {"historical", "historical_adaptive", "free_historical"}:
                    amplitude = torch.abs(torch.fft.fft(x, n=fft_size, dim=1))
                else:
                    alignment = getattr(self.args, "tifo_score_alignment", "auto")
                    normalize_score_input = alignment == "normalized" or (
                        alignment == "auto"
                        and variant in {
                            "identity_prior",
                            "hermitian_aligned",
                            "hermitian_shared",
                            "hermitian_diagonal",
                            "pointwise",
                            "pointwise_ri",
                        }
                    )
                    if normalize_score_input:
                        # Match the per-window normalization applied by the
                        # iTransformer/PatchTST input path before TIFO.
                        x = (x - x.mean(1, keepdim=True)) / torch.sqrt(
                            x.var(1, keepdim=True, unbiased=False) + 1e-5
                        )
                    amplitude = torch.abs(torch.fft.rfft(x, n=fft_size, dim=1))
                amp_sum += amplitude.sum(0)
                amp2_sum += amplitude.square().sum(0)
                sample_count += x.size(0)
                if robust and kept < robust_windows:
                    take = amplitude[: robust_windows - kept].cpu()
                    robust_amps.append(take)
                    kept += take.size(0)

        if sample_count == 0:
            raise ValueError("cannot compute TIFO statistics from an empty loader")
        mean = amp_sum / sample_count
        variance = (amp2_sum / sample_count - mean.square()).clamp_min(0.0)
        std = torch.sqrt(variance + 1e-5)
        score = mean / (std + 1e-5)
        mode = getattr(self.args, "tifo_score_mode", "data")
        if mode == "robust":
            amps = torch.cat(robust_amps, 0)
            median = amps.median(0).values
            mad = 1.4826 * (amps - median).abs().median(0).values
            return (median / (torch.sqrt(mad.square() + 1e-5) + 1e-5)).to(score.device)
        if mode == "data":
            return score
        if mode == "ones":
            return torch.ones_like(score)
        if mode == "zeros":
            return torch.zeros_like(score)
        if mode == "energy":
            # Energy-only control: the mean amplitude (numerator of S).
            return mean
        if mode == "stab_resid":
            # Stability beyond energy: residual of log S regressed on log mu
            # within each channel, mapped back to a positive score.
            log_s = torch.log(score.clamp_min(1e-6))
            log_mu = torch.log(mean.clamp_min(1e-6))
            xc = log_mu - log_mu.mean(0, keepdim=True)
            yc = log_s - log_s.mean(0, keepdim=True)
            slope = (xc * yc).sum(0, keepdim=True) / (xc.square().sum(0, keepdim=True) + 1e-12)
            return torch.exp(yc - slope * xc)
        if mode == "random":
            # Match each channel's score mean/std with an input-independent
            # Gaussian vector; it carries no data information.
            generator = torch.Generator(device="cpu")
            generator.manual_seed(int(getattr(self.args, "tifo_score_seed", 1729)))
            noise = torch.randn(score.shape, generator=generator).to(score.device)
            return score.mean(0, keepdim=True) + score.std(0, keepdim=True) * noise
        if mode == "permuted":
            # Preserve each channel's score distribution while breaking its
            # association with frequency. A local generator avoids advancing
            # the model/training RNG stream.
            generator = torch.Generator(device="cpu")
            generator.manual_seed(int(getattr(self.args, "tifo_score_seed", 1729)))
            shuffled = torch.empty_like(score)
            for channel in range(channels):
                order = torch.randperm(frequencies, generator=generator).to(score.device)
                shuffled[:, channel] = score[order, channel]
            return shuffled
        raise ValueError(f"unsupported tifo_score_mode: {mode}")


def run_filter(args, loader, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return GlobalMaskCalculator(args, device).compute_global_statistics(loader)


class FrequencyDomainFilter(nn.Module):
    """Paper-aligned TIFO input transform with a stable identity initialization."""

    def __init__(self, args, global_mask_amp):
        super().__init__()
        if global_mask_amp is None:
            raise ValueError("TIFO requires dataset-level stationarity statistics")

        self.variant = getattr(args, "tifo_variant", "historical")
        self.fft_size = _tifo_fft_size(args)
        frequencies, channels = global_mask_amp.shape
        expected_frequencies = (
            self.fft_size
            if self.variant in {"historical", "historical_adaptive", "free_historical"}
            else self.fft_size // 2 + 1
        )
        if frequencies != expected_frequencies or channels != args.enc_in:
            raise ValueError(
                "invalid TIFO statistics shape: "
                f"got {tuple(global_mask_amp.shape)}, "
                f"expected {(expected_frequencies, args.enc_in)}"
            )

        self.seq_len = args.seq_len
        self.residual_alpha = float(getattr(args, "tifo_residual_alpha", 1.0))
        if not 0.0 <= self.residual_alpha <= 1.0:
            raise ValueError("tifo_residual_alpha must be in [0, 1]")
        self.register_buffer(
            "stationarity_score", global_mask_amp.detach().clone().float()
        )
        hidden_dim = int(getattr(args, "filter_dim", 512))
        self.weight_noise = float(getattr(args, "tifo_weight_noise", 0.0))
        if self.weight_noise < 0:
            raise ValueError("tifo_weight_noise must be non-negative")

        if self.variant == "free_historical":
            # Control: a learnable global spectral filter on the historical
            # full-FFT grid with independent real/imaginary gains and no
            # dependence on the stationarity score (identity initialization).
            trainable = bool(int(getattr(args, "tifo_trainable", 1)))
            self.free_real = nn.Parameter(torch.ones(frequencies, channels), requires_grad=trainable)
            self.free_imag = nn.Parameter(torch.ones(frequencies, channels), requires_grad=trainable)
            return

        if self.variant in {"pointwise", "pointwise_ri"}:
            # Each gain depends only on the score of its own (frequency,
            # channel) through one map shared by all frequencies and channels,
            # so the frequency-to-score correspondence is structural.  The gain
            # is non-negative and shared by the real and imaginary parts
            # (phase preserving), hence the operator is a circular convolution
            # with a positive-semidefinite translation-invariant kernel whose
            # Fourier eigenvalues are the gains.
            log_score = torch.log(self.stationarity_score.clamp_min(1e-6))
            centered = log_score - log_score.mean(0, keepdim=True)
            scale = centered.std(0, keepdim=True)
            feature = torch.where(
                scale > 1e-6, centered / scale.clamp_min(1e-6), torch.zeros_like(centered)
            )
            self.register_buffer("point_feature", feature.unsqueeze(-1))
            point_hidden = int(getattr(args, "tifo_point_hidden", 16))
            self.point_map = nn.Sequential(
                nn.Linear(1, point_hidden),
                nn.GELU(),
                nn.Linear(point_hidden, 1),
            )
            nn.init.zeros_(self.point_map[-1].weight)
            nn.init.zeros_(self.point_map[-1].bias)
            if self.variant == "pointwise_ri":
                # Diagnostic: separate signed real/imaginary gains, still a
                # function of each coefficient's own score (not PSD/phase-preserving).
                self.point_map_imag = nn.Sequential(
                    nn.Linear(1, point_hidden), nn.GELU(), nn.Linear(point_hidden, 1))
                nn.init.zeros_(self.point_map_imag[-1].weight)
                nn.init.zeros_(self.point_map_imag[-1].bias)
            return

        if self.variant in {
            "historical",
            "historical_adaptive",
            "hermitian_raw",
            "hermitian_aligned",
        }:
            dropout = float(getattr(args, "tifo_dropout", 0.5))

            def historical_mlp():
                return nn.Sequential(
                    nn.Linear(frequencies, hidden_dim),
                    nn.RReLU(),
                    nn.Dropout(dropout),
                    nn.Linear(hidden_dim, frequencies),
                )

            self.linear_r = historical_mlp()
            self.linear_i = historical_mlp()
            if self.variant == "historical_adaptive":
                # Sample-conditioned modulation: a zero-initialized
                # linear map of the window's own log-amplitude spectrum scales
                # the dataset-level weights by (1 + 0.5 tanh(.)), so training
                # starts exactly at the submitted operator.
                self.sample_map = nn.Linear(frequencies, frequencies)
                nn.init.zeros_(self.sample_map.weight)
                nn.init.zeros_(self.sample_map.bias)
            return

        prior_strength = float(getattr(args, "tifo_prior_strength", 0.0))
        if prior_strength < 0:
            raise ValueError("tifo_prior_strength must be non-negative")
        normalized_score = self.stationarity_score / self.stationarity_score.mean(
            dim=0, keepdim=True
        ).clamp_min(1e-5)
        score_prior = normalized_score.clamp_min(1e-4).pow(prior_strength)
        self.register_buffer("score_prior", score_prior.clamp(0.25, 4.0))

        if self.variant == "hermitian_diagonal":
            self.gain_limit = float(getattr(args, "tifo_gain_limit", 0.5))
            if self.gain_limit <= 0:
                raise ValueError("tifo_gain_limit must be positive")
            # One phase-preserving gain per frequency and channel.  The fixed
            # stationarity score scales the learnable log-gain, while zero
            # initialization keeps the complete transform exactly at identity.
            self.diagonal_log_gain = nn.Parameter(torch.zeros_like(self.stationarity_score))
            return

        def weight_mlp():
            network = nn.Sequential(
                nn.Linear(frequencies, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, frequencies),
            )
            # lambda = 2 * sigmoid(0) = 1, so TIFO starts as the identity.
            nn.init.zeros_(network[-1].weight)
            nn.init.zeros_(network[-1].bias)
            return network

        if self.variant == "hermitian_shared":
            self.shared_weight_mlp = weight_mlp()
        else:
            self.real_weight_mlp = weight_mlp()
            self.imag_weight_mlp = weight_mlp()

    def _perturb(self, weight):
        if self.training and self.weight_noise > 0:
            noise = torch.randn_like(weight) * self.weight_noise
            weight = weight * torch.exp(noise - 0.5 * self.weight_noise ** 2)
        return weight

    def frequency_weights(self):
        if self.variant == "free_historical":
            return self._perturb(self.free_real), self._perturb(self.free_imag)
        if self.variant == "pointwise_ri":
            real = 1.0 + 2.0 * torch.tanh(self.point_map(self.point_feature).squeeze(-1))
            imag = 1.0 + 2.0 * torch.tanh(self.point_map_imag(self.point_feature).squeeze(-1))
            return self._perturb(real), self._perturb(imag)
        if self.variant == "pointwise":
            shared_weight = 2.0 * torch.sigmoid(self.point_map(self.point_feature).squeeze(-1))
            shared_weight = self._perturb(shared_weight)
            return shared_weight, shared_weight
        if self.variant in {
            "historical",
            "historical_adaptive",
            "hermitian_raw",
            "hermitian_aligned",
        }:
            score_by_channel = self.stationarity_score.transpose(0, 1)
            return (
                self.linear_r(score_by_channel).transpose(0, 1),
                self.linear_i(score_by_channel).transpose(0, 1),
            )
        score_by_channel = self.stationarity_score.transpose(0, 1)
        prior = self.score_prior.transpose(0, 1)
        if self.variant == "hermitian_diagonal":
            log_gain = self.gain_limit * torch.tanh(self.diagonal_log_gain)
            log_gain = (log_gain * self.score_prior).clamp(-1.38629436, 1.38629436)
            shared_weight = self._perturb(torch.exp(log_gain))
            return shared_weight, shared_weight
        if self.variant == "hermitian_shared":
            shared_weight = prior * 2.0 * torch.sigmoid(
                self.shared_weight_mlp(score_by_channel)
            )
            shared_weight = shared_weight.transpose(0, 1)
            return shared_weight, shared_weight
        real_weight = prior * 2.0 * torch.sigmoid(
            self.real_weight_mlp(score_by_channel)
        )
        imag_weight = prior * 2.0 * torch.sigmoid(
            self.imag_weight_mlp(score_by_channel)
        )
        return real_weight.transpose(0, 1), imag_weight.transpose(0, 1)

    def forward(self, x):
        if x.size(1) != self.seq_len:
            raise ValueError(
                f"TIFO expected sequence length {self.seq_len}, got {x.size(1)}"
            )
        if self.residual_alpha == 0.0:
            return x
        full_grid = self.variant in {"historical", "historical_adaptive", "free_historical"}
        spectrum = (
            torch.fft.fft(x, n=self.fft_size, dim=1)
            if full_grid
            else torch.fft.rfft(x, n=self.fft_size, dim=1)
        )
        real_weight, imag_weight = self.frequency_weights()
        if self.variant == "historical_adaptive":
            log_amp = torch.log1p(spectrum.abs())  # [B, K, C]
            log_amp = (log_amp - log_amp.mean(1, keepdim=True)) / (log_amp.std(1, keepdim=True) + 1e-5)
            modulation = 1.0 + 0.5 * torch.tanh(self.sample_map(log_amp.transpose(1, 2)).transpose(1, 2))
            real_weight = real_weight.unsqueeze(0) * modulation
            imag_weight = imag_weight.unsqueeze(0) * modulation
        weighted_spectrum = torch.complex(
            spectrum.real * real_weight,
            spectrum.imag * imag_weight,
        )
        if full_grid:
            filtered = torch.fft.ifft(
                weighted_spectrum, n=self.fft_size, dim=1
            ).real
        else:
            filtered = torch.fft.irfft(weighted_spectrum, n=self.fft_size, dim=1)
        filtered = filtered[:, : self.seq_len, :]
        if self.residual_alpha == 1.0:
            return filtered
        return x + self.residual_alpha * (filtered - x)


def build_frequency_domain_filter(args, global_mask_amp):
    """Build TIFO without advancing the backbone/training RNG stream."""

    with torch.random.fork_rng(devices=[]):
        return FrequencyDomainFilter(args, global_mask_amp)
