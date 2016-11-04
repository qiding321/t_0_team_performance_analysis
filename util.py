# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 11:37

@author: qiding
"""

import datetime


def fill_na_method(data_series, col_name):
    if col_name.find('date') >= 0:
        data_series_new = data_series.fillna(method='ffill')
    elif col_name.find('price') >= 0:
        data_series_new = data_series.fillna(method='ffill')
    elif col_name.find('mid_px') >= 0:
        data_series_new = data_series.fillna(method='ffill')
    elif col_name.find('volume') >= 0 and col_name.find('accvolume') == -1:
        data_series_new = data_series.fillna(value=0)
    elif col_name.find('accvolume') >= 0:
        data_series_new = data_series.fillna(method='ffill')
    elif any([col_name.find('bid') >= 0, col_name.find('ask') >= 0, col_name.find('bsize') >= 0, col_name.find('asize') >= 0]):
        data_series_new = data_series.fillna(method='ffill')
    elif col_name.find('amount') >= 0:
        data_series_new = data_series.fillna(value=0)
    elif col_name.find('trans') >= 0:
        data_series_new = data_series.fillna(value=0)
    elif col_name == 'code' or col_name == 'wind_code':
        data_series_new = data_series
    else:
        raise LookupError
    return data_series_new


def hms2datetime(hms_str):
    try:
        if len(hms_str) >= 8:
            hms_str = str(hms_str)[:-3]
        else:
            hms_str = str(hms_str)
        return datetime.datetime.strptime(hms_str,'%H%M%S')
    except:
        hms_str = '90000'
        # print("Date Error:",hms_str)
        return datetime.datetime.strptime(hms_str,'%H%M%S')

mkt_open_time_morning_str = '93000'
mkt_close_time_morning_str = '113000'
mkt_open_time_afternoon_str = '130000'
mkt_close_time_afternoon_str = '150000'

mkt_open_time_morning = hms2datetime(mkt_open_time_morning_str)
mkt_close_time_morning = hms2datetime(mkt_close_time_morning_str)
mkt_open_time_afternoon = hms2datetime(mkt_open_time_afternoon_str)
mkt_close_time_afternoon = hms2datetime(mkt_close_time_afternoon_str)


def in_morning_time(t):
    if isinstance(t,str):
        t = hms2datetime(t)
    flag = mkt_open_time_morning <= t <= mkt_close_time_morning
    return flag


def in_afternoon_time(t):
    if isinstance(t,str):
        t = hms2datetime(t)
    flag = mkt_open_time_afternoon <= t <= mkt_close_time_afternoon
    return flag
