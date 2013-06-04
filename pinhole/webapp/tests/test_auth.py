from pinhole.common.tests.base import BaseTest
from pinhole.common.models import User
from pinhole.common.app import db


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

        res = res.follow()

        frm = res.forms["frm_login"]
        frm["username"] = "super"
        frm["password"] = "aqwsed7890"
        res = frm.submit()

        res = res.follow()
        res.mustcontain("Logged in")
