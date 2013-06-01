from __future__ import absolute_import

from pinhole.common.app import db
from pinhole.common import models
from .base import BaseTest


class TestModels(BaseTest):
    def test_basic_relationships(self):
        #create user
        user = models.User("john", "john@example.com")
        db.session.add(user)

        # a photo
        photo = models.Photo()
        photo.rating = 1.3
        photo.title = "title"
        photo.user = user
        db.session.add(photo)

        db.session.commit()

        # a few tags
        for i in range(1, 11):
            photo.add_tag("tag%2d" % i)

        db.session.commit()

        photos = models.Photo.query.filter_by(title="title")

        assert photos.count() == 1
        photo = photos.first()

        assert photo.title == "title"
        assert photo.rating == 1.3
        assert photo.user_id == user.id
        assert photo.user == user
        assert len(photo.tags) == 10

        t = models.Tag.query.filter_by(name="tag10")
        assert t.count() == 1
        t = t.first()
        assert t.photos.count() == 1


class TestPhoto(object):
    def setUp(self):
        db.create_all()
        #create user
        self.user = models.User("john", "john@example.com")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    def test_repr(self):
        # a photo
        photo = models.Photo()
        photo.rating = 1.3
        photo.title = "title"
        photo.user = self.user
        db.session.add(photo)

        db.session.commit()

        assert repr(photo) == "<Photo %d>" % photo.id

    def test_add_tag(self):
        # a photo
        photo = models.Photo()
        photo.rating = 1.3
        photo.title = "title"
        photo.user = self.user
        db.session.add(photo)

        db.session.commit()

        photo.add_tag("meh")
        photo.add_tag("supr")
        assert len(photo.tags) == 2

        assert sorted([x.name for x in photo.tags]) == ["meh", "supr"]

        for t in photo.tags:
            assert t.user == self.user
