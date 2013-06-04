from __future__ import absolute_import
from collections import OrderedDict
from nose.tools import assert_equal, assert_in, assert_is_instance
from pinhole.common import models
from pinhole.common.app import db
from .base import BaseTest


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
        self.login("john2", "doe")
        params = OrderedDict([("title", "my title"),
                              ("description", "my description"),
                              ("rating", "1.3")])
        res = self.app.post("/api/v1/photos", params)

        assert_equal(res.status_int, 200)
        assert_equal(res.json["title"], "my title")
        assert_equal(res.json["description"], "my description")
        assert_equal(res.json["rating"], 1.3)

    def test_post_photo_with_tags(self):
        self.login("john2", "doe")
        params = OrderedDict([("title", "my title"),
                              ("description", "my description"),
                              ("rating", "1.3"),
                              ("tags", "vacations,party, summer")])
        res = self.app.post("/api/v1/photos", params)

        assert_equal(res.status_int, 200)
        assert_equal(res.json["title"], "my title")
        assert_equal(res.json["description"], "my description")
        assert_equal(res.json["rating"], 1.3)
        assert_in("tags", res.json)
        assert_is_instance(res.json["tags"], list)
        assert_equal(len(res.json["tags"]), 3, res.json["tags"])
        assert_equal(sorted([x["name"] for x in res.json["tags"]]),
                     sorted(["vacations", "party", "summer"]))
