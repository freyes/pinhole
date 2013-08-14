from __future__ import absolute_import
from nose.tools import assert_equal
from ..utils import convert


class TestConvert(object):
    def test(self):
        l = [('CamelCase', 'camel_case'),
             ('CamelCamelCase', 'camel_camel_case'),
             ('Camel2Camel2Case', 'camel2_camel2_case'),
             ('getHTTPResponseCode', 'get_http_response_code'),
             ('get2HTTPResponseCode', 'get2_http_response_code'),
             ('HTTPResponseCode', 'http_response_code'),
             ('HTTPResponseCodeXYZ', 'http_response_code_xyz')]
        for a, b in l:
            yield self.check, a, b

    def check(self, value, expected):
        assert_equal(convert(value), expected)
