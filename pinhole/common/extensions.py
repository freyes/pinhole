from celery import Celery
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask("pinhole")
celery = Celery("pinhole")
db = SQLAlchemy(session_options={"expire_on_commit": False})
login_manager = LoginManager()
