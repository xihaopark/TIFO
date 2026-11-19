"""TQNet (ICML 2025) with an optional TIFO input adapter.

The network body is copied from the official implementation
https://github.com/ACAT-SCUT/TQNet (Apache-2.0), commit 15e19cb,
``models/TQNet.py``. The official data loader supplies ``cycle_index`` =
(row index mod cycle). This repository's loaders do not, so the cycle phase is
recovered from the time features of the first input step; it differs from the
official index only by a constant offset, which relabels the learnable
temporal queries and leaves the model family unchanged. TIFO, when enabled, is
applied after the instance normalization, as in the other backbones.
"""

import torch
import torch.nn as nn

from utils.frequency_domain_filter import build_frequency_domain_filter


def cycle_phase(x_mark, cycle, freq):
    """Cycle phase of the first input step from timeF features in [-0.5, 0.5]."""
    first = x_mark[:, 0, :]
    if freq.startswith("t"):  # [minute, hour, dayofweek, ...]
        minute = torch.round((first[:, 0] + 0.5) * 59)
        hour = torch.round((first[:, 1] + 0.5) * 23)
        dow = torch.round((first[:, 2] + 0.5) * 6)
    else:  # [hour, dayofweek, ...]
        minute = torch.zeros_like(first[:, 0])
        hour = torch.round((first[:, 0] + 0.5) * 23)
        dow = torch.round((first[:, 1] + 0.5) * 6)
    minutes_of_week = dow * 1440 + hour * 60 + minute
    steps_per_day = {24: 24, 168: 24, 96: 96, 144: 144}[cycle]
    step = torch.div(minutes_of_week, 1440 // steps_per_day, rounding_mode="floor")
    return (step % cycle).long()


class Model(nn.Module):
    def __init__(self, configs, global_mask=None):
        super(Model, self).__init__()

        self.seq_len = configs.seq_len
        self.pred_len = configs.pred_len
        self.enc_in = configs.enc_in
        self.cycle_len = configs.cycle
        self.freq = configs.freq
        self.d_model = configs.d_model
        self.dropout = configs.dropout
        self.use_revin = configs.use_revin

        self.use_tq = True  # ablation parameter, default: True
        self.channel_aggre = True   # ablation parameter, default: True

        if self.use_tq:
            self.temporalQuery = torch.nn.Parameter(torch.zeros(self.cycle_len, self.enc_in), requires_grad=True)

        if self.channel_aggre:
            self.channelAggregator = nn.MultiheadAttention(embed_dim=self.seq_len, num_heads=4, batch_first=True, dropout=0.5)

        self.input_proj = nn.Linear(self.seq_len, self.d_model)

        self.model = nn.Sequential(
            nn.Linear(self.d_model, self.d_model),
            nn.GELU(),
            nn.Linear(self.d_model, self.d_model),
            nn.GELU(),
        )

        self.output_proj = nn.Sequential(
            nn.Dropout(self.dropout),
            nn.Linear(self.d_model, self.pred_len)
        )

        method = getattr(configs, "method", "ori")
        if method not in {"ori", "tifo"}:
            raise ValueError("TQNet supports method ori or tifo")
        self.filter = build_frequency_domain_filter(configs, global_mask) if method == "tifo" else None

    def forward(self, x, x_mark_enc, x_dec, x_mark_dec, mask=None):
        cycle_index = cycle_phase(x_mark_enc, self.cycle_len, self.freq)

        # instance norm
        if self.use_revin:
            seq_mean = torch.mean(x, dim=1, keepdim=True)
            seq_var = torch.var(x, dim=1, keepdim=True) + 1e-5
            x = (x - seq_mean) / torch.sqrt(seq_var)

        if self.filter is not None:
            x = self.filter(x)
        save = x

        # b,s,c -> b,c,s
        x_input = x.permute(0, 2, 1)

        if self.use_tq:
            gather_index = (cycle_index.view(-1, 1) + torch.arange(self.seq_len, device=cycle_index.device).view(1, -1)) % self.cycle_len
            query_input = self.temporalQuery[gather_index].permute(0, 2, 1)  # (b, c, s)
            if self.channel_aggre:
                channel_information = self.channelAggregator(query=query_input, key=x_input, value=x_input)[0]
            else:
                channel_information = query_input
        else:
            if self.channel_aggre:
                channel_information = self.channelAggregator(query=x_input, key=x_input, value=x_input)[0]
            else:
                channel_information = 0

        input = self.input_proj(x_input+channel_information)

        hidden = self.model(input)

        output = self.output_proj(hidden+input).permute(0, 2, 1)

        # instance denorm
        if self.use_revin:
            output = output * torch.sqrt(seq_var) + seq_mean

        return output[:, -self.pred_len:, :], save
