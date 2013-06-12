from __future__ import absolute_import
from datetime import datetime
from nose.tools import assert_equal, assert_raises
from ..exif import transform_datetime


def test_transform_datetime():

    assert_equal(transform_datetime("2001:12:31 19:45:59"),
                 datetime(2001, 12, 31, 19, 45, 59))
    assert_raises(ValueError, transform_datetime, "2001:12:31 9",
                  fail_silently=False)
    assert_equal(transform_datetime("2001:12:31 9", True), None)
