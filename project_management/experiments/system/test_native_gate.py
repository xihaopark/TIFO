#!/usr/bin/env python3
"""Fast correctness gate for the native Ori/TIFO experiment path."""

from __future__ import annotations

import random
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from data_provider.data_factory import data_provider  # noqa: E402
from models import DLinear, PatchTST, iTransformer  # noqa: E402
from utils.frequency_domain_filter import (  # noqa: E402
    FrequencyDomainFilter,
    run_filter,
)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_args(
    method: str,
    tifo_variant: str = "identity_prior",
    tifo_zero_pad_ratio: float = 0.0,
    tifo_residual_alpha: float = 1.0,
) -> SimpleNamespace:
    return SimpleNamespace(
        task_name="long_term_forecast",
        data="ETTm2",
        root_path=str(REPO_ROOT / "dataset/ETT-small"),
        data_path="ETTm2.csv",
        features="M",
        target="OT",
        freq="t",
        embed="timeF",
        seasonal_patterns="Monthly",
        seq_len=96,
        label_len=48,
        pred_len=96,
        enc_in=7,
        dec_in=7,
        c_out=7,
        batch_size=8,
        num_workers=0,
        augmentation_ratio=0,
        method=method,
        tifo_variant=tifo_variant,
        tifo_dropout=0.5,
        tifo_zero_pad_ratio=tifo_zero_pad_ratio,
        tifo_residual_alpha=tifo_residual_alpha,
        filter_dim=64,
        d_model=32,
        d_ff=32,
        e_layers=1,
        n_heads=4,
        factor=1,
        dropout=0.0,
        activation="gelu",
        output_attention=False,
        moving_avg=25,
        patch_len=16,
        stride=8,
    )


def assert_paired_initialization(mask: torch.Tensor) -> None:
    seed_everything(2021)
    ori = iTransformer.Model(make_args("ori"), None)
    ori_next_random = torch.rand(8)

    seed_everything(2021)
    tifo = iTransformer.Model(make_args("tifo"), mask)
    tifo_next_random = torch.rand(8)

    ori_state = ori.state_dict()
    tifo_state = tifo.state_dict()
    shared_keys = [key for key in ori_state if key in tifo_state]
    for key in shared_keys:
        if not torch.equal(ori_state[key], tifo_state[key]):
            raise AssertionError(f"paired backbone initialization differs at {key}")
    torch.testing.assert_close(ori_next_random, tifo_next_random, rtol=0, atol=0)


def assert_yamabuki_candidates(device: torch.device) -> None:
    """Check the alpha-shrinkage and zero-padding candidates imported from server 25."""

    padded_args = make_args(
        "tifo", "historical", tifo_zero_pad_ratio=1.0
    )
    synthetic_loader = [
        (torch.randn(3, padded_args.seq_len, padded_args.enc_in),)
        for _ in range(2)
    ]
    padded_mask = run_filter(padded_args, synthetic_loader, device)
    expected_mask_shape = (padded_args.seq_len * 2, padded_args.enc_in)
    if padded_mask.shape != expected_mask_shape or not torch.isfinite(padded_mask).all():
        raise AssertionError(
            "zero-padded TIFO returned invalid statistics: "
            f"shape={tuple(padded_mask.shape)} expected={expected_mask_shape}"
        )
    padded_filter = FrequencyDomainFilter(padded_args, padded_mask).to(device)
    x = torch.randn(
        2, padded_args.seq_len, padded_args.enc_in, device=device, requires_grad=True
    )
    output = padded_filter(x)
    if output.shape != x.shape or not torch.isfinite(output).all():
        raise AssertionError("zero-padded TIFO returned an invalid output")
    output.square().mean().backward()
    if not any(
        parameter.grad is not None and torch.isfinite(parameter.grad).all()
        for parameter in padded_filter.parameters()
        if parameter.requires_grad
    ):
        raise AssertionError("zero-padded TIFO did not produce finite gradients")

    identity_args = make_args(
        "tifo",
        "historical",
        tifo_zero_pad_ratio=1.0,
        tifo_residual_alpha=0.0,
    )
    identity_filter = FrequencyDomainFilter(identity_args, padded_mask).to(device)
    identity_input = torch.randn_like(x.detach())
    torch.testing.assert_close(
        identity_filter(identity_input), identity_input, rtol=0, atol=0
    )
    print("server-25 candidates ok: padded FFT shape/gradient and alpha=0 identity")


