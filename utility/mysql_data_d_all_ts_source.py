import tushare as ts
import pymysql

# 定义 SQL 注入语句
sql_insert_command = "INSERT INTO stock_daily_tick (code, date, volume, open, close, high, low) VALUES ('%', '%', %, %, %, %, %);"

# 定义 SQL Server 连接信息
sql_cofig = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'body804', 'db': 'stockdata',
             "charset": 'utf8mb4', "cursorclass": "pymysql.cursors.DictCursor"}


def get_d_data(code):
    return ts.get_k_data(code, ktype='D')


# 注入 SQL 数据库
def write_d_data(connection, data):
    for index, row in data.iterrows():
        row_tuple = (row['code'], row['date'], row['volume'], row['open'], row['close'], row['high'], row['low'])
        try:
            connection.cursor().execute(sql_insert_command, row_tuple)
        except:
            pass
    connection.commit()


def main():
    connection = pymysql.connect(**sql_cofig)
    stock_list = ts.get_stock_basics()
    for code, info in stock_list.iterrows():
        print("Trying: {}".format(code))
        print(info)
        for each in range(5):
            try:
                write_d_data(connection, get_d_data(code))
                print("Written: {}".format(code))
                break
            except:
                print("Retrying: {}".format(code))
    connection.close()


if __name__ == "__main__":
    main()
