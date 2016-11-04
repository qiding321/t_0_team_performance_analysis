# -*- coding: utf-8 -*-
"""
Created on 2016/11/3 16:25

@author: qiding
"""

import WaveWrapper.wave_para_set
import util


def get_characteristics_wave(data_list):
    wave_result_list = []
    for data_one_day in (d_ for d_ in data_list if len(d_) > 0):
        wave_one_day_result = get_wave_result_one_day(data_one_day)
        wave_result_list.append(wave_one_day_result)

    wave_num_list = []
    wave_ret_list = []

    def mean_func(l):
        return sum(l) / len(l) if len(l) != 0 else 0.0

    for one_day_waves in wave_result_list:
        assert isinstance(one_day_waves, WaveRecord)
        wave_num = len(one_day_waves.wave_list)
        wave_ret_avg = mean_func([one_wave.cal_ret() for one_wave in one_day_waves.wave_list])
        wave_num_list.append(wave_num)
        wave_ret_list.append(wave_ret_avg)
    ret_dict = {'wave_num_avg': mean_func(wave_num_list), 'wave_ret_avg': mean_func(wave_ret_list)}
    print(ret_dict)
    return ret_dict


def get_wave_result_one_day(data_one_day):
    paras = WaveWrapper.wave_para_set.set_global_paras()
    wave_record = tick_rolling(data_date_stk=data_one_day, wave_paras=paras)
    print(wave_record)
    return wave_record


def tick_rolling(data_date_stk, wave_paras):
    # Wave Record Initiate
    wave_record_date_stk = WaveRecord()

    # Morning Wave ##
    prc_series_am = data_date_stk['mid_px'].select(util.in_morning_time)

    idx_num = 0
    while idx_num < len(prc_series_am.index):

        idx = prc_series_am.index[idx_num]   # 20160622,MK: Only Calculate Wave within 9:31:00 and 14:52:00
        if (idx >= util.hms2datetime(wave_paras.effective_begin_min)) and\
                (idx <= util.hms2datetime(wave_paras.effective_begin_max)):

            this_wave = cal_wave_from_any_tick(
                idx_num_now=idx_num, prc_series=prc_series_am, paras=wave_paras,
            )
            if this_wave is not None:
                assert isinstance(this_wave, OneWave)
                wave_record_date_stk.update_wave(this_wave)

                # If wave is effective, then skip to the End Tick
                time_end_this_wave = this_wave.end_time
                idx_num = list(prc_series_am.index).index(time_end_this_wave)
            else:
                idx_num += 1
        else:
            idx_num += 1

    # After Wave ##
    prc_series_pm = data_date_stk['mid_px'].select(util.in_afternoon_time)

    idx_num = 0
    while idx_num < len(prc_series_pm.index):

        idx = prc_series_pm.index[idx_num]   # 20160622,MK: Only Calculate Wave within 9:31:00 and 14:52:00
        if (idx >= util.hms2datetime(wave_paras.effective_begin_min))\
                and (idx <= util.hms2datetime(wave_paras.effective_begin_max)):

            this_wave = cal_wave_from_any_tick(
                idx_num_now=idx_num, prc_series=prc_series_pm,
                paras=wave_paras,
            )
            if this_wave is not None:
                assert isinstance(this_wave, OneWave)
                wave_record_date_stk.update_wave(this_wave)

                # If wave is effective, then skip to the End Tick
                time_end_this_wave = this_wave.end_time
                idx_num = list(prc_series_pm.index).index(time_end_this_wave)
            else:
                idx_num += 1
        else:
            idx_num += 1

    return wave_record_date_stk


