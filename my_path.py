# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 11:18

@author: qiding
"""

import socket

name = socket.gethostname()

if name == '2013-20151201LG':
    path_root = 'F:\\IntradayTeamPerformanceAnalysis\\'
    intraday_team_return_path = path_root + 'intraday_team_return.csv'

    raw_data_path_root = '\\\\2013-20151109CR\\StockTick\\'
    output_path = 'F:\\IntradayTeamPerformanceAnalysis\\'
else:
    path_root = 'C:\\Users\\dqi\\Documents\\Data\\IntradayTeamPerformanceAnalysis\\'
    intraday_team_return_path = path_root + 'intraday_team_return.csv'

    raw_data_path_root = '\\\\2013-20151109CR\\StockTick\\'
    output_path = 'C:\\Users\\dqi\\Documents\\Data\\IntradayTeamPerformanceAnalysis\\'
