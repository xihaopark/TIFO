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
        tifo_score_mode="data",
        tifo_score_seed=1729,
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

    seed_everything(2021)
    acn = iTransformer.Model(make_args("acn"), None)
    for key in shared_keys:
        if key.startswith("encoder.attn_layers") and ".norm" in key:
            continue
        if key in acn.state_dict() and not torch.equal(ori_state[key], acn.state_dict()[key]):
            raise AssertionError(f"paired Ori/ACN backbone initialization differs at {key}")

    sample = torch.randn(4, 96, 7)
    sample_mark = torch.randn(4, 96, 4)
    output, _ = acn(sample, sample_mark, None, None)
    if output.shape != (4, 96, 7) or not torch.isfinite(output).all():
        raise AssertionError("native ACN returned an invalid output")
    output.square().mean().backward()
    invalid_gradients = [
        name
        for name, parameter in acn.named_parameters()
        if "norm" in name
        and parameter.requires_grad
        and (parameter.grad is None or not torch.isfinite(parameter.grad).all())
    ]
    if invalid_gradients:
        raise AssertionError(
            "native ACN normalization parameters lack finite gradients: "
            + ", ".join(invalid_gradients)
        )
    print("native ACN ok: paired backbone initialization and finite gradients")

    composition_args = make_args("acn_tifo", "hermitian_diagonal")
    composition_args.acn_temperature = 0.1
    composition_args.tifo_gain_limit = 0.5
    composition = iTransformer.Model(composition_args, mask)
    output, _ = composition(sample, sample_mark, None, None)
    if output.shape != (4, 96, 7) or not torch.isfinite(output).all():
        raise AssertionError("native ACN+TIFO returned an invalid output")
    output.square().mean().backward()
    required = [
        parameter.grad
        for name, parameter in composition.named_parameters()
        if "norm" in name or "diagonal_log_gain" in name
    ]
    if not required or not all(
        gradient is not None and torch.isfinite(gradient).all()
        for gradient in required
    ):
        raise AssertionError("native ACN+TIFO lacks finite plug-in gradients")
    print("native ACN+TIFO ok: valid output and finite plug-in gradients")

    wdan_args = make_args("wdan")
    wdan_args.wdan_levels = 2
    wdan_args.wdan_window = 5
    wdan_args.wdan_d_model = 32
    wdan_args.wdan_d_ff = 32
    wdan_args.wdan_layers = 1
    wdan_args.wdan_dropout = 0.0
    seed_everything(2021)
    wdan = iTransformer.Model(wdan_args, None)
    output, statistics = wdan(sample, sample_mark, None, None)
    if output.shape != (4, 96, 7) or not torch.isfinite(output).all():
        raise AssertionError("native WDAN returned an invalid output")
    loss = output.square().mean() + wdan.wdan_statistics_loss(statistics, sample)
    loss.backward()
    if not all(
        parameter.grad is not None and torch.isfinite(parameter.grad).all()
        for parameter in wdan.wdan_adapter.parameters()
        if parameter.requires_grad
    ):
        raise AssertionError("native WDAN adapter lacks finite gradients")
    print("native WDAN ok: real forecast, auxiliary statistics, finite gradients")


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


def assert_hermitian_candidates(device: torch.device) -> None:
    """Check real reconstruction and finite gradients for both new variants."""

    synthetic_loader = [(torch.randn(3, 96, 7),) for _ in range(2)]
    for variant in (
        "hermitian_raw",
        "hermitian_aligned",
        "hermitian_shared",
        "hermitian_diagonal",
    ):
        args = make_args("tifo", variant)
        mask = run_filter(args, synthetic_loader, device)
        if mask.shape != (49, 7) or not torch.isfinite(mask).all():
            raise AssertionError(
                f"{variant} returned invalid statistics: {tuple(mask.shape)}"
            )
        transform = FrequencyDomainFilter(args, mask).to(device)
        x = torch.randn(2, 96, 7, device=device, requires_grad=True)
        output = transform(x)
        if output.shape != x.shape or output.is_complex() or not torch.isfinite(output).all():
            raise AssertionError(f"{variant} returned an invalid real output")
        output.square().mean().backward()
        if not any(
            parameter.grad is not None and torch.isfinite(parameter.grad).all()
            for parameter in transform.parameters()
            if parameter.requires_grad
        ):
            raise AssertionError(f"{variant} did not produce finite gradients")
        if variant in {"hermitian_shared", "hermitian_diagonal"}:
            real_gain, imag_gain = transform.frequency_weights()
            torch.testing.assert_close(real_gain, imag_gain, rtol=0, atol=0)
        if variant == "hermitian_diagonal":
            torch.testing.assert_close(
                real_gain, torch.ones_like(real_gain), rtol=0, atol=0
            )
            with torch.no_grad():
                transform.diagonal_log_gain.fill_(0.2)
            conditioned_gain, _ = transform.frequency_weights()
            if torch.equal(conditioned_gain, torch.ones_like(conditioned_gain)):
                raise AssertionError("diagonal TIFO gain ignores its learned parameter")
            torch.testing.assert_close(output, x, rtol=1e-5, atol=1e-5)
    print("Hermitian TIFO candidates ok: real output and finite gradients")


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
    assert_hermitian_candidates(device)

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

    permuted_args = make_args("tifo")
    permuted_args.tifo_score_mode = "permuted"
    comparison_state = torch.random.get_rng_state()
    data_control_mask = run_filter(args, mask_loader, device)
    after_data_control = torch.random.get_rng_state()
    torch.random.set_rng_state(comparison_state)
    permuted_mask = run_filter(permuted_args, mask_loader, device)
    after_permutation = torch.random.get_rng_state()
    if not torch.equal(after_data_control, after_permutation):
        raise AssertionError("permuted-score control consumed extra training RNG")
    if torch.equal(data_control_mask, permuted_mask):
        raise AssertionError("permuted-score control did not change frequency alignment")
    torch.testing.assert_close(
        torch.sort(data_control_mask, dim=0).values,
        torch.sort(permuted_mask, dim=0).values,
    )
    print("permuted-score control ok: marginals preserved and RNG isolated")

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
