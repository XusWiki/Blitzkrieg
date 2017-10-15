import sys
import time
import datetime
import multiprocessing
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import tushare as ts

# 设定期初与期间
date_config = [0, 365, 15]
date_today = datetime.date.today() - datetime.timedelta(days=date_config[0])
date_yesterday = date_today - datetime.timedelta(days=date_config[1])
date_start_trading_day = date_config[2]

# 设定股票仓
portfolio = sys.argv[1:]
fund = 100000
profit = []


# 生成类，测试股票于期间的价格变化
class Backtrack(multiprocessing.Process):
    def __init__(self, code):
        multiprocessing.Process.__init__(self)
        self.code = str(code)
        try:
            self.data = pd.read_pickle('../data/{}_{}.pkl'.format(self.code, date_today))
        except:
            self.data = ts.get_k_data(str(code), start=str(date_yesterday), end=str(date_today))
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data.set_index("date", inplace=True)
            pd.to_pickle(self.data, '../data/{}_{}.pkl'.format(self.code, date_today))
        self.trading_days = len(self.data['open'])
        self.time_series = self.data.index.tolist()
        self.initial_fund = (fund / len(portfolio))
        self.real_time_fund = (fund / len(portfolio))
        self.real_time_stock = 0
        self.real_time_stock_cost = 0
        self.real_time_profit = 0
        self.strategy_long_point = 0
        self.strategy_short_point = 0
        self.log = {str(self.time_series[0])[0:10]: '''{} RUNNING STRATEGY'''.format(self.code)}

    def trade_long(self, price, date_str):
        # try:
        #     self.trade_long(self.data['open'].iloc[each + 1], str(self.time_series[each])[0:10])
        # except:
        #     pass
        volume = self.real_time_fund // price
        if volume > 0:
            self.real_time_fund -= (price * volume)
            self.real_time_stock += volume
            self.real_time_stock_cost = price
            self.log[date_str] = '[Long] ${} [Fund] ${} [Volume] {}'.format('%.2f' % price, '%.2f' % self.real_time_fund, int(volume))


    def trade_short(self, price, date_str):
        # try:
        #     self.trade_short(self.data['open'].iloc[each + 1], str(self.time_series[each])[0:10])
        # except:
        #     pass
        if self.real_time_stock == 0:
            pass
        elif self.real_time_stock > 0:
            self.real_time_fund += (price * self.real_time_stock)
            self.real_time_stock = 0
            self.real_time_profit = self.real_time_fund - self.initial_fund
            self.log[date_str] = '[Short] ${} [Fund] ${}'.format('%.2f' % price, '%.2f' % self.real_time_fund)

    def do_log(self):
        print_log = pd.Series(self.log)
        print(print_log)

    # ================================你的游乐场================================

    def do_calculate(self):
        # self.data['price_change'] = 0
        # self.data['price_change_in_day'] = 0
        self.data['ma5'] = 0
        self.data['ma10'] = 0
        for each in range(len(self.data['open'])):
            if each > 3 and each <= 8:
                self.data['ma5'].iloc[each] = (self.data['close'].iloc[each] * 5 + self.data['close'].iloc[
                    each - 1] * 4 + self.data['close'].iloc[each - 2] * 3 + self.data['close'].iloc[each - 3] * 2 +
                                               self.data['close'].iloc[each - 4]) / 15
            elif each > 8:
                self.data['ma5'].iloc[each] = (self.data['close'].iloc[each] * 5 + self.data['close'].iloc[
                    each - 1] * 4 + self.data['close'].iloc[each - 2] * 3 + self.data['close'].iloc[each - 3] * 2 +
                                               self.data['close'].iloc[each - 4]) / 15
                self.data['ma10'].iloc[each] = (self.data['close'].iloc[each] * 9 + self.data['close'].iloc[
                    each - 1] * 8 + self.data['close'].iloc[each - 2] * 7 + self.data['close'].iloc[each - 3] * 6 +
                                                self.data['close'].iloc[each - 4] * 5 + self.data['close'].iloc[
                                                    each - 5] * 4 + self.data['close'].iloc[each - 6] * 3 +
                                                self.data['close'].iloc[each - 7] * 2 + self.data['close'].iloc[
                                                    each - 8]) / 45
            else:
                self.data['ma5'].iloc[each] = 0
                self.data['ma10'].iloc[each] = 0

    def do_strategy(self):
        for each in range(self.trading_days):
            if each >= date_start_trading_day:
                if self.data['ma5'].iloc[each] > self.data['ma10'].iloc[each] and self.data['ma5'].iloc[each - 1] < self.data['ma10'].iloc[each - 1]:
                    try:
                        self.trade_long(self.data['open'].iloc[each + 1], str(self.time_series[each])[0:10])
                    except:
                        pass
                elif self.data['ma5'].iloc[each] < self.data['ma10'].iloc[each] and self.data['ma5'].iloc[each - 1] > self.data['ma10'].iloc[each - 1]:
                    try:
                        self.trade_short(self.data['open'].iloc[each + 1], str(self.time_series[each])[0:10])
                    except:
                        pass
            else:
                pass


# '''用投资组合执行策略并返回计算结果'''
def do_backtrack():
    for each in portfolio:
        temp_name = 'S_{}'.format(each)
        exec("{} = Backtrack('{}')".format(temp_name, each))
        exec('S_{}.do_calculate()'.format(each))
        exec('S_{}.do_strategy()'.format(each))
        exec('S_{}.do_log()'.format(each))
        exec('profit.append(S_{}.real_time_profit)'.format(each))
        time.sleep(1)


if __name__ == "__main__":
    start_time = time.clock()
    backtrack_process = multiprocessing.Process(target=do_backtrack())
    backtrack_process.start()
    backtrack_process.join()
    total_profit = np.array(profit).sum()
    return_rate = (total_profit / fund) * 100
    end_time = time.clock()
    print('[Initial Fund] {} [Profit] {} [Return Rate] {}%'.format(fund, "%.2f" % total_profit, "%.3f" % return_rate))
    print("RUNNING TIME: %f s" % (end_time - start_time))