def cal_wave_from_any_tick(idx_num_now, prc_series, date_str='', stk_str='', paras=None):
    if idx_num_now >= len(prc_series.index) - 1:
        return None
    time_now = prc_series.index[idx_num_now]
    prc_now = prc_series.iloc[idx_num_now]
    prc_next = prc_series.iloc[idx_num_now + 1]
    direction = 1 if prc_next > prc_now else (0 if prc_next == prc_now else -1)

    if direction == 0:
        return None

    idx_num_moving = idx_num_now + 1
    while True:
        # Return None, NO Observation
        if idx_num_moving >= len(prc_series.index):
            return None

        # Time Gap>5min
        time_moving = prc_series.index[idx_num_moving]

        if time_moving - time_now > paras.wave_max_duration:   # Revised 2016.06.16
            # break  # Original condition, if lasts more than 5min, then whole wave is ineffective

            prc_range = prc_series[idx_num_now:idx_num_moving]   # Delete the lastest point
            # Store the Peak point
            prc_end = prc_range.max() if direction == 1 else prc_range.min()
            time_end = prc_range.idxmax() if direction == 1 else prc_range.idxmin()

            # Store the Wave if effective
            wave = OneWave(date_str=date_str, stk_str=stk_str, start_time=time_now, end_time=time_end,
                           start_prc=prc_now, end_prc=prc_end,
                           direction=direction, wave_trend_limit=paras.wave_trend_limit,
                           wave_max_duration=paras.wave_max_duration, wave_min_duration=paras.wave_min_duration)
            # ============================= Most Important Output ################
            if wave.is_effective():
                return wave
            else:
                return None

        # Wave Breaker
        prc_range = prc_series[idx_num_now:idx_num_moving+1]
        breaker_flag = is_breaker_tick(prc_series_range=prc_range, direction=direction, paras=paras)
        if breaker_flag:
            # Store the Peak point
            prc_end = prc_range.max() if direction == 1 else prc_range.min()
            time_end = prc_range.idxmax() if direction == 1 else prc_range.idxmin()

            # Store the Wave if effective
            wave = OneWave(date_str=date_str, stk_str=stk_str, start_time=time_now, end_time=time_end,
                           start_prc=prc_now, end_prc=prc_end, direction=direction,
                           wave_trend_limit=paras.wave_trend_limit,
                           wave_max_duration=paras.wave_max_duration, wave_min_duration=paras.wave_min_duration)
            if wave.is_effective():
                # ====================== Most Important Output ====================
                return wave
            else:
                return None
        idx_num_moving += 1
    return None


def is_breaker_tick(prc_series_range, direction, paras):
    breaker_threshold_ret = paras.breaker_threshold_ret
    breaker_threshold_time = paras.breaker_threshold_time
    drawback_buffer_ret = paras.drawback_buffer_ret
    drawback_startpoint_ret = paras.drawback_startpoint_ret

    if direction == 1:
        # MK, 20160622, draw down >0.1% from start-point
        if prc_series_range.iloc[-1]/prc_series_range.iloc[0] - 1 < -drawback_startpoint_ret:
            return True
        if prc_series_range.iloc[-1]/prc_series_range.max() - 1 < -breaker_threshold_ret:  # draw down >0.2%
            return True
        if prc_series_range.index[-1] - prc_series_range.idxmax() > breaker_threshold_time:
            # Whether to setup immune ret 0.001
            if prc_series_range.iloc[-1]/prc_series_range.max() - 1 < -drawback_buffer_ret:
                return True
            # return True
    elif direction == -1:
        if prc_series_range.iloc[-1]/prc_series_range.iloc[0] - 1 > drawback_startpoint_ret:  # MK, 20160622
            return True
        if prc_series_range.iloc[-1]/prc_series_range.min() - 1 > breaker_threshold_ret:  # draw down >0.2%
            return True
        if prc_series_range.index[-1] - prc_series_range.idxmin() > breaker_threshold_time:
            if prc_series_range.iloc[-1]/prc_series_range.min() - 1 > drawback_buffer_ret:
                return True
            # return True

    return False


class OneWave:

    def __init__(self, date_str, stk_str, start_time, end_time, start_prc, end_prc, direction,
                 wave_max_duration, wave_min_duration, wave_trend_limit):
        self.date_str = date_str
        self.stk_str = stk_str
        self.start_time = start_time
        self.end_time = end_time
        self.start_prc = start_prc
        self.end_prc = end_prc
        self.direction = direction

        self.wave_max_duration = wave_max_duration
        self.wave_min_duration = wave_min_duration
        self.wave_trend_limit = wave_trend_limit

    def is_effective(self):
        if (self.end_time - self.start_time > self.wave_max_duration)\
                or (self.end_time - self.start_time < self.wave_min_duration):
            return False
        if -self.wave_trend_limit < (self.end_prc / self.start_prc) - 1 < self.wave_trend_limit:
            return False
        return True

    def cal_ret(self):
        ret = (self.end_prc / self.start_prc - 1) if self.start_prc != 0 else 0.0
        return ret

    def __str__(self):
        return '{:.2f},{:.2f}.'.format(self.start_prc/10000, self.end_prc/10000)


class WaveRecord:
    def __init__(self):
        self.wave_list = []

    def update_wave(self, one_wave):
        assert isinstance(one_wave, OneWave)
        self.wave_list.append(one_wave)

    def __repr__(self):
        return str(self.wave_list)
