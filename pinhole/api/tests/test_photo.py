from __future__ import absolute_import
from pinhole.common import models
from pinhole.common.app import db
from .base import BaseTest


class TestPhotoController(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.user = models.User("john", "john@example.com")
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

    def test_get(self):
        s = self.app.get("/api/v1/photos/%d" % self.photo.id)
        import ipdb; ipdb.set_trace()
