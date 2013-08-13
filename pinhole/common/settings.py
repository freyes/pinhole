from os import environ

DB_URI = environ.get("PINHOLE_DB_URI", 'sqlite:////tmp/pinhole_unittests.db')

# configuration
DEBUG = True
SECRET_KEY = 'development key'
SQLALCHEMY_DATABASE_URI = DB_URI

AWS_ACCESS_KEY = environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = environ["AWS_SECRET_KEY"]
PHOTO_BUCKET = environ["PINHOLE_PHOTO_BUCKET"]
INCOMING_PHOTO_BUCKET = environ["PINHOLE_INCOMING_PHOTO_BUCKET"]

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
