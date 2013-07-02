from __future__ import absolute_import
from nose.tools import assert_equal, assert_in
from pinhole.common.tests.base import BaseTest
from pinhole.common.models import User
from pinhole.common.app import db
from .base import BaseTestSelenium


class TestLogin(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.u = User("super", "duper@example.com")
        self.u.set_password("aqwsed7890")
        db.session.add(self.u)
        db.session.commit()

    def test_ok(self):
        res = self.app.get("/")
        assert res.headers["Location"].endswith("/account/login?next=%2F"), \
            res.headers["Location"]

        assert_equal(res.status_int, 302)
        res = res.follow()

        frm = res.forms["frm_login"]
        frm["username"] = "super"
        frm["password"] = "aqwsed7890"
        res = frm.submit()

        assert_equal(res.status_int, 302)
        res = res.follow()
        res.mustcontain("Logged in")

    def test_not_ok(self):
        res = self.app.get("/")
        assert res.headers["Location"].endswith("/account/login?next=%2F"), \
            res.headers["Location"]

        assert_equal(res.status_int, 302)
        res = res.follow()

        frm = res.forms["frm_login"]
        frm["username"] = "super"
        frm["password"] = "gre"
        res = frm.submit()
        assert_equal(res.status_int, 200)

        assert "Logged in" not in res.body


class TestSignup(BaseTestSelenium):
    def test_ok(self):
        X_REGISTER_NOW = "//a[text()='Register now!']"
        self.app.get("/")
        self.app.wait_element_by(xpath=X_REGISTER_NOW)

        e = self.app.driver.find_element_by_xpath(X_REGISTER_NOW)
        e.click()
        self.app.wait_element_by(xpath="//legend[text()='Sign up']")

        self.app.fill_form("frm_signup", {"username": "steven",
                                          "email": "steven@example.com",
                                          "password_1": "Ooshash2Oo",
                                          "password_2": "Ooshash2Oo"})

        e = self.app.driver.find_element_by_xpath("//input[@name='tos']")
        e.click()

        e = self.app.driver.find_element_by_xpath("//input[@type='submit']")
        e.click()

        assert_in("Your account was successfully created",
                  self.app.driver.page_source)
