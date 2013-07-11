from __future__ import absolute_import
from os import path
from PIL import Image
from werkzeug.datastructures import FileStorage
from nose.tools import (assert_is, assert_is_not, assert_raises, assert_equal,
                        assert_true, assert_false)
from .base import BaseTest
from ..models import User, Photo
from ..s3 import S3Adapter
from ..app import app


PHOTO_FILE = path.join(path.dirname(path.abspath(__file__)),
                       "../../api/tests/fixtures/4843655940_d8dd79d602_o.jpg")


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


class TestPhoto(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        self.s3_keys = bucket.get_all_keys()

        u = User("foob4r", "foobar@bar.com")
        u.first_name = "Foo"
        u.last_name = "Bar"
        u.active = True
        u.save()

        assert path.isfile(PHOTO_FILE)

        with open(PHOTO_FILE, "rb") as f:
            fs = FileStorage(f, path.basename(PHOTO_FILE))
            p = Photo.from_file(u, fs)

        p.title = path.basename(PHOTO_FILE)
        p.description = "description"
        self.photo = p
        self.photo.save()

    def tearDown(self):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        for key in bucket.get_all_keys():
            if key not in self.s3_keys:
                key.delete()

        BaseTest.tearDown(self)

    def test_get_image(self):
        for size in Photo.sizes:
            yield self.check_get_image, size

    def check_get_image(self, size):
        pio = self.photo.get_image(size)
        image = Image.open(pio)
        if size != "raw":
            assert_equal(image.size[0], Photo.sizes[size])
