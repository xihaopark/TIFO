from data_provider.data_factory import data_provider
from exp.exp_basic import Exp_Basic
from utils.tools import EarlyStopping, adjust_learning_rate, visual
from utils.metrics import metric
import torch
import torch.nn as nn
from torch import optim
import os
import time
import warnings
import numpy as np
import random
import copy
from utils.dtw_metric import dtw,accelerated_dtw
from utils.augmentation import run_augmentation,run_augmentation_single
from utils.frequency_domain_filter import run_filter
from utils.experiment_record import write_run_manifest
warnings.filterwarnings('ignore')


def apply_controlled_spectral_shift(batch_x, batch_y, label_len, pred_len, strength):
    """Apply a deterministic high-band amplitude intervention to a full window.

    The input and its future target are transformed together so evaluation
    measures forecasting under a coherent shifted process rather than corrupting
    only the observed context. DC and the lower half of non-DC rFFT bins are
    unchanged; upper bins are multiplied by ``1 + strength``.
    """
    if strength == 0:
        return batch_x, batch_y
    future = batch_y[:, -pred_len:, :]
    full_window = torch.cat((batch_x, future), dim=1)
    mean = full_window.mean(dim=1, keepdim=True)
    spectrum = torch.fft.rfft(full_window - mean, dim=1)
    non_dc_bins = spectrum.shape[1] - 1
    high_start = 1 + non_dc_bins // 2
    gain = torch.ones(spectrum.shape[1], device=spectrum.device, dtype=spectrum.real.dtype)
    gain[high_start:] = 1.0 + strength
    shifted = torch.fft.irfft(
        spectrum * gain.view(1, -1, 1), n=full_window.shape[1], dim=1
    ) + mean
    shifted_x = shifted[:, :batch_x.shape[1], :]
    shifted_y = torch.cat(
        (shifted_x[:, -label_len:, :], shifted[:, batch_x.shape[1]:, :]), dim=1
    )
    return shifted_x, shifted_y


