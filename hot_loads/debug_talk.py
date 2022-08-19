import os
import random
import yaml
import time
import re
import sys
import paramiko
import base64
from Crypto.Cipher import AES
from commons.yaml_util import read_yaml, write_yaml


class DebugTalk:
    """
    热加载类，下方为编写用例过程中使用到的方法
    """

    # 获取时间戳
    def get_timestamp(self):
        timestamp = time.time()
        return str(int(timestamp))

    # 获取随机数
    def get_random(self, min, max):
        return random.randint(int(min), int(max))

    # 读取extract.yaml文件
    def read_extract_yaml(self, key):
        with open(os.getcwd() + "/extract.yaml", mode="r", encoding="utf-8") as f:
            result = yaml.load(stream=f, Loader=yaml.FullLoader)
            if result is not None:
                try:
                    return result[key]
                except KeyError:
                    return ""
            else:
                return ""

    # 读取环境信息yaml文件
    def read_envinfo_yaml(self, env_name):
        """
        :param env_name: 环境名称
        :return: 环境信息
        """
        with open(os.getcwd() + "/envinfo/services_info.yaml", mode="r", encoding="utf-8") as f:
            result = yaml.load(stream=f, Loader=yaml.FullLoader)
            for envinfo in result:
                if envinfo["name"] == env_name:
                    return envinfo["info"]
            print("环境信息输入有误")

    # 获取url
    def get_url(self, key):
        result = read_yaml("url.yaml")
        url = result[key]
        return url

    # 获取消息头
    def get_headers(self):
        headers = read_yaml("headers.yaml")
        userToken = self.read_extract_yaml("userToken")
        headers["userToken"] = userToken
        return headers

    # 从日志中获取验证码
    def get_data_from_log(self, command, regular_keywords, extract_key, **kwargs):
        """
        登录时获取短信验证码
        :param extract_key: 需要提取的字段名称
        :param regular_keywords: 正则提取关键字
        :param command: 命令
        :param kwargs: 服务器信息：hostname，port，username，password
        :return:验证码
        """
        # 测试环境
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(compress=True, **kwargs)
        # 服务器连接失败异常处理
        try:
            client.connect(compress=True, **kwargs)
        except Exception as e:
            print("服务器%s连接失败！！！")
            print(e)
            sys.exit()

        # 获取日志
        stdin, stdout, stderr = client.exec_command(command)
        debug_log = stdout.read().decode("utf-8")
        start_index = regular_keywords.index("(")
        try:
            if regular_keywords[0:start_index] in debug_log:
                key_data = re.search(regular_keywords, debug_log).group(1)
                data = {extract_key: key_data}
                write_yaml("extract.yaml", data)
                return key_data
            else:
                print("未匹配到值")
        finally:
            client.close()

    # 手机号使用PKCS7进行填充用于后续加密
    def pkcs7padding(self, text):
        """
            明文使用PKCS7填充，padding：凑篇幅的文字
            DES+AES64加密
        """

        # 明文 text 也必须为16字节或者16字节的倍数的字节型数据
        need_size = 16

        # 获取明文的长度
        text_length = len(text)

        # 获取明文编码转换后的字符长度
        bytes_length = len(text.encode('utf-8'))

        # 判断明文长度与编码转换后的字符长度是否相等
        # 1、如相等，返回明文长度length； 2、如不相等，返回编码转换后的字符长度bytes_length
        padding_size = text_length if (bytes_length == text_length) else bytes_length

        # 获取需要填充的字节数：16-（明文数据长度 % 16）
        padding = need_size - padding_size % need_size

        # 使用 chr(十进制整数) 方法从ASCII码表中获取对应编号的字符，并乘以字节个数，以获取需要填充的数据
        padding_text = chr(padding) * padding

        # 返回使用PKCS7填充后的数据：明文+需要填充的数据，使明文长度为16的倍数
        return text + padding_text

    # 手机号加密
    def AES_Encryption(self, secret_key=None, text=None):
        """ AES加密 ,python运行处理的是 unicode码，因此，在做编码转换时，通常需要以unicode作为中间编码 """

        # 秘钥 secret_key 必须为16字节或者16字节的倍数的字节型数据【项目中一般都是16字节】
        if (secret_key is None) or len(secret_key) == 0:
            secret_key = "1234567812345678"

        # 明文 text 也必须为16字节或者16字节的倍数的字节型数据，所以我们需要调用PKCS7填充明文的方法
        text = self.pkcs7padding(text)

        # 1、创建一个aes对象，AES.MODE_ECB 表示模式是ECB模式
        aes = AES.new(secret_key.encode("utf-8"), AES.MODE_ECB)

        # 2、对明文进行编码加密
        en_text = aes.encrypt(text.encode('utf-8'))

        # 3、通过base64编码重新进行一次编码
        result = str(base64.b64encode(en_text), encoding='utf-8')

        return result

    # 手机号解密
    def AES_Decrypt(self, secret_key=None, ciphertext=None):
        """AES解密，ciphertext：密文"""

        # 秘钥 secret_key 必须为16字节或者16字节的倍数的字节型数据【项目中一般都是16字节】
        if (secret_key is None) or len(secret_key) == 0:
            secret_key = "1234567812345678"

        # 1、创建一个aes对象，AES.MODE_ECB 表示模式是ECB模式
        aes = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)

        # 2、解密规则与加密规则有所不同，密文长度需要是3的倍数
        if len(ciphertext) % 3 == 1:
            ciphertext += "=="  # 如果余数为1，则填充两个等号==，长度凑3
        elif len(ciphertext) % 3 == 2:
            ciphertext += "="  # 如果余数为2，则填充一个等号=，长度凑3

        # 3、将密文先进行base64反编译
        content = base64.b64decode(ciphertext)

        # 4、讲反编译后的密文通过AES解密
        text = aes.decrypt(content).decode('utf-8')

        return text


if __name__ == '__main__':
    a = DebugTalk().AES_Encryption(secret_key="Kp514OoWCfbGw98m", text="18326127537")
    print(a)
