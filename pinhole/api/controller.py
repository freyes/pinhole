from __future__ import absolute_import
from flask.ext import restful
from flask.ext.restful import abort, marshal_with
from flask.ext.login import login_required, current_user
from pinhole.common import models
from pinhole.common.app import api, db
from .params import photo_fields, photo_parser


class Photo(restful.Resource):
    @login_required
    @marshal_with(photo_fields)
    def get(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 1:
            return photos.first()

        return abort(404, message="Photo {} doesn't exist".format(photo_id))


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


api.add_resource(Photo, '/photos/<int:photo_id>')
api.add_resource(PhotoList, "/photos")
