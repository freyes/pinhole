from flask.ext.restful import fields, reqparse
from werkzeug.datastructures import FileStorage


__all__ = ["tag_fields", "roll_fields", "photo_fields",
           "photo_parser"]

# TODO: put all the public fields here
tag_fields = {
    "id": fields.Integer,
    "name": fields.String,
}

roll_fields = {
    'id': fields.Integer,
    "timestamp": fields.DateTime,
}

up_photo_fields = {
    "id": fields.Integer,
    "url": fields.String,
    "filename": fields.String,
    "size": fields.Integer,
    "key": fields.String,
    "is_writeable": fields.Boolean
}


uploaded_photos_fields = {"uploaded_photos":
                          fields.List(fields.Nested(up_photo_fields))}
uploaded_photo_fields = {"uploaded_photo": fields.Nested(up_photo_fields)}

photo_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    "timestamp": fields.DateTime,
    "roll_id": fields.Integer,
    "public": fields.Boolean,
    'rating': fields.Raw,
    "tags": fields.List(fields.Nested(tag_fields)),
    "height": fields.Raw,
    "width": fields.Raw,
    "Make": fields.Raw,
    "Model": fields.Raw,
    "Software": fields.Raw,
    "DateTime": fields.DateTime,
    "DateTimeDigitized": fields.DateTime,
    "DateTimeOriginal": fields.DateTime,
}

photos_fields = {"photos": fields.List(fields.Nested(photo_fields))}
foto_fields = {"photo": fields.Nested(photo_fields)}

photo_parser = reqparse.RequestParser()
photo_parser.add_argument('title', type=str)
photo_parser.add_argument('description', type=str)
photo_parser.add_argument("roll_id", type=int)
photo_parser.add_argument("public", type=bool)
photo_parser.add_argument('rating', type=float)
photo_parser.add_argument('tags', type=str)
photo_parser.add_argument('picture', type=FileStorage, location='files',
                          required=True)

photolist_parser = reqparse.RequestParser()
photolist_parser.add_argument("order_by", type=str,
                              default="DateTimeOriginal")

_user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "active": fields.Boolean,
}

user_fields = {"user": fields.Nested(_user_fields)}
users_fields = {"users": fields.List(fields.Nested(_user_fields))}
user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str)

login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)
