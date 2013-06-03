from webtest import TestApp
from pinhole.common.app import db, application


class BaseTest(object):
    def setUp(self):
        db.create_all()
        self.app = TestApp(application())

    def tearDown(self):
        db.drop_all()

    def login(self, username, password):
        res = self.app.get("/")
        assert res.headers["Location"].endswith("/account/login?next=%2F"), \
            res.headers["Location"]

        res = res.follow()

        frm = res.forms["frm_login"]
        frm["username"] = username
        frm["password"] = password
        res = frm.submit()

        res = res.follow()
        res.mustcontain("Logged in")
