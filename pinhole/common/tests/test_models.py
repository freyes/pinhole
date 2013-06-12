from __future__ import absolute_import
from nose.tools import (assert_is, assert_is_not, assert_raises, assert_equal,
                        assert_true, assert_false)
from .base import BaseTest
from ..models import User


class TestUser(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        u = User("foob4r", "foobar@bar.com")
        u.first_name = "Foo"
        u.last_name = "Bar"
        u.active = True
        u.save()

        u = User("foob4r2", "foobar2@bar.com")
        u.active = True
        u.save()

    def test_get_by_none(self):
        assert_is(User.get_by(username="me"), None)

    def test_get_by_one(self):
        assert_is_not(User.get_by(username="foob4r"), None)

    def test_get_by_value_error(self):
        assert_raises(ValueError, User.get_by, active=True)

    def test_repr(self):
        u = User.get_by(username="foob4r")
        assert_equal(repr(u), u'<User %r>' % u.username)

    def test_fullname(self):
        u = User.get_by(username="foob4r")
        assert_equal(u.fullname, u'Foo Bar')

    def test_password(self):
        u = User.get_by(username="foob4r")
        u.set_password("qazwsxedc", commit=True)

        assert_true(u.check_password("qazwsxedc"))
        assert_false(u.check_password("rmors"))
