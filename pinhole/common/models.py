from __future__ import absolute_import
import warnings
import logging
from tempfile import TemporaryFile
from datetime import datetime
from urlparse import urlparse
from os import path
from PIL import Image, ExifTags
from boto.s3.key import Key
from pinhole.exception import PinholeFileNotFound
from .auth import check_password, make_password
from . import s3
from .exif import exif_transform
from .extensions import db
from .utils import convert
from .dbtypes import RationalType, DateTime


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

    def is_anonymous(self):
        return False
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
    url = db.Column(db.Text(2048))
    filename = db.Column(db.String(200))
    size = db.Column(db.Integer)
    key = db.Column(db.String(100))
    is_writeable = db.Column(db.Boolean)
    processed = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(DateTime, default=datetime.now)

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("uploaded_photos",
                                                      lazy="dynamic"))

    def __repr__(self):
        return "<UploadedPhoto:%s>" % self.id or "-"


class Photo(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    timestamp = db.Column(DateTime, default=datetime.now)
    public = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text(2048))
    url = db.Column(db.Text(2048))
    rating = db.Column(db.Float)

    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    type = db.Column(db.String(20))

    s3_path = db.Column(db.Text(2048), nullable=True)

    # deleted ?
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(DateTime, nullable=True)

    # exif metadata
    make = db.Column(db.String(40))
    model = db.Column(db.String(40))
    orientation = db.Column(db.Integer)
    x_resolution = db.Column(RationalType)
    y_resolution = db.Column(RationalType)
    resolution_unit = db.Column(db.Integer)
    exposure_time = db.Column(RationalType)
    f_number = db.Column(RationalType)  # aperture
    exposure_program = db.Column(db.String(40))
    exif_version = db.Column(db.String(40))
    flash = db.Column(db.String(40))
    focal_length = db.Column(RationalType)
    color_space = db.Column(db.String(40))
    pixel_x_dimension = db.Column(db.Integer)
    pixel_y_dimension = db.Column(db.Integer)
    iso_speed_ratings = db.Column(db.String(10))

    aperture_value = db.Column(RationalType)
    max_aperture_value = db.Column(db.String(10))
    metering_mode = db.Column(db.String(10))
    exposure_mode = db.Column(db.String(10))

    # lens information
    lens_specification = db.Column(db.String(10))
    lens_make = db.Column(db.String(40))
    lens_model = db.Column(db.String(40))

    software = db.Column(db.String(40))
    host_computer = db.Column(db.String(40))

    date_time = db.Column(DateTime)
    date_time_digitized = db.Column(DateTime)
    date_time_original = db.Column(DateTime)

    copyright = db.Column(db.String(40))
    camera_owner_name = db.Column(db.String(100))

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
        photo.s3_path = "s3://%s/%s" % (app.config["PHOTO_BUCKET"],
                                        photo.gen_s3_key(f.filename))
        s3.upload_image(f.stream, photo.s3_path)

        # process exif tags
        f.stream.seek(0)
        img = Image.open(f.stream)
        photo.width, photo.height = img.size
        photo.process_exif(image=img)

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
        image_s3_path = self.gen_s3_key(path.basename(parsed.path), size)

        try:
            return s3.get_image("s3://%s/%s" % (parsed.hostname,
                                                image_s3_path))
        except PinholeFileNotFound:
            pass

        s3conn = s3.S3Adapter()
        bucket = s3conn.get_bucket(parsed.hostname)

        if size == "raw":
            key = bucket.get_key(parsed.path.lstrip("/"))
            if key is not None:
                # we have the image!
                fpath = s3.get_cache_fpath(self.s3_path)
                tmp_image = open(fpath, "wb+")
                key.get_contents_to_file(tmp_image)
                tmp_image.flush()
                tmp_image.seek(0)

                return tmp_image

        # the image doesn't exist, so let's create it
        key = bucket.get_key(parsed.path.lstrip("/"))
        if key is None:
            raise ValueError("{} - {}".format(self.s3_path, parsed.path))

        tmp_image = TemporaryFile(suffix=path.basename(parsed.path))
        key.get_contents_to_file(tmp_image)
        tmp_image.flush()
        tmp_image.seek(0)

        img_obj = Image.open(tmp_image)
        s = self.sizes[size]
        img_obj.thumbnail((s, s), Image.ANTIALIAS)

        #upload the image
        image_s3_path = self.gen_s3_key(path.basename(parsed.path), size)
        cache_fpath = s3.get_cache_fpath(image_s3_path)
        print "using ", cache_fpath
        new_image = open(cache_fpath, "wb+")
        img_obj.save(new_image, format="JPEG")
        new_image.flush()
        new_image.seek(0)

        key = Key(bucket)
        key.key = image_s3_path
        key.set_contents_from_file(new_image)

        new_image.seek(0)
        return new_image

    def process_exif(self, stream=None, image=None):
        """
        Process EXIF tags and save them in the object properties

        :param stream: file-like object
        :type stream: file
        :param image: image object
        :type image: :class:`PIL.Image.Image`
        :rtype: dict
        :returns: a dictionary with all the exif tags found
        """
        ret = {}
        if not image:
            i = Image.open(stream)
            if not i:
                msg = "Stream {} couldn't be opened as image".format(stream)
                raise ValueError(msg)
        else:
            i = image

        info = i._getexif()

        if not info:
            self.logger.info("Exif info not found in {}".format(i))
            return ret

        for tag, value in info.items():
            decoded = exif_tags.get(tag, tag)
            converted = convert(decoded)
            if isinstance(decoded, basestring) and hasattr(self, converted):
                if converted in exif_transform:
                    value = exif_transform[converted](value)
                setattr(self, converted, value)
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
        if prefix:
            fname = "%s_%s" % (prefix, fname)

        return "%s/%r/%s" % (self.user.username,
                             self.id,
                             fname)


class Roll(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(DateTime)
