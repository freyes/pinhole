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

photo_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    "timestamp": fields.DateTime,
    "roll": fields.Nested(roll_fields),
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
