# -*- coding: utf-8 -*-
import torch, math
import torch.nn as nn
import torch.nn.functional as F


# ===============================================================
# 1. GLOBAL MASK (含 z‑score)
# ===============================================================
class GlobalMaskCalculator:
    def __init__(self, args, device):
        self.args, self.device = args, device

    def compute_global_statistics(self, loader):
        C, L0 = self.args.enc_in, self.args.seq_len
        amp_sum  = torch.zeros(L0, C, device=self.device)
        amp2_sum = torch.zeros_like(amp_sum)
        n = 0
        with torch.no_grad():
            for data in loader:
                x = data[0].float().to(self.device)              # [B,L0,C]
                x = (x - x.mean(1, keepdim=True)) / (
                      torch.sqrt(x.var(1, keepdim=True, unbiased=False) + 1e-5))
                amp = torch.abs(torch.fft.fft(x, dim=1))         # [B,L0,C]
                amp_sum  += amp.sum(0)
                amp2_sum += (amp ** 2).sum(0)
                n += x.size(0)
        μ = amp_sum / n
        sigma = torch.sqrt(amp2_sum / n - μ ** 2 + 1e-5)
        return μ / (sigma + 1e-5)                                    # [L0,C]


def run_filter(args, loader):
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return GlobalMaskCalculator(args, dev).compute_global_statistics(loader)


# ===============================================================
# 2. FREQUENCY‑DOMAIN FILTER
# ===============================================================
class FrequencyDomainFilter(nn.Module):
    """
    forward()  : 生成稳定表征 (长度 = L0)
    inverse()  : 将任意长度 L1 的预测从稳定域映回原域
                 inv_mode = 'interp' | 'conv'
    """
    def __init__(self, args, global_mask_amp,
                 lam=1e-3, skip=True, inv_mode='interp'):
        super().__init__()
        self.args, self.mask = args, global_mask_amp          # [L0,C]
        self.lam, self.skip, self.inv_mode = lam, skip, inv_mode
        L0, C = global_mask_amp.size()

        # 生成 log|H|, φ
        def mlp():
            return nn.Sequential(nn.Linear(L0, 64), nn.RReLU(), nn.Dropout(0.1),
                                 nn.Linear(64, L0))
        self.linear_logmag, self.linear_phase = mlp(), mlp()

    # ---------- 复数掩码 (长度 = L0) ----------
    def _mask_L0(self):
        logmag = self.linear_logmag(self.mask.T).T
        phase  = self.linear_phase (self.mask.T).T
        mag = torch.exp(logmag)
        return torch.complex(mag * torch.cos(phase),
                             mag * torch.sin(phase))          # [L0,C]

    # ---------- 正向 ----------
    def forward(self, x):                                     # x:[B,L0,C]
        X = torch.fft.fft(x, dim=1)
        Y = torch.fft.ifft(X * self._mask_L0(), dim=1).real
        return x + Y if self.skip else Y                      # [B,L0,C]

    # ---------- 逆向 (支持任意 L1) ----------
    def inverse_filter(self, y_hat):                          # y_hat:[B,L1,C]
        """
        Args
        ----
        y_hat : 预测值 (稳定域)  [B,L1,C]
        Return
        ------
        x_hat : 反映射到原域    [B,L1,C]
        """
        if self.inv_mode == 'interp':
            return self._inverse_interp(y_hat)
        elif self.inv_mode == 'conv':
            return self._inverse_conv(y_hat)
        else:
            raise ValueError("inv_mode must be 'interp' or 'conv'.")

    # ------ 方案 A : 频域插值 ------
    def _inverse_interp(self, y_hat):
        B, L1, C = y_hat.shape
        Y = torch.fft.fft(y_hat, dim=1)                       # [B,L1,C]

        H_L0 = self._mask_L0().permute(1, 0)                 # [C,L0]
        # 线性插值到 L1
        H_L1_r = F.interpolate(H_L0.real.unsqueeze(1), size=L1,
                               mode='linear', align_corners=False).squeeze(1)
        H_L1_i = F.interpolate(H_L0.imag.unsqueeze(1), size=L1,
                               mode='linear', align_corners=False).squeeze(1)
        H_L1 = torch.complex(H_L1_r, H_L1_i).permute(1, 0)    # [L1,C]

        H2 = (H_L1.real**2 + H_L1.imag**2).clamp_min(1e-8)
        H_inv = torch.conj(H_L1) / (H2 + self.lam)            # [L1,C]

        X = Y * H_inv                                        # 广播 B
        x_hat = torch.fft.ifft(X, dim=1).real
        return x_hat

    # ------ 方案 B : 时域卷积 ------
    def _inverse_conv(self, y_hat):
        """
        1. 根据 L0 频谱求 h† (time‑domain impulse)
        2. 对任意 L1 用 conv1d SAME 实现
        """
        L0, C = self.mask.size()
        H_inv = self._pseudo_inverse_mask()                   # [L0,C]
        h_inv = torch.fft.ifft(H_inv, dim=0).real             # [L0,C]

        # 组织成 conv1d kernel :  [C,1,L0]
        kernel = h_inv.permute(1, 0).unsqueeze(1)             # [C,1,L0]
        pad = (L0 - 1) // 2                                   # SAME padding
        y_hat_ch = y_hat.permute(0, 2, 1)                     # [B,C,L1]
        x_hat = F.conv1d(y_hat_ch, kernel, padding=pad, groups=C)
        return x_hat.permute(0, 2, 1)[:, :y_hat.size(1), :]   # 裁到 L1

    # ----- 生成 H† 与方案 B 复用 -----
    def _pseudo_inverse_mask(self):
        H = self._mask_L0()
        H2 = (H.real**2 + H.imag**2).clamp_min(1e-8)
        return torch.conj(H) / (H2 + self.lam)                # [L0,C]
