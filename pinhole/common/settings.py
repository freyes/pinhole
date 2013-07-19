from os import environ

DB_URI = 'sqlite:////tmp/pinhole_unittests.db'

# configuration
DEBUG = True
SECRET_KEY = 'development key'
SQLALCHEMY_DATABASE_URI = DB_URI

AWS_ACCESS_KEY = "AKIAIWNMBKL4DUKXLWBQ"
AWS_SECRET_KEY = "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"
PHOTO_BUCKET = "storage.pinhole.tty.cl"
INCOMING_PHOTO_BUCKET = "dev.pinhole.tty.cl"

# ---------------------------------------------
# Celery

# tasks enabled
CELERY_IMPORTS = ("pinhole.tasks.photos", )

# result backend
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = DB_URI
CELERY_RESULT_ENGINE_OPTIONS = {"echo": bool(environ.get("SQL_ECHO", False))}

# broker
BROKER_URL = environ.get("BROKER_URL", 'amqp://guest@localhost//')
BROKER_USE_SSL = False

# testing related settings
CELERY_ALWAYS_EAGER = False
