from flask import request
from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.login import login_required
from pinhole.common import models
from pinhole.common.app import api


class Photo(restful.Resource):
    @login_required
    def get(self, photo_id):
        photos = models.Photo.query.filter_by(id=photo_id,
                                              user_id=request.user.id)
        if photos.count() == 1:
            return photos.first()

        return abort(404, message="Photo {} doesn't exist".format(photo_id))


api.add_resource(Photo, '/api/v1/photos/<int:photo_id>')
