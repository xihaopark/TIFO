#!/usr/bin/env python3
"""Fast invariant checks for the controlled spectral-shift intervention."""

from __future__ import annotations

import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from exp.exp_long_term_forecasting import apply_controlled_spectral_shift  # noqa: E402


def main() -> None:
    generator = torch.Generator().manual_seed(2027)
    batch_x = torch.randn(2, 96, 7, generator=generator)
    batch_y = torch.randn(2, 144, 7, generator=generator)
    batch_y[:, :48, :] = batch_x[:, -48:, :]

    unchanged_x, unchanged_y = apply_controlled_spectral_shift(
        batch_x, batch_y, 48, 96, 0.0
    )
    assert torch.equal(unchanged_x, batch_x)
    assert torch.equal(unchanged_y, batch_y)

    shifted_x, shifted_y = apply_controlled_spectral_shift(
        batch_x, batch_y, 48, 96, 0.5
    )
    assert shifted_x.shape == batch_x.shape
    assert shifted_y.shape == batch_y.shape
    assert torch.allclose(shifted_y[:, :48, :], shifted_x[:, -48:, :], atol=1e-6)
    assert torch.isfinite(shifted_x).all() and torch.isfinite(shifted_y).all()
    assert not torch.allclose(shifted_x, batch_x)
    print("controlled spectral shift invariants: ok")


if __name__ == "__main__":
    main()
