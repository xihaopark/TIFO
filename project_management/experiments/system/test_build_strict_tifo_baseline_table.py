#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_strict_tifo_baseline_table.py")
SPEC = importlib.util.spec_from_file_location("strict_table", MODULE_PATH)
STRICT_TABLE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(STRICT_TABLE)


def evidence(tifo_mse=0.1, tifo_mae=0.2):
    rows = []
    for method, mse, mae in (
        ("TIFO", tifo_mse, tifo_mae),
        ("ACN", 0.2, 0.3),
        ("WDAN", 0.3, 0.4),
    ):
        for seed in (2021, 2022, 2023):
            rows.append({
                "dataset": "ETTm1",
                "pred_len": 96,
                "method": method,
                "seed": seed,
                "mse": mse,
                "mae": mae,
                "host": "ACN" if method == "TIFO" else "standalone",
            })
    return rows


class StrictTableTest(unittest.TestCase):
    def test_renders_only_tifo_acn_wdan_with_tifo_first(self):
        cells, summary = STRICT_TABLE.summarize(evidence())
        STRICT_TABLE.enforce_tifo_all_win(cells, summary)
        tex, markdown = STRICT_TABLE.render(cells, summary)
        self.assertIn("ETTm1 & 96", tex)
        self.assertIn("| ETTm1 | 96 | ACN |", markdown)
        self.assertEqual(STRICT_TABLE.METHODS, ("TIFO", "ACN", "WDAN"))

    def test_rejects_any_tifo_metric_loss(self):
        cells, summary = STRICT_TABLE.summarize(evidence(tifo_mae=0.35))
        with self.assertRaises(SystemExit) as caught:
            STRICT_TABLE.enforce_tifo_all_win(cells, summary)
        self.assertIn("TIFO is not strictly best", str(caught.exception))
        self.assertIn("MAE", str(caught.exception))

    def test_rejects_missing_seed(self):
        rows = [row for row in evidence() if not (row["method"] == "WDAN" and row["seed"] == 2023)]
        with self.assertRaises(SystemExit) as caught:
            STRICT_TABLE.summarize(rows)
        self.assertIn("expected exactly seeds", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
