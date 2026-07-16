"""Dataset-level TIFO stationarity statistics and input transformation.

The implementation mirrors the paper pipeline: compute a frequency-wise
stationarity score from the training split, learn independent real/imaginary
weights from that score, and transform each input back to the time domain before
the forecasting backbone.  TIFO does not transform the backbone prediction.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class GlobalMaskCalculator:
    """Compute S(k, c) = mean_i A_i(k, c) / std_i A_i(k, c)."""

    def __init__(self, args, device):
        self.args = args
        self.device = torch.device(device)

    def compute_global_statistics(self, loader):
        channels = self.args.enc_in
        frequencies = self.args.seq_len // 2 + 1
        amp_sum = torch.zeros(frequencies, channels, device=self.device)
        amp2_sum = torch.zeros_like(amp_sum)
        sample_count = 0

        with torch.no_grad():
            for data in loader:
                x = data[0].float().to(self.device)  # [B, L, C]
                x = (x - x.mean(1, keepdim=True)) / torch.sqrt(
                    x.var(1, keepdim=True, unbiased=False) + 1e-5
                )
                amplitude = torch.abs(torch.fft.rfft(x, dim=1))
                amp_sum += amplitude.sum(0)
                amp2_sum += amplitude.square().sum(0)
                sample_count += x.size(0)

        if sample_count == 0:
            raise ValueError("cannot compute TIFO statistics from an empty loader")
        mean = amp_sum / sample_count
        variance = (amp2_sum / sample_count - mean.square()).clamp_min(0.0)
        std = torch.sqrt(variance + 1e-5)
        return mean / (std + 1e-5)


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

        frequencies, channels = global_mask_amp.shape
        expected_frequencies = args.seq_len // 2 + 1
        if frequencies != expected_frequencies or channels != args.enc_in:
            raise ValueError(
                "invalid TIFO statistics shape: "
                f"got {tuple(global_mask_amp.shape)}, "
                f"expected {(expected_frequencies, args.enc_in)}"
            )

        self.seq_len = args.seq_len
        self.register_buffer(
            "stationarity_score", global_mask_amp.detach().clone().float()
        )
        hidden_dim = int(getattr(args, "filter_dim", 512))

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

        self.real_weight_mlp = weight_mlp()
        self.imag_weight_mlp = weight_mlp()

    def frequency_weights(self):
        score_by_channel = self.stationarity_score.transpose(0, 1)
        real_weight = 2.0 * torch.sigmoid(self.real_weight_mlp(score_by_channel))
        imag_weight = 2.0 * torch.sigmoid(self.imag_weight_mlp(score_by_channel))
        return real_weight.transpose(0, 1), imag_weight.transpose(0, 1)

    def forward(self, x):
        if x.size(1) != self.seq_len:
            raise ValueError(
                f"TIFO expected sequence length {self.seq_len}, got {x.size(1)}"
            )
        spectrum = torch.fft.rfft(x, dim=1)
        real_weight, imag_weight = self.frequency_weights()
        weighted_spectrum = torch.complex(
            spectrum.real * real_weight,
            spectrum.imag * imag_weight,
        )
        return torch.fft.irfft(weighted_spectrum, n=self.seq_len, dim=1)


def build_frequency_domain_filter(args, global_mask_amp):
    """Build TIFO without advancing the backbone/training RNG stream."""

    with torch.random.fork_rng(devices=[]):
        return FrequencyDomainFilter(args, global_mask_amp)