def main() -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("native gate requires CUDA")
    device = torch.device("cuda:0")
    capability = torch.cuda.get_device_capability(device)
    probe = torch.randn(64, 64, device=device, requires_grad=True)
    probe.square().mean().backward()
    print(
        f"cuda ok: {torch.cuda.get_device_name(device)} capability={capability} "
        f"torch={torch.__version__}"
    )
    assert_yamabuki_candidates(device)

    args = make_args("tifo")
    _, mask_loader = data_provider(args, "train", shuffle_override=False)
    mask = run_filter(args, mask_loader, device)
    if mask.shape != (49, 7) or not torch.isfinite(mask).all():
        raise AssertionError(f"invalid global statistics: shape={tuple(mask.shape)}")
    print(
        "global statistics ok: "
        f"shape={tuple(mask.shape)} min={mask.min().item():.6f} "
        f"max={mask.max().item():.6f}"
    )

    transform = FrequencyDomainFilter(args, mask).to(device)
    x = torch.randn(4, args.seq_len, args.enc_in, device=device, requires_grad=True)
    transformed = transform(x)
    torch.testing.assert_close(transformed, x, rtol=1e-5, atol=1e-5)
    transformed.square().mean().backward()
    trainable_gradients = [
        parameter.grad for parameter in transform.parameters() if parameter.requires_grad
    ]
    if not any(gradient is not None and torch.isfinite(gradient).all() for gradient in trainable_gradients):
        raise AssertionError("TIFO did not produce finite trainable gradients")
    print("TIFO operator ok: real output, identity initialization, finite gradient")

    assert_paired_initialization(mask.cpu())
    print("paired RNG ok: Ori/TIFO backbone parameters and subsequent RNG match")

    historical_args = make_args("tifo", "historical")
    _, historical_mask_loader = data_provider(
        historical_args, "train", shuffle_override=False
    )
    historical_mask = run_filter(historical_args, historical_mask_loader, device)
    if historical_mask.shape != (96, 7) or not torch.isfinite(historical_mask).all():
        raise AssertionError(
            f"invalid historical statistics: shape={tuple(historical_mask.shape)}"
        )
    _, train_loader = data_provider(historical_args, "train")
    batch_x, batch_y, batch_x_mark, batch_y_mark = next(iter(train_loader))
    batch_x = batch_x.float().to(device)
    batch_y = batch_y.float().to(device)
    batch_x_mark = batch_x_mark.float().to(device)
    batch_y_mark = batch_y_mark.float().to(device)
    dec_inp = torch.cat(
        [
            batch_y[:, : historical_args.label_len],
            torch.zeros_like(batch_y[:, -historical_args.pred_len :]),
        ],
        dim=1,
    )
    for model_module in (DLinear, PatchTST, iTransformer):
        seed_everything(2021)
        model = model_module.Model(historical_args, historical_mask).float().to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
        optimizer.zero_grad()
        output, _ = model(batch_x, batch_x_mark, dec_inp, batch_y_mark)
        loss = torch.nn.functional.mse_loss(
            output, batch_y[:, -historical_args.pred_len :]
        )
        loss.backward()
        optimizer.step()
        if not torch.isfinite(loss):
            raise AssertionError(
                f"{model_module.__name__} one-step ETTm2 loss is not finite"
            )
        print(
            f"historical TIFO {model_module.__name__} optimizer step ok: "
            f"loss={loss.item():.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
