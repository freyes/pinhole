from flask.ext import restful
from flask.ext.restful import abort, fields, marshal_with
from flask.ext.login import login_required, current_user
from pinhole.common import models
from pinhole.common.app import api


# TODO: put all the public fields here
photo_fields = {
    'id': fields.Integer,
    'title': fields.String,
}


class Photo(restful.Resource):
    @login_required
    @marshal_with(photo_fields)
    def get(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=current_user.id)
        if photos.count() == 1:
            return photos.first()

        return abort(404, message="Photo {} doesn't exist".format(photo_id))


api.add_resource(Photo, '/api/v1/photos/<int:photo_id>')
