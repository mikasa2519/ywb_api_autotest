import jsonpath


def assert_result(expect_result, actual_result, status_code):
    all_flag = 0
    print("预期结果: %s" % expect_result)
    print("实际状态吗：%s" % status_code)
    print("实际结果: %s" % actual_result)
    for expect in expect_result:
        for key, value in expect.items():
            if key == "equals":
                flag = equals_assert(value=value, actual_result=actual_result, status_code=status_code)
                all_flag = all_flag + flag
            elif key == "contains":
                flag = contains_assert(value=value, actual_result=actual_result)
                all_flag = all_flag + flag
            else:
                print("不支持此类断言")
    return all_flag


# 相等断言
def equals_assert(value, actual_result, status_code):
    flag = 0
    for equals_key, equals_value in value.items():
        if equals_key == "status_code":
            if equals_value != status_code:
                print("断言失败：" + str(equals_key) + "不等于" + str(equals_value))
                flag = flag + 1
        else:
            value_list = jsonpath.jsonpath(actual_result, "$..%s" % equals_key)
            if value_list:
                if equals_value not in value_list:
                    print("断言失败：" + str(equals_key) + "不等于" + str(equals_value))
                    flag = flag + 1
            else:
                print("断言失败：" + str(equals_key) + "不在返回值中")
                flag = flag + 1
    return flag


# 包含断言
def contains_assert(value, actual_result):
    flag = 0
    if str(value) not in str(actual_result):
        print("contains断言失败：返回的结果中没有" + str(value))
        flag = flag + 1

    return flag
