import pytest

from commons.requests_util import RequestUtil
from commons.yaml_util import read_yaml
from hot_loads.debug_talk import DebugTalk


class TestLogin:

    @pytest.mark.parametrize("caseinfo", read_yaml("testcases/test_login/test_get_image_code.yaml"))
    def test_get_image_code(self, caseinfo):
        RequestUtil(DebugTalk()).standard_yaml_testcase(caseinfo)

    @pytest.mark.parametrize("caseinfo", read_yaml("testcases/test_login/test_check_image_code.yaml"))
    def test_check_image_code(self, caseinfo):
        RequestUtil(DebugTalk()).standard_yaml_testcase(caseinfo)

    @pytest.mark.parametrize("caseinfo", read_yaml("testcases/test_login/test_get_sms_code.yaml"))
    def test_get_sms_code(self, caseinfo):
        RequestUtil(DebugTalk()).standard_yaml_testcase(caseinfo)

    @pytest.mark.parametrize("caseinfo", read_yaml("testcases/test_login/test_login.yaml"))
    def test_login(self, caseinfo):
        RequestUtil(DebugTalk()).standard_yaml_testcase(caseinfo)
