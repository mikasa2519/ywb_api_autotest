import re
import sys

import paramiko
import pytest

from commons.yaml_util import clear_yaml
from hot_loads.debug_talk import DebugTalk


# 执行用例前清除extract.yaml文件
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    clear_yaml("extract.yaml")


# 执行用例前清除服务器日志
@pytest.fixture(scope="session", autouse=True)
def get_data_from_log():
    # 获取环境信息
    env_info = DebugTalk().read_envinfo_yaml("env")
    # 连接测试环境
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(compress=True, **env_info)
    # 服务器连接失败异常处理
    try:
        client.connect(compress=True, **env_info)
    except Exception as e:
        print("服务器%s连接失败！！！")
        print(e)
        sys.exit()

    # 清除日志命令
    command = "echo ""> /data/logs/tomcat-8087/primary-app-api_debug.log"
    # 执行命令
    client.exec_command(command)
    # 关闭日志
    client.close()
