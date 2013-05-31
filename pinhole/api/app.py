from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask("pinhole.api")
app.config.from_object("pinhole.api.settings")
app.config.from_envvar('PINHOLE_API_SETTINGS', silent=True)
db = SQLAlchemy(app)
