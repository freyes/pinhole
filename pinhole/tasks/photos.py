from os import path
#import celery
from celery.utils.log import get_task_logger
from werkzeug.datastructures import FileStorage
from pinhole.common.app import celery, db, app
from pinhole.common import models, s3
from pinhole.common.utils import mkdtemp

#from pinhole.common.extensions import celery, db, app
from celery.signals import task_postrun


logger = get_task_logger(__name__)


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


@celery.task
class ProcessUploadedPhoto(celery.Task):

    def run(self, up_photo_id, force=False):
        uploaded_photo = models.UploadedPhoto.get_by(id=up_photo_id)

        assert uploaded_photo is not None
        if uploaded_photo.processed and not force:
            return {"code": 10,
                    "message": "The %s was already processed" % uploaded_photo}
        s3conn = s3.S3Adapter()
        bucket = s3conn.get_bucket(app.config["INCOMING_PHOTO_BUCKET"])
        k = bucket.get_key(uploaded_photo.key)

        with mkdtemp() as tmpdir:
            forig_path = path.join(tmpdir, uploaded_photo.key)
            forig = open(forig_path, "w+b")
            k.get_contents_to_file(forig)
            forig.flush()
            forig.seek(0)

            fs = FileStorage(forig, uploaded_photo.filename)
            photo = models.Photo.from_file(uploaded_photo.user, fs)
            forig.seek(0)
            photo.create_thumbnails(uploaded_photo.filename, forig)

            # we are done.
            uploaded_photo.processed = True
            db.session.add(uploaded_photo)
            db.session.commit()
            k.delete()

        return {"photo_id": photo.id}
