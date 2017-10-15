import tushare as ts
import sqlite3
import dateutil.parser as dateparser

# 定义 SQL 注入语句
sql_insert_command = "INSERT INTO stock_d_tick (id, datetime, code, date, open, close, high, low, volume) VALUES ({}, {}, '{}', '{}', {}, {}, {}, {}, {});"

# 定义 SQLite 数据库文件所在位置。
sql_cofig = "stock_data.db"


def get_day_data(code):
    return ts.get_k_data(code, ktype='D')


# 注入 SQL 数据库
def write_day_data(connection, data):
    for index, row in data.iterrows():
        datetime_str =
        datetime = int(time.mktime(time.strptime(row['date'].format(' 15:00:00'), "%Y-%m-%d %H:%M:%S"))) * 10000
        id = int('101{}'.format(datetime))
        try:
            # 在此处进行修改
            connection.cursor().execute(sql_insert_command.format(id, datetime, row['code'], row['date'], row['open'], row['close'], row['high'], row['low'], row['volume']))
        except:
            print('Error: 16')
            pass
    connection.commit()


def main():
    connection = sqlite3.connect(sql_cofig)
    stock_list = ts.get_stock_basics()
    for code, info in stock_list.iterrows():
        print("Trying: {}".format(code))
        print(info)
        for each in range(5):
            try:
                write_day_data(connection, get_day_data(code))
                print("Written: {}".format(code))
                break
            except:
                print("Retrying: {}".format(code))
    connection.close()


if __name__ == "__main__":
    main()
