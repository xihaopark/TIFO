"""FilterNet backbones (PaiFilter / TexFilter) with an optional TIFO input adapter.

Model bodies and RevIN are copied from the official implementation
https://github.com/aikunyi/FilterNet (Apache-2.0), commit cdb321c
(``models/PaiFilter.py``, ``models/TexFilter.py``, ``layers/RevIN.py``).
TIFO, when enabled, is applied to the RevIN-normalized input, matching how it
is applied inside the DLinear/iTransformer backbones of this repository.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from utils.frequency_domain_filter import build_frequency_domain_filter


class RevIN(nn.Module):
    def __init__(self, num_features: int, eps=1e-5, affine=True, subtract_last=False):
        """
        :param num_features: the number of features or channels
        :param eps: a value added for numerical stability
        :param affine: if True, RevIN has learnable affine parameters
        """
        super(RevIN, self).__init__()
        self.num_features = num_features
        self.eps = eps
        self.affine = affine
        self.subtract_last = subtract_last
        if self.affine:
            self._init_params()

    def forward(self, x, mode:str):
        if mode == 'norm':
            self._get_statistics(x)
            x = self._normalize(x)
        elif mode == 'denorm':
            x = self._denormalize(x)
        else: raise NotImplementedError
        return x

    def _init_params(self):
        # initialize RevIN params: (C,)
        self.affine_weight = nn.Parameter(torch.ones(self.num_features))
        self.affine_bias = nn.Parameter(torch.zeros(self.num_features))

    def _get_statistics(self, x):
        dim2reduce = tuple(range(1, x.ndim-1))
        if self.subtract_last:
            self.last = x[:,-1,:].unsqueeze(1)
        else:
            self.mean = torch.mean(x, dim=dim2reduce, keepdim=True).detach()
        self.stdev = torch.sqrt(torch.var(x, dim=dim2reduce, keepdim=True, unbiased=False) + self.eps).detach()

    def _normalize(self, x):
        if self.subtract_last:
            x = x - self.last
        else:
            x = x - self.mean
        x = x / self.stdev
        if self.affine:
            x = x * self.affine_weight
            x = x + self.affine_bias
        return x

    def _denormalize(self, x):
        if self.affine:
            x = x - self.affine_bias
            x = x / (self.affine_weight + self.eps*self.eps)
        x = x * self.stdev
        if self.subtract_last:
            x = x + self.last
        else:
            x = x + self.mean
        return x

class PaiFilter(nn.Module):

    def __init__(self, configs):
        super(PaiFilter, self).__init__()
        self.seq_len = configs.seq_len
        self.pred_len = configs.pred_len
        self.scale = 0.02
        self.revin_layer = RevIN(configs.enc_in, affine=True, subtract_last=False)

        self.embed_size = self.seq_len
        self.hidden_size = configs.hidden_size
        
        self.w = nn.Parameter(self.scale * torch.randn(1, self.embed_size))

        self.fc = nn.Sequential(
            nn.Linear(self.embed_size, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, self.pred_len)
        )


    def circular_convolution(self, x, w):
        x = torch.fft.rfft(x, dim=2, norm='ortho')
        w = torch.fft.rfft(w, dim=1, norm='ortho')
        y = x * w
        out = torch.fft.irfft(y, n=self.embed_size, dim=2, norm="ortho")
        return out

    def body(self, x):
        x = x.permute(0, 2, 1)
        x = self.circular_convolution(x, self.w.to(x.device))  # B, N, D
        x = self.fc(x)
        return x.permute(0, 2, 1)


class TexFilter(nn.Module):

    def __init__(self, configs):
        super(TexFilter, self).__init__()
        self.seq_len = configs.seq_len
        self.pred_len = configs.pred_len
        self.embed_size = configs.embed_size
        self.hidden_size = configs.hidden_size
        self.dropout = configs.dropout
        self.band_width = 96
        self.scale = 0.02
        self.sparsity_threshold = 0.01

        self.revin_layer = RevIN(configs.enc_in, affine=True, subtract_last=False)
        self.embedding = nn.Linear(self.seq_len, self.embed_size)
        self.token = nn.Conv1d(in_channels=self.seq_len, out_channels=self.embed_size, kernel_size=(1,))

        self.w = nn.Parameter(self.scale * torch.randn(2, self.embed_size))
        self.w1 = nn.Parameter(self.scale * torch.randn(2, self.embed_size))

        self.rb1 = nn.Parameter(self.scale * torch.randn(self.embed_size))
        self.ib1 = nn.Parameter(self.scale * torch.randn(self.embed_size))

        self.rb2 = nn.Parameter(self.scale * torch.randn(self.embed_size))
        self.ib2 = nn.Parameter(self.scale * torch.randn(self.embed_size))

        self.fc = nn.Sequential(
            nn.Linear(self.embed_size, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, self.embed_size)
        )

        self.output = nn.Linear(self.embed_size, self.pred_len)
        self.layernorm = nn.LayerNorm(self.embed_size)
        self.layernorm1 = nn.LayerNorm(self.embed_size)
        self.dropout = nn.Dropout(self.dropout)

    def tokenEmbed(self, x):
        x = self.token(x)
        return x

    def texfilter(self, x):
        B, N, _ = x.shape
        o1_real = torch.zeros([B, N // 2 + 1, self.embed_size],
                              device=x.device)
        o1_imag = torch.zeros([B, N // 2 + 1, self.embed_size],
                              device=x.device)

        o2_real = torch.zeros([B, N // 2 + 1, self.embed_size],
                              device=x.device)
        o2_imag = torch.zeros([B, N // 2 + 1, self.embed_size],
                              device=x.device)

        o1_real = F.relu(
            torch.einsum('bid,d->bid', x.real, self.w[0]) - \
            torch.einsum('bid,d->bid', x.imag, self.w[1]) + \
            self.rb1
        )

        o1_imag = F.relu(
            torch.einsum('bid,d->bid', x.imag, self.w[0]) + \
            torch.einsum('bid,d->bid', x.real, self.w[1]) + \
            self.ib1
        )

        o2_real = (
                torch.einsum('bid,d->bid', o1_real, self.w1[0]) - \
                torch.einsum('bid,d->bid', o1_imag, self.w1[1]) + \
                self.rb2
        )

        o2_imag = (
                torch.einsum('bid,d->bid', o1_imag, self.w1[0]) + \
                torch.einsum('bid,d->bid', o1_real, self.w1[1]) + \
                self.ib2
        )

        y = torch.stack([o2_real, o2_imag], dim=-1)
        y = F.softshrink(y, lambd=self.sparsity_threshold)
        y = torch.view_as_complex(y)
        return y

    def body(self, x):
        B, L, N = x.shape
        x = x.permute(0, 2, 1)
        x = self.embedding(x)  # B, N, D
        x = self.layernorm(x)
        x = torch.fft.rfft(x, dim=1, norm='ortho')
        weight = self.texfilter(x)
        x = x * weight
        x = torch.fft.irfft(x, n=N, dim=1, norm="ortho")
        x = self.layernorm1(x)
        x = self.dropout(x)
        x = self.fc(x)
        x = self.output(x)
        return x.permute(0, 2, 1)


class Model(nn.Module):
    """RevIN -> [TIFO] -> PaiFilter/TexFilter body -> RevIN^-1 (official order)."""

    def __init__(self, configs, global_mask=None):
        super().__init__()
        variant = getattr(configs, "filternet_variant", "pai")
        self.net = PaiFilter(configs) if variant == "pai" else TexFilter(configs)
        self.pred_len = configs.pred_len
        method = getattr(configs, "method", "ori")
        if method not in {"ori", "tifo"}:
            raise ValueError("FilterNet supports method ori or tifo")
        self.filter = build_frequency_domain_filter(configs, global_mask) if method == "tifo" else None

    def forward(self, x_enc, x_mark_enc, x_dec, x_mark_dec, mask=None):
        x = self.net.revin_layer(x_enc, 'norm')
        if self.filter is not None:
            x = self.filter(x)
        save = x
        x = self.net.body(x)
        x = self.net.revin_layer(x, 'denorm')
        return x[:, -self.pred_len:, :], save
