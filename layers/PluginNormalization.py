"""Native implementations of comparison plug-ins for matched experiments."""

from __future__ import annotations

import torch
import torch.nn as nn


class AdaptiveChannelNorm(nn.Module):
    """Adaptive channel normalization used by the ACN comparison.

    Channel embeddings are normalized across features. Cosine similarity then
    mixes trainable channel-wise affine parameters before applying them to the
    normalized embeddings. This keeps the backbone and training loop identical
    to Ori/TIFO while changing only the normalization plug-in.
    """

    def __init__(
        self,
        channels: int,
        features: int,
        temperature: float,
        eps: float = 1e-5,
    ) -> None:
        super().__init__()
        if temperature <= 0:
            raise ValueError("ACN temperature must be positive")
        self.temperature = float(temperature)
        self.eps = float(eps)
        self.channels = int(channels)
        self.local_scale = nn.Parameter(torch.ones(channels, features))
        self.local_bias = nn.Parameter(torch.zeros(channels, features))
        self.global_scale = nn.Parameter(torch.ones(channels, features))
        self.global_bias = nn.Parameter(torch.ones(channels, features))
        self.context_norm = nn.LayerNorm(features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        variables = x[:, : self.channels, :]
        mean = variables.mean(dim=-1, keepdim=True)
        variance = variables.var(dim=-1, keepdim=True, unbiased=False)
        normalized = (variables - mean) / torch.sqrt(variance + self.eps)
        unit = normalized / normalized.norm(dim=-1, keepdim=True).clamp_min(
            self.eps
        )
        affinity = torch.matmul(unit, unit.transpose(1, 2))
        mixing = torch.softmax(affinity / self.temperature, dim=-1)
        scale = torch.matmul(mixing, self.local_scale.unsqueeze(0).expand(
            x.size(0), -1, -1
        )) * self.global_scale.unsqueeze(0)
        bias = torch.matmul(mixing, self.local_bias.unsqueeze(0).expand(
            x.size(0), -1, -1
        )) * self.global_bias.unsqueeze(0)
        normalized_variables = scale * normalized + bias
        if x.size(1) == self.channels:
            return normalized_variables
        if x.size(1) < self.channels:
            raise ValueError(
                f"ACN expected at least {self.channels} tokens, got {x.size(1)}"
            )
        return torch.cat(
            (normalized_variables, self.context_norm(x[:, self.channels :, :])),
            dim=1,
        )
