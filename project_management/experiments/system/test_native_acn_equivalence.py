#!/usr/bin/env python3
"""Verify the native ACN layer against the pinned official implementation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from layers.PluginNormalization import AdaptiveChannelNorm  # noqa: E402


def load_official_class():
    path = ROOT / "third_party/CN-official/layers/Transformer_EncDec_ACN.py"
    spec = importlib.util.spec_from_file_location("official_acn_layer", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.ChannelwiseLayerNorm


def main() -> None:
    torch.manual_seed(1729)
    channels, features, temperature = 7, 32, 0.1
    official = load_official_class()(channels, features, temperature)
    native = AdaptiveChannelNorm(channels, features, temperature)
    with torch.no_grad():
        native.local_scale.copy_(official.weighted_norm.weight)
        native.local_bias.copy_(official.weighted_norm.bias)
        native.global_scale.copy_(official.weighted_norm.weight_global)
        native.global_bias.copy_(official.weighted_norm.bias_global)
    sample = torch.randn(5, channels, features)
    torch.testing.assert_close(
        native(sample), official(sample), rtol=1e-6, atol=1e-6
    )
    print("native ACN matches the pinned official normalization operator")


if __name__ == "__main__":
    main()
