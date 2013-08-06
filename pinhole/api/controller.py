from __future__ import absolute_import
import re
import operator
import logging
from datetime import datetime
from sqlalchemy.sql.expression import and_, or_
from flask import request, make_response, send_file
from flask.ext import restful
from flask.ext.restful import abort, marshal_with, fields, marshal
from flask.ext.login import login_required, current_user, login_user
from pinhole.common import models
from pinhole.common.app import db, app
from flask.ext.restful import Api
from pinhole.common.s3 import S3Adapter
from pinhole.tasks.photos import ProcessUploadedPhoto
from .params import (photo_fields, photo_parser, photolist_parser,
                     uploaded_photo_fields, uploaded_photos_fields,
                     users_fields, user_fields, user_parser, photos_fields,
                     foto_fields)
from . import params


# api setup
api = Api(app, prefix="/api/v1")

RE_OP = re.compile("^(.*)__(lt|le|eq|ne|ge|gt)$")
logger = logging.getLogger(__name__)


class Photo(restful.Resource):
    @login_required
    @marshal_with(foto_fields)
    def get(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 1:
            return {"photo": photos.first()}

        return abort(404, message="Photo {} doesn't exist".format(photo_id))

    @login_required
    def delete(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 0:
            return abort(404,
                         message="Photo {} doesn't exist".format(photo_id))

        photo = photos.first()
        photo.deleted = True
        photo.deleted_at = datetime.now()
        db.session.add(photo)
        db.session.commit()


class PhotoList(restful.Resource):
    @login_required
    @marshal_with(photo_fields)
    def post(self):
        args = photo_parser.parse_args()
        photo = models.Photo.from_file(current_user,
                                       args.get("picture").stream)
        photo.title = args.get("title")
        photo.description = args.get("description")
        photo.rating = args.get("rating")
        photo.user = current_user
        db.session.add(photo)
        db.session.commit()

        tags = args.get("tags")
        if tags:
            for tag_name in tags.split(","):
                photo.add_tag(tag_name.strip())

        return photo

    @login_required
    @marshal_with(photos_fields)
    def get(self):
        args = photolist_parser.parse_args()
        photos = models.Photo.query.filter_by(user_id=current_user.id)
        filters = and_()

        for key in request.args:
            matched = RE_OP.match(key)
            if matched and matched.group(1) in photo_fields:
                prop = getattr(models.Photo, matched.group(1))
                op = getattr(operator, matched.group(2))
                filters.append(op(prop, request.args[key]))
            elif key in photo_fields:
                prop = getattr(models.Photo, key)
                filters.append(prop == request.args[key])

        photos = photos.filter(filters)
        if args["order_by"] in photo_fields:
            photos = photos.order_by(args["order_by"])

        return {"photos": photos.all()}


class UploadedPhotos(restful.Resource):
    @login_required
    @marshal_with(uploaded_photos_fields)
    def get(self):
        photos = models.UploadedPhoto.query.filter_by(user_id=current_user.id,
                                                      processed=False)
        return {"uploaded_photos": photos.all()}

    @login_required
    def post(self):
        o = models.UploadedPhoto()
        o.user_id = current_user.id
        for key, value in request.json["uploaded_photo"].items():
            if hasattr(o, key):
                setattr(o, key, value)
        db.session.add(o)
        db.session.commit()

        task = ProcessUploadedPhoto.delay(o.id)
        logger.debug("Sent %s" % task)

        return marshal({"uploaded_photo": o}, uploaded_photo_fields), 200


class PhotoFile(restful.Resource):
    @login_required
    def get(self, photo_id, size, fname):
        if size not in models.Photo.sizes:
            return abort(404,
                         message="Photo format {} doesn't exist".format(size))

        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 0:
            return abort(404,
                         message="Photo {} doesn't exist".format(photo_id))

        photo = photos.first()

        return send_file(photo.get_image(size),
                         attachment_filename=photo.fname,
                         add_etags=False)


class User(restful.Resource):
    @login_required
    @marshal_with(user_fields)
    def get(self, user_id):
        if user_id != current_user.id:
            return abort(404, message="User {} doesn't exist".format(user_id))

        return {"user": current_user}


class UserList(restful.Resource):
    @login_required
    @marshal_with(users_fields)
    def get(self):
        args = user_parser.parse_args()

        username = args["username"]
        if username and username != current_user.username:
            return abort(404, message="User {} doesn't exist".format(username))

        return {"users": [current_user]}

    @marshal_with(params.user_fields)
    def post(self):
        args = params.register_user.parse_args()

        filters = or_()
        filters.append(models.User.email == args["email"])
        filters.append(models.User.username == args["username"])
        users = models.User.query.filter(filters)

        if users.count() > 0:
            return abort(400, message="Username/email already in use")

        user = models.User(args["username"], args["email"])
        user.set_password(args["password"], commit=False)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=False)

        return {"user": user}


class UsersAvailable(restful.Resource):
    def post(self):
        args = params.check_user_parser.parse_args()

        if not args.get("email") and not args.get("username"):
            return abort(404, message="Provide email or username")

        filters = or_()
        if args.get("email"):
            filters.append(models.User.email == args["email"])

        if args.get("username"):
            filters.append(models.User.username == args["username"])

        users = models.User.query.filter(filters)
        if users.count() == 0:
            return "true", 200
        else:
            return "Already in use, please try another", 200


class Authenticated(restful.Resource):
    def get(self):
        authenticated = current_user.is_authenticated()
        if authenticated:
            return marshal({"authenticated": authenticated,
                            "user": current_user},
                           {"authenticated": fields.Boolean,
                            "user": user_fields["user"]}), 200
        else:
            return marshal({"authenticated": authenticated},
                           {"authenticated": fields.Boolean}), 200

    def post(self):
        args = params.login_parser.parse_args()

        user = models.User.get_by(username=args["username"])

        if not user or not user.check_password(args["password"]):
            return abort(404,
                         message="Wrong Username and password combination.")

        if login_user(user, remember=False):
            return marshal({"authenticated": True, "user": user},
                           {"authenticated": fields.Boolean,
                            "user": user_fields["user"]}), 200
        else:
            return abort(404, message="Invalid username/password combination")


endpoints = [(Photo, '/photos/<int:photo_id>'),
             (PhotoList, "/photos"),
             (UploadedPhotos, "/uploaded_photos"),
             (PhotoFile,
              '/photos/file/<int:photo_id>/<string:size>/<string:fname>'),
             (User, "/users/<int:user_id>"),
             (UserList, "/users"),
             (UsersAvailable, "/users_available"),
             (Authenticated, "/authenticated"),
             ]
for args in endpoints:
    try:
        api.add_resource(*args)
    except ValueError:
        pass
