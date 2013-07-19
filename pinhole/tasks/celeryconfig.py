import os
from pinhole.common.app import app

# tasks enabled
CELERY_IMPORTS = ("pinhole.tasks.photos", )

# result backend
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = 'sqlite:////tmp/pinhole_unittests.db'
CELERY_RESULT_ENGINE_OPTIONS = {"echo": app.config["SQL_ECHO"]}

# broker
BROKER_URL = os.environ.get("BROKER", 'amqp://guest@localhost//')
BROKER_USE_SSL = False

# testing related settings
CELERY_ALWAYS_EAGER = bool(os.environ.get("CELERY_ALWAYS_EAGER", False))
