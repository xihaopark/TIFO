#!/usr/bin/env python3

import unittest
from types import SimpleNamespace

import torch

from exp.exp_long_term_forecasting import Exp_Long_Term_Forecast


class WeightedForecastingLossTest(unittest.TestCase):
    def criterion(self, weight):
        instance = object.__new__(Exp_Long_Term_Forecast)
        instance.args = SimpleNamespace(mae_loss_weight=weight)
        return instance._select_criterion()

    def test_zero_weight_is_plain_mse(self):
        prediction = torch.tensor([1.0, 3.0])
        target = torch.tensor([0.0, 1.0])
        self.assertAlmostEqual(self.criterion(0.0)(prediction, target).item(), 2.5)

    def test_positive_weight_adds_l1(self):
        prediction = torch.tensor([1.0, 3.0])
        target = torch.tensor([0.0, 1.0])
        self.assertAlmostEqual(self.criterion(0.5)(prediction, target).item(), 3.25)

    def test_negative_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            self.criterion(-0.1)


if __name__ == '__main__':
    unittest.main()
