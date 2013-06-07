from __future__ import absolute_import
from os import path
from collections import OrderedDict
from datetime import datetime
from nose.tools import assert_equal, assert_in, assert_is_instance, assert_true
from webtest.forms import Upload
from pinhole.common import models
from pinhole.common.app import db
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
