# -*- coding: utf-8 -*-
"""
Created on 2016/11/3 16:44

@author: qiding
"""


import datetime


class set_global_paras:
    breaker_threshold_ret = .003
    breaker_threshold_time = datetime.timedelta(seconds=10)
    drawback_buffer_ret = .001
    drawback_startpoint_ret = .001

    # Effective Wave Parameters
    wave_trend_limit = .008
    wave_max_duration = datetime.timedelta(seconds=300)
    wave_min_duration = datetime.timedelta(seconds=60)

    # Effective Begin Time Range
    effective_begin_min = "93100"
    effective_begin_max = "145200"

    # Wave Returns Parameters       # MK, 20160627
    # trade_depth = [1,2,3]
    open_ret_position = .2
    close_ret_position = .9
    vol_start_position = .15
    vol_end_position = .25
    capacity_ratio = 1
