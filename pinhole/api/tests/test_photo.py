from __future__ import absolute_import
import json
from os import path
from urllib import urlencode
from collections import OrderedDict
from datetime import datetime, timedelta
from flask.ext.restful import marshal
from nose.tools import assert_equal, assert_in, assert_is_instance, assert_true
from webtest import TestApp
from webtest.forms import Upload
from pinhole.common import models
from pinhole.common.app import db, app, application
from pinhole.common.s3 import S3Adapter
from pinhole.api.params import photo_fields
from .base import BaseTest

DOT = path.dirname(path.abspath(__file__))


class TestPhotoController(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.user = models.User("john", "john@example.com")
        self.user.set_password("doe")
        db.session.add(self.user)
        db.session.commit()

        self.user2 = models.User("john2", "john2@example.com")
        self.user2.set_password("doe")
        db.session.add(self.user2)
        db.session.commit()

        self.photo = models.Photo()
        self.photo.user = self.user
        self.photo.title = "Landscape"
        self.photo.description = """This is an awesome description"""
        self.photo.url = "s3://dev.pinhole.tty.cl/mesh"
        self.photo.rating = 5.0
        db.session.add(self.photo)
        db.session.commit()
        self.photo_id = self.photo.id

    def test_get(self):
        self.login("john", "doe")
        res = self.app.get("/api/v1/photos/%d" % self.photo_id)

        assert "id" in res.json
        assert "title" in res.json
        assert res.json["id"] == self.photo_id
        assert res.json["title"] == "Landscape"

    def test_get_someone_else_photo(self):
        self.login("john2", "doe")
        res = self.app.get("/api/v1/photos/%d" % self.photo_id,
                           expect_errors=True)

        assert_equal(res.status_int, 404)

    def test_post_photo(self):
        yield self.check_post_photo
        yield self.check_post_photo, "vacations,party, summer"
        yield self.check_post_photo, "vacations"
        yield self.check_post_photo, ", ".join(["t%d" % i for i in range(100)])

    def check_post_photo(self, tags=None):
        self.login("john2", "doe")

        with open(path.join(DOT, "fixtures",
                            "4843655940_d8dd79d602_o.jpg")) as f:
            picture = Upload("4843655940_d8dd79d602_o.jpg", f.read())

        params = OrderedDict([("title", "my title"),
                              ("description", "my description"),
                              ("rating", "1.3"),
                              ("picture", picture)])
        if tags:
            params["tags"] = tags

        res = self.app.post("/api/v1/photos", params)

        assert_equal(res.status_int, 200)
        assert_in("id", res.json)
        assert_equal(res.json["title"], "my title")
        assert_equal(res.json["description"], "my description")
        assert_equal(res.json["rating"], 1.3)

        if tags:
            splited_tags = [x.strip() for x in tags.split(",")]
            assert_in("tags", res.json)
            assert_is_instance(res.json["tags"], list)
            assert_equal(len(res.json["tags"]), len(splited_tags),
                         res.json["tags"])
            assert_equal(sorted([x["name"] for x in res.json["tags"]]),
                         sorted(splited_tags))

        photo = models.Photo.get_by(id=int(res.json["id"]))
        assert_true(photo.s3_path is not None,
                    "s3_path is None: %s" % photo.s3_path)
        assert_true(photo.s3_path.endswith("4843655940_d8dd79d602_o.jpg"))
        # exif checks
        assert_equal(photo.DateTime, datetime(2010, 7, 25, 20, 26, 50))
        assert_equal(photo.DateTimeOriginal, datetime(2010, 7, 5, 18, 55, 35))
        assert_equal(photo.DateTimeDigitized, datetime(2010, 7, 5, 18, 55, 35))
        assert_equal(photo.Make, u"Canon")
        assert_equal(photo.Model, u"Canon EOS 40D")
        assert_equal(photo.Software, u'QuickTime 7.6.6')
        assert_equal(photo.HostComputer, u'Mac OS X 10.6.4')
        assert_equal(photo.Orientation, 1)


class TestPhotoGetWithFilters(object):
    @classmethod
    def setUpClass(cls):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        cls.s3_keys = bucket.get_all_keys()

        db.create_all()
        cls.app = TestApp(application())

        cls.user = models.User("john", "john@example.com")
        cls.user.set_password("doe")
        db.session.add(cls.user)
        db.session.commit()

        cls.roll = models.Roll()
        cls.roll.timestamp = datetime.now()
        db.session.add(cls.roll)
        db.session.commit()

        cls.photos = []
        start = datetime.now() - timedelta(days=1)
        for i in range(20):
            photo = models.Photo()
            photo.title = "Photo%.2d" % i
            photo.description = "Photo desc"

            photo.width = 10 * (i + 1)
            photo.height = 10 * (i + 1)

            # exif
            photo.Make = "Make%s" % i
            photo.Model = "Model%s" % i
            photo.Software = "Software%s" % i
            photo.HostComputer = "HostComputer%s" % i
            photo.Orientation = 1
            photo.DateTime = start + timedelta(seconds=3600 * i)
            photo.DateTimeDigitized = start + timedelta(seconds=3600 * i + 1)
            photo.DateTimeOriginal = start + timedelta(seconds=3600 * i + 2)
            photo.user = cls.user
            photo.roll = cls.roll

            db.session.add(photo)
            db.session.commit()
            photo.add_tag("tag%s" % i)
            cls.photos.append(photo)

        cls.login("john", "doe")

    @classmethod
    def login(cls, username, password):
        res = cls.app.get("/")
        assert res.headers["Location"].endswith("/account/login?next=%2F"), \
            res.headers["Location"]

        res = res.follow()

        frm = res.forms["frm_login"]
        frm["username"] = username
        frm["password"] = password
        res = frm.submit()

        res = res.follow()
        res.mustcontain("Logged in")

    @classmethod
    def tearDownClass(cls):
        s3conn = S3Adapter()
        bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
        assert bucket is not None
        for key in bucket.get_all_keys():
            if key not in cls.s3_keys:
                key.delete()
        db.drop_all()

    def test_filters(self):
        yield self.check_filters, {"Make": "Make2"}, \
            json.loads(json.dumps(marshal([self.photos[2]],
                                          photo_fields)))
        data = marshal([p for p in self.photos if p.id > 10], photo_fields)
        yield self.check_filters, {"id__gt": 10}, \
            json.loads(json.dumps(data))
        yield self.check_filters, {"id__lt": 0}, []

    def check_filters(self, filters, expected):
        res = self.app.get("/api/v1/photos?%s" % urlencode(filters))
        assert_equal(set([x["id"] for x in res.json]),
                     set([x["id"] for x in expected]))
        assert_equal(len(res.json), len(expected))

        la = sorted(res.json, key=lambda x: x["id"])
        lb = sorted(expected, key=lambda x: x["id"])

        for i in range(len(la)):
            a = la[i]
            b = lb[i]
            self.compare_photo(a, b)

    def compare_photo(self, a, b):
        for key in a:
            assert_in(key, b)
            if not isinstance(a[key], dict) and not isinstance(a[key], list):
                assert_equal(a[key], b[key],
                             "a['%(key)s'] != b['%(key)s'] -> %(a)s != %(b)s"
                             % {"key": key, "a": a[key], "b": b[key]})
            elif isinstance(a[key], dict):
                self.compare_photo(a[key], b[key])
