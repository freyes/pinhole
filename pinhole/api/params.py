import datetime
from flask.ext.restful import fields, reqparse
from werkzeug.datastructures import FileStorage


__all__ = ["tag_fields", "roll_fields", "photo_fields",
           "photo_parser"]
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'


class DateTime(fields.Raw):
    def format(self, value):
        if value and hasattr(value, "strftime"):
            return value.strftime(ISO8601)
        else:
            return value


def parse_ts(ts):
    ts = ts.strip()
    dt = datetime.datetime.strptime(ts, ISO8601)
    return dt


# TODO: put all the public fields here
tag_fields = {
    "id": fields.Integer,
    "name": fields.String,
}

tags = {"tags": fields.List(fields.Nested(tag_fields))}
tag = {"tag": fields.Nested(tag_fields)}

roll_fields = {
    'id': fields.Integer,
    "timestamp": DateTime,
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
    "timestamp": DateTime,
    "roll_id": fields.Integer,
    "public": fields.Boolean,
    'rating': fields.Raw,
    "tags": fields.List(fields.Nested(tag_fields)),
    "tag_ids": fields.List(fields.Integer),
    "height": fields.Raw,
    "width": fields.Raw,
    "make": fields.Raw,
    "model": fields.Raw,
    "software": fields.Raw,
    "date_time": DateTime,
    "date_time_digitized": DateTime,
    "date_time_original": DateTime,
}

photos_fields = {"photos": fields.List(fields.Nested(photo_fields))}
foto_fields = {"photo": fields.Nested(photo_fields)}

photo_parser = reqparse.RequestParser()
photo_parser.add_argument('title', type=str)
photo_parser.add_argument('description', type=str)
photo_parser.add_argument("timestamp", type=str)
photo_parser.add_argument("roll_id", type=int)
photo_parser.add_argument("public", type=bool)
photo_parser.add_argument('rating', type=float)
photo_parser.add_argument('tags', type=str)
photo_parser.add_argument("height", type=int)
photo_parser.add_argument("width", type=int)
photo_parser.add_argument("make", type=str)
photo_parser.add_argument("model", type=str)
photo_parser.add_argument("software", type=str)
photo_parser.add_argument("date_time", type=parse_ts)
photo_parser.add_argument("date_time_digitized", type=parse_ts)
photo_parser.add_argument("date_time_original", type=parse_ts)

photo_parser.add_argument('picture', type=FileStorage, location='files',
                          required=False)

photolist_parser = reqparse.RequestParser()
photolist_parser.add_argument("order_by", type=str,
                              default="DateTimeOriginal")
photolist_parser.add_argument("limit", type=int, default=0)

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

check_user_parser = reqparse.RequestParser()
check_user_parser.add_argument('username', type=str)
check_user_parser.add_argument('email', type=str)


login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True)
login_parser.add_argument('password', type=str, required=True)

register_user = reqparse.RequestParser()
register_user.add_argument('username', type=str, required=True)
register_user.add_argument('password', type=str, required=True)
register_user.add_argument('email', type=str, required=True)
