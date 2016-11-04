# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 11:15

@author: qiding
"""


import datetime

import pandas as pd
import numpy as np

from my_path import *
import resample_dicts
import const
import util


def get_raw_data(stock, date, wave_flag=False):
    if stock[0] == '6':
        market_this_stk = 'SH'
    else:
        market_this_stk = 'SZ'
    tick_file_path = raw_data_path_root + 'Tick\\' + market_this_stk + '\\' + date.replace('-', '') + '\\' + stock + '.csv'
    tran_file_path = raw_data_path_root + 'Transaction\\' + market_this_stk + '\\' + date.replace('-', '') + '\\' + stock + '.csv'

    try:
        stk_data = pd.read_csv(tick_file_path, parse_dates=['time'], date_parser=lambda x: datetime.datetime.strptime(str(x), '%H%M%S%f'), encoding='gbk').drop_duplicates('time', keep='last').set_index('time')
        if not wave_flag:
            transaction_data = pd.read_csv(tran_file_path, parse_dates=['time'], date_parser=lambda x: datetime.datetime.strptime(str(x), '%H%M%S%f'), encoding='gbk').set_index('time')
        else:
            transaction_data = None
    except OSError:
        return pd.DataFrame()

    if wave_flag:
        stk_data2 = filter_time(stk_data)
        func_dict = resample_dicts.stk_func_dict
        cols = list(set(stk_data2.columns).intersection(set(func_dict.keys())))
        stk_data3 = stk_data2[cols]
        data_merged_fill_na = fill_na(stk_data3)
        data_merged_drop_limit = drop_limit(data_merged_fill_na)
        px_mid = (data_merged_drop_limit['bid1'] + data_merged_drop_limit['ask1']) / 2
        data_merged_drop_limit.loc[:, 'mid_px'] = px_mid
        return data_merged_drop_limit

    else:
        stk_data_resample = clean_data_stk(stk_data)
        transaction_data_resample = clean_data_transaction(transaction_data)

        data_merged = pd.DataFrame(pd.concat([
            stk_data_resample,
            transaction_data_resample,
        ], axis=1))
        data_merged_fill_na = fill_na(data_merged)
        data_merged_drop_limit = drop_limit(data_merged_fill_na)
        return data_merged_drop_limit


def get_characteristics(data_df):

    px_mid = pd.Series((data_df['bid1'] + data_df['ask1']) / 2)
    ret = px_mid.pct_change()
    volume = data_df['buyvolume'] + data_df['sellvolume']
    ret_shift = pd.DataFrame(pd.concat([ret, ret.shift(1)], axis=1)).dropna()

    volume_zero_index = volume == 0

    spread = data_df['ask1'] - data_df['bid1']
    spread_rel = spread / px_mid
    auto_corr = ret_shift.corr().iloc[0, 1]
    abs_ret_volume = np.abs(ret) / volume
    abs_ret_volume[volume_zero_index] = np.nan
    volatility = ret.std()
    volume_sum = volume.sum()

    char_dict = dict(zip(
        ['spread', 'spread_rel', 'auto_corr', 'abs_ret_volume', 'volatility', 'volume'],
        [
            (var_.dropna().mean() if isinstance(var_, pd.Series) else var_) for var_ in
            [spread, spread_rel, auto_corr, abs_ret_volume, volatility, volume_sum]
         ]
    ))

    return char_dict


def clean_data_stk(stk_data, freq='3s'):
    func_dict = resample_dicts.stk_func_dict

    cols = list(set(stk_data.columns).intersection(set(func_dict.keys())))
    func_dict2 = dict((x_, func_dict[x_]) for x_ in cols)

    resample_data = stk_data.resample(freq, label='right', closed='left')[cols].agg(func_dict2)
    resample_data2 = filter_time(resample_data)

    return resample_data2


def clean_data_transaction(transaction_data, freq='3s'):
    transaction_data['amount'] = transaction_data['trade_price'] * transaction_data['trade_volume']

    transaction_data_buy = transaction_data[transaction_data['bs_flag'] == ord('B')]
    transaction_data_sell = transaction_data[transaction_data['bs_flag'] == ord('S')]

    columns = [
        'newprice',
        'totalamount', 'totalvolume', 'totaltransaction',
        'buytrans', 'selltrans',
        'buyvolume', 'sellvolume',
        'buyamount', 'sellamount'
        ]

    def resample_sum(s_):
        return s_.resample(freq, label='right', closed='left').sum()

    def resample_last(s_):
        return s_.resample(freq, label='right', closed='left').apply('last')

    def resample_count(s_):
        return s_.resample(freq, label='right', closed='left').count()

    newprice = resample_last(transaction_data['trade_price'])
    totalamount = resample_sum(transaction_data['amount'])
    totalvolume = resample_sum(transaction_data['trade_volume'])
    totaltransaction = resample_count(transaction_data['trade_volume'])

    buyamount = resample_sum(transaction_data_buy['amount'])
    buyvolume = resample_sum(transaction_data_buy['trade_volume'])
    buytrans = resample_count(transaction_data_buy['trade_volume'])

    sellamount = resample_sum(transaction_data_sell['amount'])
    sellvolume = resample_sum(transaction_data_sell['trade_volume'])
    selltrans = resample_count(transaction_data_sell['trade_volume'])

    resample_data = pd.DataFrame([
        newprice,
        totalamount, totalvolume, totaltransaction,
        buytrans, selltrans,
        buyvolume, sellvolume,
        buyamount, sellamount
        ], index=columns).T

    resample_data2 = filter_time(resample_data)

    return resample_data2


def filter_time(data):
    data_new = data.select(lambda x: const.MARKET_OPEN_TIME <= x <= const.MARKET_CLOSE_TIME_NOON or const.MARKET_OPEN_TIME_NOON<= x <= const.MARKET_END_TIME)
    return data_new


def fill_na(data_df):
    col_list = []
    for col_name in data_df.columns:
        col_new = util.fill_na_method(data_df[col_name], col_name)
        col_list.append(col_new)
    data_df_ = pd.DataFrame(pd.concat(col_list, axis=1, keys=data_df.columns))
    return data_df_


def drop_limit(data_df):
    index = (data_df['bid1'] != 0) & (data_df['ask1'] != 0)
    return data_df[index]
