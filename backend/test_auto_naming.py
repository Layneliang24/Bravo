# 测试自动命名校验的文件
# pylint: disable=invalid-name


class badClassName:  # 违反类名规范
    def BadMethodName(self):  # 违反方法名规范
        MyVariable = "test"  # 违反变量名规范
        return MyVariable


def BAD_FUNCTION_NAME():  # 违反函数名规范
    AnotherBadVariable = 42  # 违反变量名规范
    return AnotherBadVariable


# 违反常量名规范
bad_constant_name = "should be uppercase"


def test_function(BadParamName):  # 违反参数名规范
    return BadParamName
