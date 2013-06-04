from flask.ext import restful
from flask.ext.restful import abort, fields, marshal_with, reqparse
from flask.ext.login import login_required, current_user
from pinhole.common import models
from pinhole.common.app import api, db


# TODO: put all the public fields here
tag_fields = {
    "id": fields.Integer,
    "name": fields.String,
    }

roll_fields = {
    'id': fields.Integer,
    "timestamp": fields.DateTime,
    }

photo_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    "timestamp": fields.DateTime,
    "roll": fields.Nested(roll_fields),
    "public": fields.Boolean,
    'rating': fields.Raw,
    "tags": fields.List(fields.Nested(tag_fields)),
}


photo_parser = reqparse.RequestParser()
photo_parser.add_argument('title', type=str)
photo_parser.add_argument('description', type=str)
photo_parser.add_argument('rating', type=float)
photo_parser.add_argument('tags', type=str)


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
        photo = models.Photo()
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


api.add_resource(Photo, '/api/v1/photos/<int:photo_id>')
api.add_resource(PhotoList, "/api/v1/photos")
