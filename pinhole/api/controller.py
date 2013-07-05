from __future__ import absolute_import
import re
import operator
from datetime import datetime
from sqlalchemy.sql.expression import and_
from flask import request
from flask.ext import restful
from flask.ext.restful import abort, marshal_with, fields, marshal
from flask.ext.login import login_required, current_user
from pinhole.common import models
from pinhole.common.app import api, db
from .params import (photo_fields, photo_parser, photolist_parser,
                     uploaded_photo_fields, uploaded_photos_fields)


RE_OP = re.compile("^(.*)__(lt|le|eq|ne|ge|gt)$")


class Photo(restful.Resource):
    @login_required
    @marshal_with(photo_fields)
    def get(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 1:
            return photos.first()

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
        photo = models.Photo.from_file(current_user, args.get("picture"))
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
    @marshal_with(photo_fields)
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

        return photos.all()


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

        # TODO: queue task to process the photo
        # task = ProcessUploadedPhoto().apply_async()

        return marshal({"uploaded_photo": o}, uploaded_photo_fields), 200


api.add_resource(Photo, '/photos/<int:photo_id>')
api.add_resource(PhotoList, "/photos")
api.add_resource(UploadedPhotos, "/uploaded_photos")
