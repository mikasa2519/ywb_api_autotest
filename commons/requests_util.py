import json
import re

import jsonpath
import requests

from commons.assert_util import assert_result
from commons.yaml_util import write_yaml
from hot_loads.debug_talk import DebugTalk


class RequestUtil:
    # 初始化session对象
    sess = requests.session()

    # 初始化热加载对象
    def __init__(self, obj):
        self.obj = obj

    # 用例格式规范校验
    def standard_yaml_testcase(self, caseinfo):
        # 校验一级关键字
        caseinfo_keys = caseinfo.keys()
        if "name" and "request" and "validata" in caseinfo_keys:
            request_keys = caseinfo["request"].keys()
            if "url" and "method" in request_keys:
                # 获取url和method
                url = caseinfo["request"].pop("url")
                method = caseinfo["request"].pop("method")
                # 发送请求
                res = self.send_requests(url=url, method=method, **caseinfo["request"])
                # 获取文本格式的返回值
                text_result = res.text
                status_code = res.status_code

                # 获取json格式返回值
                try:
                    json_result = res.json()
                except json.JSONDecodeError:
                    json_result = ""

                # 从返回值中提取中间变量
                if "extract_from_res" in caseinfo.keys():

                    # 遍历字典需要使用字典对象item()，遍历出来的是key和value的值
                    for key, value in caseinfo["extract_from_res"].items():
                        # 正则提取中间关联变量
                        if "(.*?)" in value or "(.+?)" in value:

                            # 通过re.search(“表达式”，要提取的源文本)来进行正则提取
                            regular_value = re.search(value, text_result)
                            if regular_value:
                                data = {key: regular_value.group(1)}
                                write_yaml("extract.yaml", data)
                            else:
                                print("extract中间变量提取失败，请检查正则提取表达式")

                        # jsonpath提取中间关联变量,仅仅支持json格式数据
                        elif "$.." in value:
                            if json_result != "":
                                js_value = jsonpath.jsonpath(json_result, value)
                                print(js_value)
                                if js_value:
                                    data = {key: js_value[0]}
                                    write_yaml("extract.yaml", data)
                                else:
                                    print("extract中间变量提取失败，请检查jsonpath提取式")
                            else:
                                print("接口返回数据不是json格式")
                        else:
                            print("仅支持使用正则或jsonpath提取关联变量")
                # 从日志中提取中间变量
                elif "extract_from_log" in caseinfo.keys():
                    # 校验提取条件是否完整
                    extract_from_log_keys = caseinfo["extract_from_log"].keys()
                    if "command" and "regular_keywords" and "extract_key" and "server_info" in extract_from_log_keys:
                        for key, value in caseinfo["extract_from_log"].items():
                            if "${" and "}" in value:
                                caseinfo["extract_from_log"][key] = self.replace_get_value(data=value)
                    else:
                        print("提取信息不完整，请检查后重新填写")
                    # 得到查询日志详情信息
                    get_log_terms = caseinfo["extract_from_log"]
                    # 获取参数
                    command = get_log_terms["command"]
                    regular_keywords = get_log_terms["regular_keywords"]
                    extract_key = get_log_terms["extract_key"]
                    server_info = get_log_terms["server_info"]
                    # 调用函数写入中间变量
                    DebugTalk().get_data_from_log(command=command, regular_keywords=regular_keywords,
                                                  extract_key=extract_key, **server_info)

                # 断言
                expect_result = caseinfo["validata"]
                actual_result = json_result
                all_flag = assert_result(expect_result=expect_result,
                                         actual_result=actual_result,
                                         status_code=status_code)
                assert all_flag == 0
            else:
                print("用例必须包含二级关键字，url，method")
        else:
            print("用例必须包含一级关键字，name，request，validata")

    # 参数替换
    def replace_get_value(self, data):
        """
        封装替换取得的中间变量的方法，将standard_yaml_testcases方法中获取的中间变量，替换到需要用到的地方(url，param，data，json)
        注意1：使用中间变量的地方可能的是(url, params, data, json, headers)
        注意2：各种数据类型的切换：(int,float,string,list,dict)
        此方法还可以对用例yaml文件中的方法进行调用
        :param type: 转换后的数据类型
        :param data:需要转换的数据
        :return:转换后的数据
        """
        if data:
            data_type = type(data)
            # 如果需要替换的数据是列表或者字典，需要对其进行序列化转换成字符串
            if isinstance(data, list) or isinstance(data, dict):
                str_data = json.dumps(data)
            else:
                str_data = str(data)
            # 转换
            for a in range(1, str_data.count("${") + 1):
                if "${" and "}" in str_data:
                    start_index = str_data.index("${")
                    end_index = str_data.index("}", start_index)
                    old_value = str_data[start_index:end_index + 1]
                    # 获取方法名
                    function_name = old_value[2:old_value.index("(")]
                    # 获取参数
                    args_value = old_value[old_value.index("(") + 1:old_value.index(")")]
                    # 如果有参数
                    if args_value != "":
                        # 多个参数通过","进行分割
                        args_value = args_value.split(",")
                        # 反射：通过getattr进行方法的调用
                        new_value = getattr(self.obj, function_name)(*args_value)
                    else:
                        new_value = getattr(self.obj, function_name)()
                    str_data = str_data.replace(old_value, str(new_value))
            # 将数据的数据类型进行还原
            if str_data[0] == "{" and str_data[-1] == "}":
                data = json.loads(json.dumps(eval(str_data)))
            else:
                if isinstance(data, list) or isinstance(data, dict):
                    data = json.loads(str_data)
                else:
                    data = data_type(str_data)
            return data

    # 统一请求接口
    def send_requests(self, method, url, **kwargs):
        """
        发送请求
        :param method:方法
        :param url: 地址
        :param kwargs: 其他参数
        :return:请求结果
        """
        # 统一小写
        method = str(method).lower()

        # url通过${方法}，${变量}取值
        url = self.replace_get_value(data=url)
        # 剩余参数通过${方法}，${变量}取值
        for key, value in kwargs.items():
            if key in ["headers", "params", "datas", "json"]:
                kwargs[key] = self.replace_get_value(data=value)
            # 文件上传场景
            elif key == "files":
                for file_key, file_value in value.items():
                    value[file_key] = open(file_value, "rb")

        res = RequestUtil.sess.request(url=url, method=method, **kwargs)
        text_result = res.text
        print(text_result)
        return res
