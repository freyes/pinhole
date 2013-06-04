from __future__ import absolute_import
from flask.ext.sqlalchemy import SQLAlchemy
from .auth import check_password, make_password

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

    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

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


class Roll(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime)
