"""Load the pinned WDAN statistics module for matched native-runner tests."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WDAN_ROOT = ROOT / "third_party/WDAN-official"


def build_wdan_adapter(args):
    if not WDAN_ROOT.is_dir():
        raise FileNotFoundError(
            "pinned WDAN checkout is required; run the baseline bootstrap first"
        )
    root = str(WDAN_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from nns.models.WDAN import Model as WDANModel

    return WDANModel(
        seq_len=int(args.seq_len),
        pred_len=int(args.pred_len),
        wavelet="haar",
        filter_learn=True,
        dwt_levels=int(getattr(args, "wdan_levels", 2)),
        window_len=int(getattr(args, "wdan_window", 5)),
        d_model=int(getattr(args, "wdan_d_model", 128)),
        d_ff=int(getattr(args, "wdan_d_ff", 128)),
        dropout=float(getattr(args, "wdan_dropout", 0.1)),
        ffn_layers=int(getattr(args, "wdan_layers", 1)),
    )
