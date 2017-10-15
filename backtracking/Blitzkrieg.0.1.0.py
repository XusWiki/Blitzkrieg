import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
import datetime

# 设定期初与期间
date_config = [0, 365, 15]
date_today = datetime.date.today() - datetime.timedelta(days=date_config[0])
date_yesterday = date_today - datetime.timedelta(days=date_config[1])
date_start_trading_day = date_config[2]

# 设定股票仓
portfolio = ['002484']
fund = 100000
profit = []


# 生成类，测试股票于期间的价格变化
class Backtrack:
    def __init__(self, code):
        self.code = str(code)
        try:
            self.data = pd.read_pickle('../data/{}_{}.pkl'.format(self.code, date_today))
        except:
            self.data = ts.get_k_data(str(code), start=str(date_yesterday), end=str(date_today))
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data.set_index("date", inplace=True)
            pd.to_pickle(self.data, '../data/{}_{}.pkl'.format(self.code, date_today))
        self.trading_days = len(self.data['open'])
        self.initial_fund = (fund / len(portfolio))
        self.real_time_fund = (fund / len(portfolio))
        self.real_time_stock = 0
        self.real_time_stock_cost = 0
        self.real_time_profit = 0
        self.strategy_long_point = 0
        self.strategy_short_point = 0
        self.log = '''股票代码 {} 交易：\n'''.format(self.code)

    def trade_long(self, price):
        volume = self.real_time_fund // price
        if volume > 0:
            self.real_time_fund -= (price * volume)
            self.real_time_stock += volume
            self.real_time_stock_cost = price
            self.log += '[L] {} 元，基金余额 {} 元，持有 {} 股。\n'.format('%.2f' % price, '%.2f' % self.real_time_fund,
                                                                int(volume))

    def trade_short(self, price):
        if self.real_time_stock == 0:
            pass
        elif self.real_time_stock > 0:
            self.real_time_fund += (price * self.real_time_stock)
            self.real_time_stock = 0
            self.real_time_profit = self.real_time_fund - self.initial_fund
            self.log += '[S] {} 元，基金余额 {} 元。\n'.format('%.2f' % price, '%.2f' % self.real_time_fund)

    def do_log(self):
        print(self.log)

    # ================================你的游乐场================================

    def do_calculate(self):
        # 为方便随时增加或删除指标，此处将计算方法分开为多个循环。在使用大量数据时应注意运行效率问题。

        '''计算每日价格变动'''

        # try:
        #     self.data['price_change'].iloc[0]
        # except:
        #     self.data['price_change'] = 0
        #     for each in range(1, self.trading_days):
        #         self.data['price_change'].iloc[each] = self.data['close'].iloc[each] - self.data['close'].iloc[each - 1]

        '''计算每日价格变动的均值'''

        # self.data['index_1'] = 0
        # for each in range(self.trading_days):
        #     self.data['index_1'].iloc[each] = self.data['close'].iloc[0:each].mean()
        #
        # '''计算每日价格变动的均值'''
        #
        # self.data['index_2'] = 0
        # for each in range(self.trading_days):
        #     self.data['index_2'].iloc[each] = self.data['close'].iloc[0:each].median()

        '''Temp Code'''

        self.data['price_change'] = 0
        self.data['ma'] = 0
        self.data['median'] = 0
        self.data['index_1'] = 0
        self.data['index_2'] = 0
        for each in range(len(self.data['open'])):
            self.data['price_change'].iloc[each] = self.data['close'].iloc[each] - self.data['close'].iloc[each - 1]
            try:
                self.data['ma'].iloc[each] = (self.data['price_change'].iloc[each] * 5 + self.data['price_change'].iloc[
                    each - 1] * 4 +
                                              self.data['price_change'].iloc[each - 2] * 3 +
                                              self.data['price_change'].iloc[
                                                  each - 3] * 2 + self.data['price_change'].iloc[each - 4]) / 15
            except:
                pass
            self.data['median'].iloc[each] = self.data['price_change'].iloc[0:each].median()
            self.data['index_1'].iloc[each] = self.data['close'].iloc[each - 1] + self.data['ma'].iloc[each]
            self.data['index_2'].iloc[each] = self.data['close'].iloc[each - 1] + self.data['median'].iloc[each]

    def do_strategy(self):
        '''执行计算'''
        self.do_calculate()
        '''执行交易'''
        for each in range(0, self.trading_days - 1):
            if each < date_start_trading_day:
                continue
            elif self.data['index_1'].iloc[each] < self.data['index_2'].iloc[each] and self.data['index_1'].iloc[
                        each - 1] >= self.data['index_2'].iloc[each - 1]:
                try:
                    self.trade_long(self.data['open'].iloc[each + 1])

                except:
                    print('Error: 98')

            elif self.data['index_1'].iloc[each] > self.data['index_2'].iloc[each] and self.data['index_1'].iloc[
                        each - 1] <= self.data['index_2'].iloc[each - 1]:
                try:
                    self.trade_short(self.data['open'].iloc[each + 1])
                    # if self.real_time_profit <= 0:
                    #     pass
                    # else:
                    # for every in range(each, self.trading_days):
                    #     self.data['index_1'].iloc[every] = self.data['price_change'].iloc[each - 15:every].mean()
                    #     self.data['index_2'].iloc[every] = self.data['price_change'].iloc[each - 15:every].median()
                except:
                    print('Error: 103')


'''用投资组合执行策略并返回计算结果'''

for each in portfolio:
    exec("S_{} = Backtrack(code = '{}')".format(each, each))
    exec('S_{}.do_calculate()'.format(each))
    exec('S_{}.do_strategy()'.format(each))
    exec('S_{}.do_log()'.format(each))
    exec('profit.append(S_{}.real_time_profit)'.format(each))

total_profit = np.array(profit).sum()
return_rate = (total_profit / fund) * 100

print('投资组合总成本 {} 元，收益 {} 元，回报率 {}%。'.format(fund, "%.2f" % total_profit, "%.3f" % return_rate))
