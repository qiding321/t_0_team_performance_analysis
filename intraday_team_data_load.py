# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 11:15

@author: qiding
"""

import pandas as pd
from my_path import *


def get_intraday_team_return_data():
    data_raw = pd.read_csv(intraday_team_return_path)
    data_raw['month'] = data_raw['date'].apply(lambda x: x[:-3])
    intraday_team_return_data = data_raw.groupby(['month', 'coid'], group_keys=False, as_index=False)[['traded_return', 'traded_amount', 'traded_volume']].mean()
    intraday_team_return_data['coid'] = intraday_team_return_data['coid'].apply(lambda i: str(i).zfill(6))
    return intraday_team_return_data


def get_stock_month_list(intraday_team_return_data):
    return list(zip(list(intraday_team_return_data['coid']), list(intraday_team_return_data['month'])))
