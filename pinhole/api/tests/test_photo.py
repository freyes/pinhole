from __future__ import absolute_import
from pinhole.common import models
from pinhole.common.app import db
from .base import BaseTest


class TestPhotoController(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.user = models.User("john", "john@example.com")
        self.user.password = "doe"
        db.session.add(self.user)
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
