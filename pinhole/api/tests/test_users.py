from __future__ import absolute_import
from collections import OrderedDict
from nose.tools import assert_equal, assert_in, assert_is_instance
from pinhole.common import models
from pinhole.common.app import db
from .base import BaseTest


class TestRegister(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.user = models.User("john", "john@example.com")
        self.user.set_password("doe")
        db.session.add(self.user)
        db.session.commit()

    def test_ok(self):
        params = OrderedDict([("username", "foobar"),
                              ("email", "foobar@example.com"),
                              ("password", "12345678")])

        res = self.app.post("/api/v1/users", params)
        assert_equal(res.status_int, 200)

        assert_is_instance(res.json, dict)
        assert_in("user", res.json)
        assert_is_instance(res.json["user"], dict)
        user = res.json["user"]
        assert_equal(user["username"], "foobar")
        assert_equal(user["email"], "foobar@example.com")

    def test_already_used_username(self):
        params = OrderedDict([("username", "john"),
                              ("email", "foobar@example.com"),
                              ("password", "12345678")])

        res = self.app.post("/api/v1/users", params, expect_errors=True)
        assert_equal(res.status_int, 400)

        assert_is_instance(res.json, dict)
        assert_in("message", res.json)
        assert_equal(res.json["message"], "Username/email already in use")

    def test_already_used_email(self):
        params = OrderedDict([("username", "foobar"),
                              ("email", "john@example.com"),
                              ("password", "12345678")])

        res = self.app.post("/api/v1/users", params, expect_errors=True)
        assert_equal(res.status_int, 400)

        assert_is_instance(res.json, dict)
        assert_in("message", res.json)
        assert_equal(res.json["message"], "Username/email already in use")

    def test_check_username_used(self):
        params = OrderedDict([("username", "john")])
        res = self.app.patch("/api/v1/users", params)
        assert_equal(res.body, '"false"\n')

    def test_check_username_is_available(self):
        params = OrderedDict([("username", "asdf")])
        res = self.app.patch("/api/v1/users", params)
        assert_equal(res.body, '"true"\n')

    def test_check_email_used(self):
        params = OrderedDict([("email", "john@example.com")])
        res = self.app.patch("/api/v1/users", params)
        assert_equal(res.body, '"false"\n')

    def test_check_email_is_available(self):
        params = OrderedDict([("email", "john@example.cl")])
        res = self.app.patch("/api/v1/users", params)
        assert_equal(res.body, '"true"\n')

    def test_login(self):
        params = OrderedDict([("username", "john"),
                              ("password", "doe")])
        res = self.app.post("/api/v1/authenticated", params)

        assert_is_instance(res.json, dict)
        assert_equal(res.json["authenticated"], True)
        assert_is_instance(res.json["user"], dict)
        assert_equal(res.json["user"]["username"], "john")

    def test_login_invalid_creds(self):
        params = OrderedDict([("username", "joasfdhn"),
                              ("password", "doe")])
        res = self.app.post("/api/v1/authenticated", params,
                            expect_errors=True)

        assert_equal(res.status_int, 404)
        assert_is_instance(res.json, dict)
        assert_equal(res.json["message"],
                     "Wrong Username and password combination.")
