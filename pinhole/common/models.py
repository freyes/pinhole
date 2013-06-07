from __future__ import absolute_import
import uuid
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from boto.s3.key import Key
from .auth import check_password, make_password
from .s3 import S3Adapter

db = SQLAlchemy()


class BaseModel(object):
    @classmethod
    def get_by(cls, **kwargs):
        rows = cls.query.filter_by(**kwargs)
        if rows.count() == 1:
            return rows.first()
        elif rows.count() == 0:
            return None
        else:
            raise ValueError("More than 1 rows matched")


class User(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))
    email = db.Column(db.String(120), unique=True)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    # required by flask-login
    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True
    # end required by flask-login

    @property
    def fullname(self):
        return u"%s %s" % (self.first_name or '',
                           self.last_name or '')

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.

        :param raw_password: the password that should be checked
                             against the saved one
        :type raw_password: str
        :returns: True if the password matches, False otherwise
        :rtype: bool
        """
        return check_password(raw_password, self.password)

    def set_password(self, raw_password, commit=False):
        """
        Transform the password with a hash function and the store it

        :param raw_password: the password to set
        :type raw_password: str
        :param commit: commit the session on True
        :type commit: bool
        """
        self.password = make_password(raw_password)
        db.session.add(self)
        if commit:
            db.session.commit()


class Tag(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("tags",
                                                      lazy="dynamic"))


tags = db.Table('tag_photo',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'),
                          nullable=False),
                db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'),
                          nullable=False)
                )


class Photo(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)
    public = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(2000))
    rating = db.Column(db.Float)

    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    type = db.Column(db.String(20))

    s3_path = db.Column(db.String(2048), unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("photos",
                                                      lazy="dynamic"))

    roll_id = db.Column(db.Integer, db.ForeignKey("roll.id"))
    roll = db.relationship("Roll", backref=db.backref("photos",
                                                      lazy="dynamic"))
    tags = db.relationship('Tag', secondary=tags,
                           backref=db.backref('photos', lazy='dynamic'))

    def __repr__(self):
        return "<Photo %d>" % (self.id, )

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(key)

    def add_tag(self, name):
        assert self.user is not None

        tag = Tag.query.filter_by(name=name,
                                  user_id=self.user.id)
        if tag.count() == 0:
            tag = Tag()
            tag.name = name
            tag.user = self.user
            db.session.add(tag)
            db.session.commit()

        ti = tags.insert(bind=db.engine)
        ti.values(photo_id=self.id, tag_id=tag.id).execute()

        db.session.commit()

    def set_contents_from(self, f):
        """
        Populate the object with all the information that can be extracted
        from a photo file (i.e. EXIF metadata, width, height, etc)

        :param f: photo content
        """

    @classmethod
    def from_file(cls, user, f):
        """
        Creates a :class:`pinhole.common.models.Photo` instance and populates
        the properties

        :param user: the owner of the photo, it can be a ``User`` instance or
                     a username
        :type user: :class:`pinhole.common.models.User` or str
        :param f: the file
        :type: :class:`werkzeug.datastructures.FileStorage`
        :returns: the photo instance populated
        :rtype: :class:`pinhole.common.models.Photo`
        """
        from .app import app
        if isinstance(user, basestring):
            user = User.get_by(username=user)

        assert user is not None

        photo = cls()
        photo.user = user

        # do we have to offload the upload process
        # to a celery task?
        s3conn = S3Adapter()
        bucket = s3conn.get_bucket(app.config["PHOTO_BUCKET"])
        k = Key(bucket)
        k.key = photo.gen_s3_key(f.stream.filename)
        k.set_contents_from_file(f.stream.stream)

        photo.s3_path = "s3://%s%s" % (bucket.name, k.key)
        db.session.add(photo)
        db.session.commit()

        return photo

    def gen_s3_key(self, fname):
        """
        Generate a unique S3 key where the photo will be uploaded

        :param fname: file name
        :type fname: str
        :rtype: str
        :returns: a S3 key (i.e. `foo/bar/myphoto.jpg`)
        """
        uid = uuid.uuid1()
        return "%s/%s/%s/%s_%s" % (self.user.username,
                                   datetime.now().strftime("%Y_%m_%d"),
                                   uid, uid,
                                   fname)


class Roll(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime)
