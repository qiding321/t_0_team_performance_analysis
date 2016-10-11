# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 11:37

@author: qiding
"""


def fill_na_method(data_series, col_name):
    if col_name.find('date') >= 0:
        data_series_new = data_series.fillna(method='ffill')
    elif col_name.find('price') >= 0:
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
    else:
        raise LookupError
    return data_series_new
