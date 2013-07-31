import os

DB_URI = os.environ.get("PINHOLE_DB_URI", 'sqlite:////tmp/foo.db')
SQLALCHEMY_DATABASE_URI = DB_URI
CELERY_RESULT_DBURI = DB_URI
CELERY_ALWAYS_EAGER = True
