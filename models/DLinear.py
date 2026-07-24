import torch
import torch.nn as nn
import torch.nn.functional as F
from layers.Autoformer_EncDec import series_decomp
from layers.PluginNormalization import AdaptiveChannelNorm
from utils.frequency_domain_filter import build_frequency_domain_filter
from utils.wdan_adapter import build_wdan_adapter

class Model(nn.Module):
    """
    Paper link: https://arxiv.org/pdf/2205.13504.pdf
    """

    def __init__(self, configs, global_mask, individual=False):
        """
        individual: Bool, whether shared model among different variates.
        """
        super(Model, self).__init__()
        self.task_name = configs.task_name
        self.seq_len = configs.seq_len
        if self.task_name == 'classification' or self.task_name == 'anomaly_detection' or self.task_name == 'imputation':
            self.pred_len = configs.seq_len
        else:
            self.pred_len = configs.pred_len
        # Series decomposition block from Autoformer
        self.decompsition = series_decomp(configs.moving_avg)
        self.individual = individual
        self.channels = configs.enc_in

        self.global_mask = global_mask
        method = getattr(configs, 'method', 'tifo')
        self.use_tifo = method == 'tifo'
        self.use_acn = method == 'acn'
        self.use_wdan = method == 'wdan'
        if self.individual:
            self.Linear_Seasonal = nn.ModuleList()
            self.Linear_Trend = nn.ModuleList()

            for i in range(self.channels):
                self.Linear_Seasonal.append(
                    nn.Linear(self.seq_len, self.pred_len))
                self.Linear_Trend.append(
                    nn.Linear(self.seq_len, self.pred_len))

                self.Linear_Seasonal[i].weight = nn.Parameter(
                    (1 / self.seq_len) * torch.ones([self.pred_len, self.seq_len]))
                self.Linear_Trend[i].weight = nn.Parameter(
                    (1 / self.seq_len) * torch.ones([self.pred_len, self.seq_len]))
        else:
            self.Linear_Seasonal = nn.Linear(self.seq_len, self.pred_len)
            self.Linear_Trend = nn.Linear(self.seq_len, self.pred_len)

            self.Linear_Seasonal.weight = nn.Parameter(
                (1 / self.seq_len) * torch.ones([self.pred_len, self.seq_len]))
            self.Linear_Trend.weight = nn.Parameter(
                (1 / self.seq_len) * torch.ones([self.pred_len, self.seq_len]))

        if self.task_name == 'classification':
            self.projection = nn.Linear(
                configs.enc_in * configs.seq_len, configs.num_class)

        self.filter = build_frequency_domain_filter(configs, self.global_mask) if self.use_tifo else None
        self.acn_adapter = (
            AdaptiveChannelNorm(
                configs.enc_in,
                configs.seq_len,
                float(getattr(configs, 'acn_temperature', 0.1)),
            )
            if self.use_acn
            else None
        )
        self.wdan_adapter = build_wdan_adapter(configs) if self.use_wdan else None

    def encoder(self, x):
        seasonal_init, trend_init = self.decompsition(x)
        seasonal_init, trend_init = seasonal_init.permute(
            0, 2, 1), trend_init.permute(0, 2, 1)
        if self.individual:
            seasonal_output = torch.zeros([seasonal_init.size(0), seasonal_init.size(1), self.pred_len],
                                          dtype=seasonal_init.dtype).to(seasonal_init.device)
            trend_output = torch.zeros([trend_init.size(0), trend_init.size(1), self.pred_len],
                                       dtype=trend_init.dtype).to(trend_init.device)
            for i in range(self.channels):
                seasonal_output[:, i, :] = self.Linear_Seasonal[i](
                    seasonal_init[:, i, :])
                trend_output[:, i, :] = self.Linear_Trend[i](
                    trend_init[:, i, :])
        else:
            seasonal_output = self.Linear_Seasonal(seasonal_init)
            trend_output = self.Linear_Trend(trend_init)
        x = seasonal_output + trend_output
        return x.permute(0, 2, 1)

    def forecast(self, x_enc):
        # Encoder
        wdan_statistics = None
        if self.use_wdan:
            x_enc, wdan_statistics = self.wdan_adapter.normalize(x_enc)
            means = stdev = None
        else:
            # Preserve DLinear's existing reversible instance normalization.
            means = x_enc.mean(1, keepdim=True).detach()
            x_enc = x_enc - means
            stdev = torch.sqrt(torch.var(x_enc, dim=1, keepdim=True, unbiased=False) + 1e-5)
            x_enc /= stdev
            if self.use_acn:
                # ACN operates across channel tokens. DLinear has no latent
                # LayerNorm, so apply the official channel-normalization
                # operator to its normalized channel-by-time representation.
                x_enc = self.acn_adapter(x_enc.transpose(1, 2)).transpose(1, 2)

        if self.use_tifo:
            x_enc = self.filter(x_enc)
        save = x_enc

        dec_out = self.encoder(x_enc)

        if self.use_wdan:
            dec_out = self.wdan_adapter.de_normalize(dec_out, wdan_statistics)
            save = wdan_statistics
        else:
            dec_out = dec_out * (stdev[:, 0, :].unsqueeze(1).repeat(1, self.pred_len, 1))
            dec_out = dec_out + (means[:, 0, :].unsqueeze(1).repeat(1, self.pred_len, 1))
        return dec_out, save

    def wdan_statistics_loss(self, predicted_statistics, future):
        if not self.use_wdan or predicted_statistics is None:
            raise RuntimeError("WDAN statistics loss requested outside WDAN mode")
        _, low_frequency, high_frequency_scale = self.wdan_adapter.normalize(
            future, predict=False
        )
        target_statistics = torch.stack(
            (low_frequency, high_frequency_scale), dim=1
        )
        return F.mse_loss(predicted_statistics, target_statistics)

    def imputation(self, x_enc):
        # Encoder
        return self.encoder(x_enc)

    def anomaly_detection(self, x_enc):
        # Encoder
        return self.encoder(x_enc)

    def classification(self, x_enc):
        # Encoder
        enc_out = self.encoder(x_enc)
        # Output
        # (batch_size, seq_length * d_model)
        output = enc_out.reshape(enc_out.shape[0], -1)
        # (batch_size, num_classes)
        output = self.projection(output)
        return output

    def forward(self, x_enc, x_mark_enc, x_dec, x_mark_dec, mask=None):
        if self.task_name == 'long_term_forecast' or self.task_name == 'short_term_forecast':
            dec_out, save = self.forecast(x_enc)
            return dec_out[:, -self.pred_len:, :], save  # [B, L, D]
        if self.task_name == 'imputation':
            dec_out = self.imputation(x_enc)
            return dec_out  # [B, L, D]
        if self.task_name == 'anomaly_detection':
            dec_out = self.anomaly_detection(x_enc)
            return dec_out  # [B, L, D]
        if self.task_name == 'classification':
            dec_out = self.classification(x_enc)
            return dec_out  # [B, N]
        return None
