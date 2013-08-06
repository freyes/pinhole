from __future__ import absolute_import
import uuid
import warnings
import logging
from tempfile import TemporaryFile
from datetime import datetime
from urlparse import urlparse
from os import path
from PIL import Image, ExifTags
from boto.s3.key import Key
from .auth import check_password, make_password
from .s3 import S3Adapter
from .exif import exif_transform
from .extensions import db


exif_tags = ExifTags.TAGS
exif_tags[316] = "HostComputer"


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

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(key)

    @property
    def logger(self):
        if not hasattr(self, "_logger") or not self._logger:
            self._logger = logging.getLogger(self.__class__.__name__)

        return self._logger

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
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


class UploadedPhoto(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(2000))
    filename = db.Column(db.String(200))
    size = db.Column(db.Integer)
    key = db.Column(db.String(100))
    is_writeable = db.Column(db.Boolean)
    processed = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("uploaded_photos",
                                                      lazy="dynamic"))

    def __repr__(self):
        return "<UploadedPhoto:%s>" % self.id or "-"


class Photo(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    public = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(2000))
    rating = db.Column(db.Float)

    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    type = db.Column(db.String(20))

    s3_path = db.Column(db.String(2048), unique=True, nullable=True)

    # deleted ?
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # exif metadata
    Make = db.Column(db.String(40))
    Model = db.Column(db.String(40))
    Software = db.Column(db.String(40))
    HostComputer = db.Column(db.String(40))
    Orientation = db.Column(db.Integer)

    DateTime = db.Column(db.DateTime)
    DateTimeDigitized = db.Column(db.DateTime)
    DateTimeOriginal = db.Column(db.DateTime)

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("photos",
                                                      lazy="dynamic"))

    roll_id = db.Column(db.Integer, db.ForeignKey("roll.id"))
    roll = db.relationship("Roll", backref=db.backref("photos",
                                                      lazy="dynamic"))
    tags = db.relationship('Tag', secondary=tags,
                           backref=db.backref('photos', lazy='dynamic'))

    # non-model properties
    # key -> code
    # value -> width or height, it depends on the orientation
    sizes = {"square_75": 75,
             "square_150": 150,
             "thumbnail": 100,
             "small_240": 240,
             "small_320": 320,
             "medium_500": 500,
             "medium_640": 640,
             "medium_800": 800,
             "large_1024": 1024,
             "large_1600": 1600,
             "large_2048": 2048,
             "raw": None,
             }

    def __repr__(self):
        return "<Photo %d>" % (self.id, )

    @property
    def fname(self):
        parsed = urlparse(self.s3_path)
        return path.basename(parsed.path)

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
        photo.title = f.filename

        # do we have to offload the upload process
        # to a celery task?
        s3conn = S3Adapter()
        bucket = s3conn.get_bucket(app.config["PHOTO_BUCKET"])
        k = Key(bucket)
        k.key = photo.gen_s3_key(f.filename)
        k.set_contents_from_file(f.stream)

        photo.s3_path = "s3://%s/%s" % (bucket.name, k.key)

        # process exif tags
        f.stream.seek(0)
        photo.process_exif(f.stream)

        db.session.add(photo)
        db.session.commit()

        return photo

    def create_thumbnails(self, filename, stream, keep_aspect_ratio=True):
        """
        Create thumbnails for this photo

        :param filename: filename
        :type filename: str
        :param stream: image file
        :type stream: file-like object
        """

    def get_image(self, size="raw", fmt=None):
        """
        Get the image file in the given size

        :param size: image size requested
                     (see :attr:`pinhole.common.models.Photo.sizes`)
        :type size: str
        :param fmt: image format requested (jpeg, png, gif, etc)
        :type fmt: str
        :rtype: file-like object
        :returns: a file pointer to be read with the image transformed,
                  if the `fp` is closed, the file will be automatically deleted
        """
        if size not in self.sizes:
            raise ValueError("Size {} not supported".format(size))

        if fmt is not None:
            warnings.warn("File format is not implemented yet")

        parsed = urlparse(self.s3_path)

        s3conn = S3Adapter()
        bucket = s3conn.get_bucket(parsed.hostname)

        if size == "raw":
            key = bucket.get_key(parsed.path.lstrip("/"))
        else:
            # look for existing image
            image_s3_path = self.gen_s3_key(path.basename(parsed.path), size)
            key = bucket.get_key(image_s3_path)

        if key is not None:
            # we have the image!
            tmp_image = TemporaryFile(suffix=path.basename(parsed.path))
            key.get_contents_to_file(tmp_image)
            tmp_image.flush()
            tmp_image.seek(0)

            return tmp_image

        # the image doesn't exist, so let's create it
        key = bucket.get_key(parsed.path.lstrip("/"))
        assert key is not None

        tmp_image = TemporaryFile(suffix=path.basename(parsed.path))
        key.get_contents_to_file(tmp_image)
        tmp_image.flush()
        tmp_image.seek(0)

        img_obj = Image.open(tmp_image)
        s = self.sizes[size]
        img_obj.thumbnail((s, s), Image.ANTIALIAS)

        #upload the image
        new_image = TemporaryFile(suffix=path.basename(parsed.path))
        img_obj.save(new_image, format="JPEG")
        new_image.seek(0)

        key = Key(bucket)
        key.key = image_s3_path
        key.set_contents_from_file(new_image)

        new_image.seek(0)
        return new_image

    def process_exif(self, stream):
        """
        Process EXIF tags and save them in the object properties

        :param stream: file-like object
        :type stream: file
        :rtype: dict
        :returns: a dictionary with all the exif tags found
        """
        ret = {}
        i = Image.open(stream)
        if not i:
            msg = "Stream {} couldn't be opened as image".format(stream)
            raise ValueError(msg)

        info = i._getexif()

        if not info:
            self.logger.info("Exif info not found in {}".format(i))
            return ret

        for tag, value in info.items():
            decoded = exif_tags.get(tag, tag)
            if isinstance(decoded, basestring) and hasattr(self, decoded):
                if decoded in exif_transform:
                    value = exif_transform[decoded](value)
                setattr(self, decoded, value)
            ret[decoded] = value
        return ret

    def gen_s3_key(self, fname, prefix=""):
        """
        Generate a unique S3 key where the photo will be uploaded

        :param fname: file name
        :type fname: str
        :param prefix: prefix for `fname`
        :type prefix: str
        :rtype: str
        :returns: a S3 key (i.e. `foo/bar/myphoto.jpg`)
        """
        uid = uuid.uuid1()
        if prefix:
            fname = "%s_%s" % (prefix, fname)

        return "%s/%s/%s/%s_%s" % (self.user.username,
                                   datetime.now().strftime("%Y_%m_%d"),
                                   uid, uid,
                                   fname)


class Roll(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime)
