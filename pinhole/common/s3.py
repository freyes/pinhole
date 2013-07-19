from __future__ import absolute_import
from boto.s3.connection import S3Connection

__all__ = ["S3Adapter"]


class S3Adapter(S3Connection):
    def __init__(self, access_key=None, secret_key=None):
        from pinhole.common.app import app

        if not access_key:
            access_key = app.config["AWS_ACCESS_KEY"]

        if not secret_key:
            secret_key = app.config["AWS_SECRET_KEY"]

        S3Connection.__init__(self, access_key, secret_key)
