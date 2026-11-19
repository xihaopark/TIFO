"""Helpers to rebuild a run's arguments, data and trained TIFO weights."""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _parser():
    source = (ROOT / "run.py").read_text()
    head = source.split("    args = parser.parse_args()")[0]
    body = "\n".join(line[4:] if line.startswith("    ") else line
                     for line in head.split("if __name__ == '__main__':", 1)[1].splitlines())
    namespace: dict = {}
    exec(compile(head.split("if __name__ == '__main__':", 1)[0] + "\n" + body, "run.py", "exec"), namespace)
    return namespace["parser"]


def run_args(run_id: str):
    record = json.loads((ROOT / "experiment_records" / run_id / "launch.json").read_text())
    args = _parser().parse_args(record["command"][2:])
    args.use_gpu = torch.cuda.is_available()
    args.use_multi_gpu = False
    args.gpu = 0
    return args


def checkpoint_path(run_id: str) -> Path:
    matches = glob.glob(str(ROOT / "checkpoints" / f"*_{run_id}_*" / "checkpoint.pth"))
    if len(matches) != 1:
        raise FileNotFoundError(f"{run_id}: expected one checkpoint, found {len(matches)}")
    return Path(matches[0])


def loaders(args, flag: str):
    from data_provider.data_factory import data_provider
    return data_provider(args, flag)


def trained_filter(run_id: str, device: str = "cpu"):
    """Return (args, FrequencyDomainFilter with trained weights, score S)."""
    from utils.frequency_domain_filter import GlobalMaskCalculator, build_frequency_domain_filter
    args = run_args(run_id)
    _, train_loader = loaders(args, "train")
    score = GlobalMaskCalculator(args, device).compute_global_statistics(train_loader)
    filt = build_frequency_domain_filter(args, score)
    state = torch.load(checkpoint_path(run_id), map_location=device)
    filt.load_state_dict({k[len("filter."):]: v for k, v in state.items() if k.startswith("filter.")})
    return args, filt.eval(), score
