import tushare as ts
import sqlite3

# 定义 SQL 注入语句
sql_insert_command = "INSERT INTO stock_5min_tick (code, date, volume, open, close, high, low) VALUES ('{}', '{}', {}, {}, {}, {}, {});"

# 定义 SQLite 数据库文件所在位置。
sql_cofig = "stock_data.db"


def get_5min_data(code):
    return ts.get_k_data(code, ktype='5')


# 注入 SQL 数据库
def write_5min_data(connection, data):
    for index, row in data.iterrows():
        try:
            # 在此处进行修改
            connection.cursor().execute(sql_insert_command.format(row['code'], row['date'], row['volume'], row['open'], row['close'], row['high'], row['low']))
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
                write_5min_data(connection, get_5min_data(code))
                print("Written: {}".format(code))
                break
            except:
                print("Retrying: {}".format(code))
    connection.close()


if __name__ == "__main__":
    main()
