from sqlite3 import Connection, Cursor

import pymysql

from commons.yaml_util import read_yaml


class DatabaseUtil:

    def creat_conn(self):
        """
        创建连接
        :return:返回连接
        """
        self.conn: Connection = pymysql.connect(
            host="39.102.59.111",
            user="root",
            passwd="TzZ%h2#Y",
            database="primary_eink_test",
            port=23306
        )
        return self.conn

    # 执行sql
    def execute_sql(self):
        sql = "select * from primary_user where name = '刘志鹏test';"
        # 创建游标
        self.cs: Cursor = self.conn.cursor()
        # 通过游标去执行sql
        self.cs.execute(sql)
        value = self.cs.fetchone()
        return value

    # 关闭资源
    def close_conn(self):
        self.cs.close()
        self.conn.close()


# def get_database_info(name):
#     """
#     获取数据库信息
#     :param name: 数据库名称
#     :return:
#     """
#     database_info = read_yaml("envinfo/datebase_info")
#     for database in database_info:
#         if database["name"] == name:
#             return database["info"]
#
#
# conn: Connection = pymysql.connect(
#
# )
if __name__ == '__main__':
    du = DatabaseUtil()
    du.creat_conn()
    print(du.execute_sql())
    du.close_conn()
