#!/usr/bin/env python3
"""Forward/backward smoke tests for native ACN and WDAN on DLinear."""

from __future__ import annotations

from types import SimpleNamespace

import torch

from models.DLinear import Model


def config(method: str) -> SimpleNamespace:
    return SimpleNamespace(
        task_name="long_term_forecast",
        seq_len=96,
        pred_len=24,
        moving_avg=25,
        enc_in=7,
        method=method,
        acn_temperature=0.1,
        wdan_levels=2,
        wdan_window=5,
        wdan_d_model=16,
        wdan_d_ff=16,
        wdan_layers=0,
        wdan_dropout=0.1,
    )


def check(method: str) -> None:
    torch.manual_seed(7)
    model = Model(config(method), global_mask=None)
    x = torch.randn(3, 96, 7)
    output, auxiliary = model(x, None, None, None)
    assert output.shape == (3, 24, 7)
    assert torch.isfinite(output).all()
    output.square().mean().backward()
    gradients = [
        parameter.grad
        for parameter in model.parameters()
        if parameter.requires_grad and parameter.grad is not None
    ]
    assert gradients and all(torch.isfinite(gradient).all() for gradient in gradients)
    if method == "acn":
        assert model.acn_adapter.local_scale.grad is not None
    if method == "wdan":
        assert auxiliary is not None
        future = torch.randn(3, 24, 7)
        statistics_loss = model.wdan_statistics_loss(auxiliary, future)
        assert torch.isfinite(statistics_loss)


def main() -> None:
    check("acn")
    check("wdan")
    print("DLinear ACN/WDAN adapter smoke tests passed")


if __name__ == "__main__":
    main()
