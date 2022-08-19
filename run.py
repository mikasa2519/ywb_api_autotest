import pytest

from commons.yaml_util import read_yaml
from hot_loads.debug_talk import DebugTalk

if __name__ == '__main__':
    pytest.mian()
    # database_info = [
    #                  {'name': '小学本测试环境', 'info': {'hostname': '39.102.59.111', 'port': 23306, 'username': 'root', 'password': 'TzZ%h2#Y'}},
    #                  {'name': '小学本预上线环境', 'info': {'hostname': '172.17.27.166', 'port': 43306, 'username': 'primary_user', 'password': 'f0R#KFj!^Qtx@QtW'}},
    #                  {'name': '小学本测试环境redis', 'info': {'hostname': '39.102.59.111', 'port': 22, 'username': 'roo', 'password': 'JYJJmr0z'}}
    #                 ]
    # for database in database_info:
    #     if database["name"] == "小学本测试环境":
    #         print(database["info"])