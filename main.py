# -*- coding: utf-8 -*-
"""
Created on 2016/10/11 10:43

@author: qiding
"""

from multiprocessing import Pool

from intraday_market_data_load import *
from intraday_team_data_load import *
from my_path import *


def main():

    intraday_team_return_data = get_intraday_team_return_data()
    stock_month_list = get_stock_month_list(intraday_team_return_data)

    stock_list = []
    date_list = []
    intraday_characteristics_list = []

    pool_num = 26
    pool = Pool(pool_num)

    result = []
    for num, (stock, month) in enumerate(stock_month_list):
        date_last_month = get_date_list_last_month(month, stock)
        stock_list.append(stock)
        date_list.append(date_last_month)

        result.append(pool.apply_async(one_stock_month_func, (date_last_month, stock,)))

        # characteristics_this_stock_date_dict = one_stock_month_func(date_last_month, stock)

        # intraday_characteristics_list.append(characteristics_this_stock_date_dict)

    pool.close()
    pool.join()

    for res in result:
        intraday_characteristics_list.append(res.get())

    data_new = pd.DataFrame(intraday_characteristics_list, index=list(zip(stock_list, date_list))).reset_index()
    data_new['coid'] = data_new['index'].apply(lambda x: x[0])
    data_new['date'] = data_new['index'].apply(lambda x: x[1])
    data_new = data_new.drop('index', axis=1)

    data_merged = pd.merge(intraday_team_return_data, data_new, on=['coid', 'date'], how='outer')
    data_merged.to_csv(output_path + 'intraday_characteristics.csv', index=None)
    print(output_path + 'intraday_characteristics.csv' + ' done')


def one_stock_month_func(date_last_month, stock):
    signal = '{}, {}, {}, begin'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), stock, date_last_month)
    print(signal)
    date_list_last_month = [date_last_month + '-' + str(date).zfill(2) for date in range(1, 32)]
    data_this_month = []
    for date_one_day in date_list_last_month:
        data_this_day = get_raw_data(stock, date_one_day)
        data_this_month.append(data_this_day)
    data_this_stock_date = pd.DataFrame(pd.concat(data_this_month, axis=0))
    signal = '{}, {}, {}, data loading end, data length: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), stock, date_last_month, len(data_this_stock_date.index))
    print(signal)

    characteristics_this_stock_date_dict = get_characteristics(data_this_stock_date)
    print(characteristics_this_stock_date_dict)
    # signal = '{}, {}/{} completed, {}, {}'\
    #     .format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), num, len(stock_month_list), stock, month)
    signal = '{}, {}, {}, completed'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), stock, date_last_month)
    print(signal)
    return characteristics_this_stock_date_dict


def get_date_list_last_month(month, stock):

    year_, month_ = month.split('-')
    if int(month_) == 1:
        year_last_int = int(year_) - 1
        month_last_int = 12
    else:
        year_last_int = int(year_)
        month_last_int = int(month_) - 1

    date_last_month = str(year_last_int) + '-' + str(month_last_int).zfill(2)

    return date_last_month


if __name__ == '__main__':
    main()
