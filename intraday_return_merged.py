# -*- coding: utf-8 -*-
"""
Created on 2016/10/26 17:14

@author: qiding
"""

import pandas as pd
import datetime


def str2datetime(s):
    try:
        date = datetime.datetime.strptime(s, '%Y/%m/%d')
    except:
        date = datetime.datetime.strptime(s, '%Y-%m-%d')
    return date


def one_file_data(file_path):
    data_ = pd.read_csv(file_path, date_parser=str2datetime, parse_dates=['date'])
    data_ = data_.set_index('date')
    data__ = data_.rename(columns={'ret(d_pool_size)': 'ret', 'pool_size': 'weight'})
    return data__


def main():
    path_root = 'C:\\Users\\qiding\\Desktop\\'
    file_name_list = ['1t0report', '2t0report', '7t0report', '11t0report',
                      '12t0report', '16t0report', '17t0report']

    ret_list = []
    weight_list = []
    for file_name in file_name_list:
        file_path = path_root + file_name + '.csv'
        data_ = one_file_data(file_path)
        ret_list.append(data_['ret'])
        weight_list.append(data_['weight'])

    ret_df = pd.concat(ret_list, keys=file_name_list, axis=1)
    weight_df = pd.concat(weight_list, keys=file_name_list, axis=1)
    weight_df2 = weight_df.apply(lambda x: x/x.sum(), axis=1)

    ret_weight = ret_df * weight_df2
    ret_sum = ret_weight.sum(axis=1)
    ret_sum_cum = ret_sum.cumsum()

    ret_all = pd.concat([ret_sum, ret_sum_cum], axis=1, keys=['ret', 'ret_cum'])

    ret_all.to_csv(path_root+'intraday_return_merged.csv')

if __name__ == '__main__':
    main()
