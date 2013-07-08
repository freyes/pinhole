from pinhole.common.app import app


CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_URI = app.config["SQLALCHEMY_DATABASE_URI"]
CELERY_RESULT_ENGINE_OPTIONS = {"echo": app.config["SQL_ECHO"]}
BROKER_URL = os.environ.get("BROKER", 'amqp://guest@localhost//')
BROKER_USE_SSL = True
CELERY_ALWAYS_EAGER = bool(os.environ.get("CELERY_ALWAYS_EAGER", False))
