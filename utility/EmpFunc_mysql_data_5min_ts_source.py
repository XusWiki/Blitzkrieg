'''
采用新的SQL注入方法，更简洁。
'''
#from sqlalchemy import create_engine
#import tushare as ts

#df = ts.get_tick_data('600848', date='2014-12-22')
#engine = create_engine('sqlite:///../data/stock_data.db/stock_d')

#存入数据库
#df.to_sql('tick_data',engine)

#追加数据到现有表
#df.to_sql('tick_data',engine,if_exists='append')
'''
========================================
'''

import tushare as ts
from sqlalchemy import create_engine
import time

# 定义 SQL 注入语句
sql_insert_command = "INSERT INTO stock_5min_tick (code, date, volume, open, close, high, low) VALUES ('%', '%', %, %, %, %, %);"

# 定义 SQL Server 连接信息
sql_cofig = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'body804', 'db': 'stockdata',
             "charset": 'utf8mb4', "cursorclass": "pymysql.cursors.DictCursor"}


def get_5min_data(code):
    return ts.get_k_data(code, ktype='5')


# 注入 SQL 数据库
def write_5min_data(connection, data):
    for index, row in data.iterrows():
        row_tuple = (row['code'], row['date'], row['volume'], row['open'], row['close'], row['high'], row['low'])
        try:
            connection.cursor().execute(sql_insert_command, row_tuple)
        except:
            pass
    connection.commit()

engine = create_engine()


def main():
    connection = pymysql.connect(**sql_cofig)
    stock_list = ts.get_stock_basics()
    for code, info in stock_list.iterrows():
        print("Trying: {}".format(code))
        print(info)
        for each in range(5):
            try:
                write_5min_data(connection, get_5min_data(code))
                print("Written: {}".format(code))
                break
            except:
                print("Retrying: {}".format(code))
    connection.close()


if __name__ == "__main__":
    main()
