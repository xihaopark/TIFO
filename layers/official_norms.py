"""Official RevIN / SAN / FAN normalizers and reversible plug-in wrappers.

The three classes below are copied verbatim (apart from removing a debug
print) from https://github.com/icannotnamemyself/FAN (Apache-2.0), commit
838e1b0, ``torch_timeseries/normalizations/{RevIN,SAN,FAN}.py``. The wrappers
reproduce that framework's training objective: SAN adds MSE losses on the
predicted slice mean/std, FAN adds its main-frequency/residual loss, RevIN has
no auxiliary loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- official RevIN.py -------------------------------------------------------
class RevIN(nn.Module):
    def __init__(self, n_series, affine):
        super().__init__()
        self.affine = affine
        if affine: # affine: use affine layers or not
            self.gamma = nn.Parameter(torch.ones(n_series)) # n_series: number of series
            self.beta = nn.Parameter(torch.zeros(n_series))
        else:
            self.gamma, self.beta = 1, 0
    
    def normalize(self, batch_x, dec_inp=None):
        # batch_x: B*L*D || dec_inp: B*?*D (for xxformers)
        self.preget(batch_x)
        batch_x = self.forward_process(batch_x)
        dec_inp = None if dec_inp is None else self.forward_process(dec_inp)
        return batch_x, dec_inp
    
    def loss(self, true):
        return 0

    def denormalize(self, batch_x):
        # batch_x: B*H*D (forecasts)
        batch_y = self.inverse_process(batch_x)
        return batch_y


    def preget(self, batch_x):
        # (B, T, N)
        self.avg = torch.mean(batch_x, axis=1, keepdim=True).detach() # b*1*d
        self.var = torch.var(batch_x, axis=1, keepdim=True).detach()  # b*1*d

    def forward_process(self, batch_input):
        temp = (batch_input - self.avg)/torch.sqrt(self.var + 1e-8)
        if self.affine:
            return temp.mul(self.gamma) + self.beta
        else: 
            return temp

    def inverse_process(self, batch_input):
        return ((batch_input - self.beta) / self.gamma) * torch.sqrt(self.var + 1e-8) + self.avg
    
    def forward(self, batch_x, mode='n', dec=None):
        if mode == 'n':
            return self.normalize(batch_x, dec)
        elif mode =='d':
            return self.denormalize(batch_x)
            



# ---- official SAN.py ---------------------------------------------------------
class SAN(nn.Module):
    def __init__(self, seq_len, pred_len, period_len, enc_in,station_type='adaptive'):
        super().__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.period_len = period_len
        self.channels = enc_in 
        self.enc_in = enc_in 
        # configs.enc_in if configs.features == 'M' else 1
        self.station_type = station_type

        self.seq_len_new = int(self.seq_len / self.period_len)
        self.pred_len_new = int(self.pred_len / self.period_len)
        self.epsilon = 1e-5
        self._build_model()
        self.weight = nn.Parameter(torch.ones(2, self.channels))

    def _build_model(self):
        seq_len = self.seq_len // self.period_len
        enc_in = self.enc_in
        pred_len = self.pred_len_new
        self.model = SANMLP(seq_len, pred_len, enc_in, self.period_len, mode='mean').float()
        self.model_std = SANMLP( seq_len, pred_len, enc_in, self.period_len, mode='std').float()

    def normalize(self, input):
        # (B, T, N)
        if self.station_type == 'adaptive':
            bs, len, dim = input.shape
            input = input.reshape(bs, -1, self.period_len, dim)
            mean = torch.mean(input, dim=-2, keepdim=True)
            std = torch.std(input, dim=-2, keepdim=True)
            norm_input = (input - mean) / (std + self.epsilon)
            input = input.reshape(bs, len, dim)
            mean_all = torch.mean(input, dim=1, keepdim=True)
            outputs_mean = self.model(mean.squeeze(2) - mean_all, input - mean_all) * self.weight[0] + mean_all * \
                           self.weight[1]
            outputs_std = self.model_std(std.squeeze(2), input)

            outputs = torch.cat([outputs_mean, outputs_std], dim=-1)

            return norm_input.reshape(bs, len, dim), outputs[:, -self.pred_len_new:, :]

        else:
            return input, None

    def denormalize(self, input, station_pred):
        # input:  (B, O, N)
        # station_pred: outputs of normalize 
        if self.station_type == 'adaptive':
            bs, len, dim = input.shape
            input = input.reshape(bs, -1, self.period_len, dim)
            # mean = station_pred[:, :, :self.channels].unsqueeze(2)
            # std = station_pred[:, :, self.channels:].unsqueeze(2)
            mean = station_pred[:, :, :self.channels].unsqueeze(2)
            std = station_pred[:, :, self.channels:].unsqueeze(2)
            output = input * (std + self.epsilon) + mean
            return output.reshape(bs, len, dim)
        else:
            return input
    def forward(self, batch_x, mode='n', station_pred=None):
        if mode == 'n':
            return self.normalize(batch_x)
        elif mode =='d':
            return self.denormalize(batch_x, station_pred)


class SANMLP(nn.Module):
    def __init__(self, seq_len, pred_len, enc_in, period_len, mode):
        super(SANMLP, self).__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.channels = enc_in
        self.period_len = period_len
        self.mode = mode
        if mode == 'std':
            self.final_activation = nn.ReLU()
        else:
            self.final_activation = nn.Identity()
        self.input = nn.Linear(self.seq_len, 512)
        self.input_raw = nn.Linear(self.seq_len * self.period_len, 512)
        self.activation = nn.ReLU() if mode == 'std' else nn.Tanh()
        self.output = nn.Linear(1024, self.pred_len)

    def forward(self, x, x_raw):
        x, x_raw = x.permute(0, 2, 1), x_raw.permute(0, 2, 1)
        x = self.input(x)
        x_raw = self.input_raw(x_raw)
        x = torch.cat([x, x_raw], dim=-1)
        x = self.output(self.activation(x))
        x = self.final_activation(x)
        return x.permute(0, 2, 1)
# ---- official FAN.py ---------------------------------------------------------
def main_freq_part(x, k, rfft=True):
    # freq normalization
    # start = time.time()
    if rfft:
        xf = torch.fft.rfft(x, dim=1)
    else:
        xf = torch.fft.fft(x, dim=1)
        
    k_values = torch.topk(xf.abs(), k, dim = 1)  
    indices = k_values.indices

    mask = torch.zeros_like(xf)
    mask.scatter_(1, indices, 1)
    xf_filtered = xf * mask

    if rfft:
        x_filtered = torch.fft.irfft(xf_filtered, dim=1).real.float()
    else:
        x_filtered = torch.fft.ifft(xf_filtered, dim=1).real.float()

    
    norm_input = x - x_filtered
    # print(f"decompose take:{ time.time() - start} s")
    return norm_input, x_filtered



class FAN(nn.Module):
    """FAN first substract bottom k frequecy component from the original series
      

    Args:
        nn (_type_): _description_
    """
    def __init__(self,  seq_len, pred_len, enc_in, freq_topk = 20, rfft=True, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.enc_in = enc_in 
        self.epsilon = 1e-8
        self.freq_topk = freq_topk
        self.rfft = rfft
        
        self._build_model()
        self.weight = nn.Parameter(torch.ones(2, self.enc_in))
        
    def _build_model(self):
        self.model_freq = MLPfreq(seq_len=self.seq_len, pred_len=self.pred_len, enc_in=self.enc_in)
        
    def loss(self, true):
        # freq normalization
        B , O, N= true.shape
        residual, pred_main  = main_freq_part(true, self.freq_topk, self.rfft)
        

        lf = nn.functional.mse_loss
        return  lf(self.pred_main_freq_signal, pred_main) + lf(residual, self.pred_residual) 
        
        
    def normalize(self, input):
        # (B, T, N)
        bs, len, dim = input.shape
        norm_input, x_filtered = main_freq_part(input, self.freq_topk, self.rfft)
        self.pred_main_freq_signal = self.model_freq(x_filtered.transpose(1,2), input.transpose(1,2)).transpose(1,2)
        
        return norm_input.reshape(bs, len, dim)


    def denormalize(self, input_norm):
        # input:  (B, O, N)
        # station_pred: outputs of normalize
        bs, len, dim = input_norm.shape
        # freq denormalize
        self.pred_residual = input_norm
        output = self.pred_residual + self.pred_main_freq_signal
        
        return output.reshape(bs, len, dim)
    
    def forward(self, batch_x, mode='n'):
        if mode == 'n':
            return self.normalize(batch_x)
        elif mode =='d':
            return self.denormalize(batch_x)


class MLPfreq(nn.Module):
    def __init__(self, seq_len, pred_len, enc_in):
        super(MLPfreq, self).__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.channels = enc_in
        
        self.model_freq = nn.Sequential(
            nn.Linear(self.seq_len, 64),
            nn.ReLU(),
        )
        
        self.model_all = nn.Sequential(
            nn.Linear(64 + seq_len, 128),
            nn.ReLU(),
            nn.Linear(128, pred_len)
        )


    def forward(self, main_freq, x):
        inp = torch.concat([self.model_freq(main_freq), x], dim=-1)
        return self.model_all(inp)
        
        
        


# ---- reversible plug-in wrappers (FredNormer) --------------------------------
class ReversibleNormPlugin(nn.Module):
    """normalize(x) -> x_norm; denormalize(y_norm) -> y; auxiliary_loss(y)."""

    def __init__(self, kind: str, configs):
        super().__init__()
        self.kind = kind
        if kind == "revin":
            self.norm = RevIN(configs.enc_in, True)
        elif kind == "san":
            period = int(getattr(configs, "san_period_len", 12))
            if configs.seq_len % period or configs.pred_len % period:
                raise ValueError("SAN requires seq_len and pred_len divisible by san_period_len")
            self.period = period
            self.norm = SAN(configs.seq_len, configs.pred_len, period, configs.enc_in)
        elif kind == "fan":
            self.norm = FAN(configs.seq_len, configs.pred_len, configs.enc_in,
                            freq_topk=int(getattr(configs, "fan_topk", 20)))
        else:
            raise ValueError(f"unknown normalization plug-in {kind!r}")
        self._station = None

    def normalize(self, x):
        if self.kind == "revin":
            return self.norm.normalize(x)[0]
        if self.kind == "san":
            x_norm, self._station = self.norm.normalize(x)
            return x_norm
        return self.norm.normalize(x)

    def denormalize(self, y):
        if self.kind == "san":
            return self.norm.denormalize(y, self._station)
        return self.norm.denormalize(y)

    def auxiliary_loss(self, true):
        if self.kind == "san":
            channels = true.size(-1)
            mean = self._station[:, :, :channels]
            std = self._station[:, :, channels:]
            sliced = true.reshape(true.size(0), -1, self.period, channels)
            return F.mse_loss(mean, sliced.mean(2)) + F.mse_loss(std, sliced.std(2))
        if self.kind == "fan":
            return self.norm.loss(true)
        return true.new_zeros(())
