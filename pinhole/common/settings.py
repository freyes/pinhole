import os


# configuration
DEBUG = True
SECRET_KEY = 'development key'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/pinhole_data.db'
AWS_ACCESS_KEY = "AKIAIWNMBKL4DUKXLWBQ"
AWS_SECRET_KEY = "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"
PHOTO_BUCKET = "storage.pinhole.tty.cl"
INCOMING_PHOTO_BUCKET = "dev.pinhole.tty.cl"
SQL_ECHO = DEBUG or bool(os.environ.get("SQL_ECHO", False))
