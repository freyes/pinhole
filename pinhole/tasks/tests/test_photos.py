from __future__ import absolute_import
import os
import boto
from os import path
from nose.tools import (assert_equal, assert_in, assert_is_instance,
                        assert_is_not)
from boto.s3.key import Key

from pinhole.common import models
from pinhole.common.app import db, app
from pinhole.common import s3
from .base import BaseTest
from ..photos import ProcessUploadedPhoto

DOT = path.dirname(path.abspath(__file__))
PHOTO_PATH = path.join(DOT, "../..",
                       "api/tests/fixtures/4843655940_d8dd79d602_o.jpg")


class TestProcessUploadedPhoto(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        # upload a photo
        self.u = models.User("super", "duper@example.com")
        self.u.set_password("aqwsed7890")
        db.session.add(self.u)
        db.session.commit()

        self.up = models.UploadedPhoto()
        self.up.url = "http://example.com/meh.jpeg"
        self.up.filename = "meh.jpeg"
        self.up.size = 123
        self.up.key = "grrr_meh.jpeg"
        self.up.user_id = self.u.id

        db.session.add(self.up)
        db.session.commit()
        s3conn = s3.S3Adapter()
        bucket = s3conn.get_bucket(app.config["INCOMING_PHOTO_BUCKET"])
        k = Key(bucket)
        k.key = self.up.key
        with open(PHOTO_PATH, "rb") as f:
            k.set_contents_from_file(f)

        self.key = k

    def tearDown(self):
        BaseTest.tearDown(self)
        try:
            self.key.delete()
        except:
            pass

    def test_already_processed_photo(self):
        self.up.processed = True
        db.session.add(self.up)
        db.session.commit()

        t = ProcessUploadedPhoto().apply(args=(self.up.id, ))

        assert_equal(t.ready(), True)
        r = t.result
        assert_is_instance(r, dict)
        assert_in("code", r)
        assert_equal(r["code"], 10)
        assert_in("message", r)
        assert_equal(r["message"], "The %s was already processed" % self.up)

    def test_ok(self):
        t = ProcessUploadedPhoto().apply(args=(self.up.id, ))
        assert_equal(t.ready(), True)
        assert_equal(t.state, "SUCCESS", t.traceback)
        r = t.result
        assert_is_instance(r, dict)
        assert_in("photo_id", r)
        photo = models.Photo.get_by(id=r["photo_id"])
        assert_is_not(photo, None)
        assert_equal(photo.user, self.u)
