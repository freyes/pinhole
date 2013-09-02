from cookielib import CookieJar
from webtest import TestApp
from nose.tools import assert_true
from pinhole.common.app import db, application, app
from pinhole.common.s3 import S3Adapter


class BaseTest(object):
    def setUp(self):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        self.s3_keys = bucket.get_all_keys()

        db.create_all()
        self.app = TestApp(application(), cookiejar=CookieJar())

    def tearDown(self):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        for key in bucket.get_all_keys():
            if key not in self.s3_keys:
                key.delete()
        db.drop_all()

    def login(self, username, password):
        res = self.app.post("/api/v1/authenticated",
                            params={"username": username,
                                    "password": password})
        assert_true(res.json["authenticated"], "I couldn't authenticate")