class Exp_Long_Term_Forecast(Exp_Basic):
    def __init__(self, args):
        super(Exp_Long_Term_Forecast, self).__init__(args)
        #self.filter, self.global_mask, self.local_mask = None, None, None

    def _compute_global_mask(self):
        python_state = random.getstate()
        numpy_state = np.random.get_state()
        torch_state = torch.get_rng_state()
        cuda_states = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
        try:
            train_data, train_loader = data_provider(
                self.args, flag='train', shuffle_override=False
            )
            self.global_mask = run_filter(self.args, train_loader, self.device)
        finally:
            random.setstate(python_state)
            np.random.set_state(numpy_state)
            torch.set_rng_state(torch_state)
            if cuda_states is not None:
                torch.cuda.set_rng_state_all(cuda_states)
        print("global mask done!!")

    def _build_model(self):
        self.global_mask = None
        if getattr(self.args, 'method', 'tifo') in {'tifo', 'wdan_tifo', 'acn_tifo'}:
            self._compute_global_mask()
        model = self.model_dict[self.args.model].Model(self.args, self.global_mask).float()

        if self.args.use_multi_gpu and self.args.use_gpu:
            model = nn.DataParallel(model, device_ids=self.args.device_ids)
        return model

    def _get_data(self, flag):
        data_set, data_loader = data_provider(self.args, flag)
        return data_set, data_loader

    def _select_optimizer(self):
        if getattr(self.args, 'method', 'ori') == 'wdan':
            # Official stats_bb_union trains the statistics module separately,
            # then jointly optimizes backbone and statistics at the backbone LR.
            return optim.Adam(self.model.parameters(), lr=self.args.learning_rate)
        if getattr(self.args, 'method', 'ori') == 'wdan_tifo':
            lr_scale = float(getattr(self.args, 'tifo_lr_scale', 1.0))
            backbone_params, filter_params = [], []
            for name, parameter in self.model.named_parameters():
                if not parameter.requires_grad:
                    continue
                (filter_params if 'filter.' in name else backbone_params).append(parameter)
            if not filter_params:
                raise RuntimeError('WDAN+TIFO mode has no TIFO filter parameters')
            return optim.Adam(
                [
                    {'params': backbone_params, 'lr': self.args.learning_rate, 'lr_scale': 1.0},
                    {
                        'params': filter_params,
                        'lr': self.args.learning_rate * lr_scale,
                        'lr_scale': lr_scale,
                    },
                ],
                lr=self.args.learning_rate,
            )
        lr_scale = float(getattr(self.args, 'tifo_lr_scale', 1.0))
        if getattr(self.args, 'method', 'ori') not in {'tifo', 'acn_tifo'} or lr_scale == 1.0:
            return optim.Adam(self.model.parameters(), lr=self.args.learning_rate)

        backbone_params = []
        filter_params = []
        for name, parameter in self.model.named_parameters():
            if not parameter.requires_grad:
                continue
            if name.startswith('filter.') or '.filter.' in name:
                filter_params.append(parameter)
            else:
                backbone_params.append(parameter)
        if not filter_params:
            raise RuntimeError('tifo_lr_scale was set but no TIFO filter parameters were found')
        return optim.Adam(
            [
                {'params': backbone_params, 'lr': self.args.learning_rate, 'lr_scale': 1.0},
                {
                    'params': filter_params,
                    'lr': self.args.learning_rate * lr_scale,
                    'lr_scale': lr_scale,
                },
            ],
            lr=self.args.learning_rate,
        )

    def _select_criterion(self):
        mse = nn.MSELoss()
        mae_weight = float(getattr(self.args, 'mae_loss_weight', 0.0))
        if mae_weight < 0:
            raise ValueError('mae_loss_weight must be non-negative')
        if mae_weight == 0:
            return mse
        mae = nn.L1Loss()

        def weighted_loss(prediction, target):
            return mse(prediction, target) + mae_weight * mae(prediction, target)

        return weighted_loss

    def _pretrain_wdan_adapter(self, train_loader, vali_loader):
        """Match WDAN's official five-epoch statistics pretraining stage."""
        if getattr(self.args, 'method', 'ori') not in {'wdan', 'wdan_tifo'}:
            return
        model = self.model.module if isinstance(self.model, nn.DataParallel) else self.model
        epochs = int(getattr(self.args, 'wdan_stats_epochs', 5))
        stats_lr = self.args.learning_rate * float(
            getattr(self.args, 'wdan_lr_scale', 1.0)
        )
        optimizer = optim.Adam(model.wdan_adapter.parameters(), lr=stats_lr)
        best_loss = float('inf')
        best_state = None
        for epoch in range(epochs):
            model.wdan_adapter.train()
            train_losses = []
            for batch_x, batch_y, _, _ in train_loader:
                batch_x = batch_x.float().to(self.device)
                future = batch_y[:, -self.args.pred_len:, :].float().to(self.device)
                optimizer.zero_grad()
                _, statistics = model.wdan_adapter.normalize(batch_x)
                loss = model.wdan_statistics_loss(statistics, future)
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())

            model.wdan_adapter.eval()
            validation_losses = []
            with torch.no_grad():
                for batch_x, batch_y, _, _ in vali_loader:
                    batch_x = batch_x.float().to(self.device)
                    future = batch_y[:, -self.args.pred_len:, :].float().to(self.device)
                    _, statistics = model.wdan_adapter.normalize(batch_x)
                    validation_losses.append(
                        model.wdan_statistics_loss(statistics, future).item()
                    )
            validation_loss = float(np.average(validation_losses))
            print(
                'WDAN stats epoch: {0} | Train Loss: {1:.7f} Vali Loss: {2:.7f}'.format(
                    epoch + 1, float(np.average(train_losses)), validation_loss
                )
            )
            if validation_loss < best_loss:
                best_loss = validation_loss
                best_state = copy.deepcopy(model.wdan_adapter.state_dict())
        if best_state is None:
            raise RuntimeError('WDAN statistics pretraining produced no checkpoint')
        model.wdan_adapter.load_state_dict(best_state)


    def vali(self, vali_data, vali_loader, criterion):
        total_loss = []
        self.model.eval()
        with torch.no_grad():
            for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(vali_loader):
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.float()

                batch_x_mark = batch_x_mark.float().to(self.device)
                batch_y_mark = batch_y_mark.float().to(self.device)

                # decoder input
                dec_inp = torch.zeros_like(batch_y[:, -self.args.pred_len:, :]).float()
                dec_inp = torch.cat([batch_y[:, :self.args.label_len, :], dec_inp], dim=1).float().to(self.device)

                # encoder - decoder
                if self.args.use_amp:
                    with torch.cuda.amp.autocast():
                        if self.args.output_attention:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                        else:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)
                else:
                    if self.args.output_attention:
                        outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                    else:
                        outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)
                f_dim = -1 if self.args.features == 'MS' else 0
                outputs = outputs[:, -self.args.pred_len:, f_dim:]
                batch_y = batch_y[:, -self.args.pred_len:, f_dim:].to(self.device)

                pred = outputs.detach().cpu()
                true = batch_y.detach().cpu()

                loss = criterion(pred, true)

                total_loss.append(loss)
        total_loss = np.average(total_loss)
        self.model.train()
        return total_loss

    def validation_metrics(self):
        """Report sample-weighted validation MSE and MAE for a frozen checkpoint."""
        _, validation_loader = self._get_data(flag='val')
        squared_error = 0.0
        absolute_error = 0.0
        element_count = 0
        self.model.eval()
        with torch.no_grad():
            for batch_x, batch_y, batch_x_mark, batch_y_mark in validation_loader:
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.float().to(self.device)
                batch_x_mark = batch_x_mark.float().to(self.device)
                batch_y_mark = batch_y_mark.float().to(self.device)
                dec_inp = torch.cat(
                    [
                        batch_y[:, :self.args.label_len, :],
                        torch.zeros_like(batch_y[:, -self.args.pred_len:, :]),
                    ],
                    dim=1,
                )
                outputs, _ = self.model(
                    batch_x, batch_x_mark, dec_inp, batch_y_mark
                )
                feature_start = -1 if self.args.features == 'MS' else 0
                outputs = outputs[:, -self.args.pred_len:, feature_start:]
                targets = batch_y[:, -self.args.pred_len:, feature_start:]
                error = outputs - targets
                squared_error += error.square().sum().item()
                absolute_error += error.abs().sum().item()
                element_count += error.numel()
        if element_count == 0:
            raise RuntimeError('validation loader produced no elements')
        mse = squared_error / element_count
        mae = absolute_error / element_count
        print(f'VALIDATION_METRICS mse={mse:.10f} mae={mae:.10f} n={element_count}')
        self.model.train()
        return mse, mae

    def train(self, setting):
        train_data, train_loader = self._get_data(flag='train')
        vali_data, vali_loader = self._get_data(flag='val')

        path = os.path.join(self.args.checkpoints, setting)
        if not os.path.exists(path):
            os.makedirs(path)

        time_now = time.time()

        train_steps = len(train_loader)
        early_stopping = EarlyStopping(patience=self.args.patience, verbose=True)

        self._pretrain_wdan_adapter(train_loader, vali_loader)
        model_optim = self._select_optimizer()
        criterion = self._select_criterion()

        if self.args.use_amp:
            scaler = torch.cuda.amp.GradScaler()

        for epoch in range(self.args.train_epochs):
            iter_count = 0
            train_loss = []

            self.model.train()
            epoch_time = time.time()
            for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(train_loader):
                iter_count += 1
                model_optim.zero_grad()
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.float().to(self.device)
                batch_x_mark = batch_x_mark.float().to(self.device)
                batch_y_mark = batch_y_mark.float().to(self.device)

                # decoder input
                dec_inp = torch.zeros_like(batch_y[:, -self.args.pred_len:, :]).float()
                dec_inp = torch.cat([batch_y[:, :self.args.label_len, :], dec_inp], dim=1).float().to(self.device)

                # encoder - decoder
                if self.args.use_amp:
                    with torch.cuda.amp.autocast():
                        if self.args.output_attention:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                        else:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)

                        f_dim = -1 if self.args.features == 'MS' else 0
                        outputs = outputs[:, -self.args.pred_len:, f_dim:]
                        batch_y = batch_y[:, -self.args.pred_len:, f_dim:].to(self.device)
                        loss = criterion(outputs, batch_y)
                        train_loss.append(loss.item())
                else:
                    if self.args.output_attention:
                        outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                    else:
                        outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)

                    f_dim = -1 if self.args.features == 'MS' else 0
                    outputs = outputs[:, -self.args.pred_len:, f_dim:]
                    batch_y = batch_y[:, -self.args.pred_len:, f_dim:].to(self.device)
                    loss = criterion(outputs, batch_y)
                    train_loss.append(loss.item())

                if (i + 1) % 100 == 0:
                    print("\titers: {0}, epoch: {1} | loss: {2:.7f}".format(i + 1, epoch + 1, loss.item()))
                    speed = (time.time() - time_now) / iter_count
                    left_time = speed * ((self.args.train_epochs - epoch) * train_steps - i)
                    print('\tspeed: {:.4f}s/iter; left time: {:.4f}s'.format(speed, left_time))
                    iter_count = 0
                    time_now = time.time()

                if self.args.use_amp:
                    scaler.scale(loss).backward()
                    scaler.step(model_optim)
                    scaler.update()
                else:
                    loss.backward()
                    model_optim.step()

            print("Epoch: {} cost time: {}".format(epoch + 1, time.time() - epoch_time))
            train_loss = np.average(train_loss)
            vali_loss = self.vali(vali_data, vali_loader, criterion)

            print("Epoch: {0}, Steps: {1} | Train Loss: {2:.7f} Vali Loss: {3:.7f}".format(
                epoch + 1, train_steps, train_loss, vali_loss))
            early_stopping(vali_loss, self.model, path)
            if early_stopping.early_stop:
                print("Early stopping")
                break

            adjust_learning_rate(model_optim, epoch + 1, self.args)

        best_model_path = path + '/' + 'checkpoint.pth'
        self.model.load_state_dict(torch.load(best_model_path))

        return self.model

    def test(self, setting, test=0):
        test_data, test_loader = self._get_data(flag='test')
        if test:
            print('loading model')
            self.model.load_state_dict(torch.load(os.path.join('./checkpoints/' + setting, 'checkpoint.pth')))

        evaluation_tag = getattr(self.args, 'evaluation_tag', '')
        evaluation_setting = setting if not evaluation_tag else f'{setting}__{evaluation_tag}'
        preds = []
        trues = []
        folder_path = './test_results/' + evaluation_setting + '/'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.model.eval()
        with torch.no_grad():
            for i, (batch_x, batch_y, batch_x_mark, batch_y_mark) in enumerate(test_loader):
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.float().to(self.device)

                batch_x, batch_y = apply_controlled_spectral_shift(
                    batch_x,
                    batch_y,
                    self.args.label_len,
                    self.args.pred_len,
                    float(getattr(self.args, 'spectral_shift_strength', 0.0)),
                )

                batch_x_mark = batch_x_mark.float().to(self.device)
                batch_y_mark = batch_y_mark.float().to(self.device)

                # decoder input
                dec_inp = torch.zeros_like(batch_y[:, -self.args.pred_len:, :]).float()
                dec_inp = torch.cat([batch_y[:, :self.args.label_len, :], dec_inp], dim=1).float().to(self.device)

                if self.args.use_amp:
                    with torch.cuda.amp.autocast():
                        if self.args.output_attention:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                        else:
                            outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)
                else:
                    if self.args.output_attention:
                        outputs, save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]

                    else:
                        outputs,save = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)

                f_dim = -1 if self.args.features == 'MS' else 0
                outputs = outputs[:, -self.args.pred_len:, :]
                batch_y = batch_y[:, -self.args.pred_len:, :].to(self.device)

                outputs = outputs.detach().cpu().numpy()
                batch_y = batch_y.detach().cpu().numpy()

                if test_data.scale and self.args.inverse:
                    shape = outputs.shape
                    outputs = test_data.inverse_transform(outputs.reshape(shape[0] * shape[1], -1)).reshape(shape)
                    batch_y = test_data.inverse_transform(batch_y.reshape(shape[0] * shape[1], -1)).reshape(shape)

                outputs = outputs[:, :, f_dim:]
                batch_y = batch_y[:, :, f_dim:]

                pred = outputs
                true = batch_y

                preds.append(pred)
                trues.append(true)
                # if i % 20 == 0:
                #     input = batch_x.detach().cpu().numpy()
                #     if test_data.scale and self.args.inverse:
                #         shape = input.shape
                #         input = test_data.inverse_transform(input.reshape(shape[0] * shape[1], -1)).reshape(shape)
                #     gt = np.concatenate((input[0, :, -1], true[0, :, -1]), axis=0)
                #     pd = np.concatenate((input[0, :, -1], pred[0, :, -1]), axis=0)
                #     visual(gt, pd, os.path.join(folder_path, str(i) + '.pdf'))

        preds = np.concatenate(preds, axis=0)
        trues = np.concatenate(trues, axis=0)
        print('test shape:', preds.shape, trues.shape)
        preds = preds.reshape(-1, preds.shape[-2], preds.shape[-1])
        trues = trues.reshape(-1, trues.shape[-2], trues.shape[-1])
        print('test shape:', preds.shape, trues.shape)

        # result save
        folder_path = './results/' + evaluation_setting + '/'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # dtw calculation
        # if self.args.use_dtw:
        #     dtw_list = []
        #     manhattan_distance = lambda x, y: np.abs(x - y)
        #     for i in range(preds.shape[0]):
        #         x = preds[i].reshape(-1,1)
        #         y = trues[i].reshape(-1,1)
        #         if i % 100 == 0:
        #             print("calculating dtw iter:", i)
        #         d, _, _, _ = accelerated_dtw(x, y, dist=manhattan_distance)
        #         dtw_list.append(d)
        #     dtw = np.array(dtw_list).mean()
        # else:
        #     dtw = -999


        mae, mse, rmse, mape, mspe = metric(preds, trues)
        dtw_value = -999
        print('mse:{}, mae:{}, dtw:{}'.format(mse, mae, dtw_value))
        f = open("result_long_term_forecast.txt", 'a')
        f.write(evaluation_setting + "  \n")
        f.write('mse:{}, mae:{}, dtw:{}'.format(mse, mae, dtw_value))
        f.write('\n')
        f.write('\n')
        f.close()

        np.save(folder_path + 'metrics.npy', np.array([mae, mse, rmse, mape, mspe]))
        if self.args.save_arrays:
            np.save(folder_path + 'pred.npy', preds)
            np.save(folder_path + 'true.npy', trues)

        write_run_manifest(
            self.args,
            evaluation_setting,
            folder_path,
            metrics={
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(rmse),
                'mape': float(mape),
                'mspe': float(mspe),
            },
        )

        return
