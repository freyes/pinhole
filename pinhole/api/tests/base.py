from webtest import TestApp
from pinhole.common.app import db, application, app
from pinhole.common.s3 import S3Adapter


class BaseTest(object):
    def setUp(self):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        self.s3_keys = bucket.get_all_keys()

        db.create_all()
        self.app = TestApp(application())

    def tearDown(self):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        for key in bucket.get_all_keys():
            if key not in self.s3_keys:
                key.delete()
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
