#!/usr/bin/env python3
"""Fast correctness checks for the ACN+TIFO composition adapter."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import torch


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "third_party/CN-official/utils/tifo_adapter.py"
SPEC = importlib.util.spec_from_file_location("acn_tifo_adapter", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def args(alpha: float = 0.25):
    return SimpleNamespace(
        seq_len=96,
        enc_in=7,
        tifo_zero_pad_ratio=0.0,
        tifo_residual_alpha=alpha,
        filter_dim=32,
        tifo_dropout=0.0,
    )


def main() -> None:
    score = torch.rand(49, 7) + 0.1
    before = torch.random.get_rng_state()
    adapter = MODULE.build_tifo_adapter(args(), score)
    after = torch.random.get_rng_state()
    if not torch.equal(before, after):
        raise AssertionError("adapter construction advanced the backbone RNG stream")

    x = torch.randn(4, 96, 7, requires_grad=True)
    output = adapter(x)
    if output.shape != x.shape or not torch.isfinite(output).all() or output.is_complex():
        raise AssertionError("adapter returned an invalid real-valued tensor")
    output.square().mean().backward()
    if not all(parameter.grad is not None and torch.isfinite(parameter.grad).all()
               for parameter in adapter.parameters()):
        raise AssertionError("adapter parameters did not receive finite gradients")

    identity = MODULE.build_tifo_adapter(args(alpha=0.0), score)
    if not torch.equal(identity(x.detach()), x.detach()):
        raise AssertionError("zero residual strength is not an exact identity")
    print("ACN+TIFO adapter invariants: ok")


if __name__ == "__main__":
    main()
