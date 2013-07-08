from __future__ import absolute_import
from os import path
from importlib import import_module
from flask import Flask
from flask.ext.restful import Api
from flask.ext.login import LoginManager

from .models import db

TEMPLATES_DIR = path.join(path.dirname(path.abspath(__file__)), "..",
                          "webapp", "templates")
# wgi setup
app = Flask("pinhole.common", template_folder=TEMPLATES_DIR)
app.config.from_object("pinhole.common.settings")
app.config.from_envvar('PINHOLE_SETTINGS')

# database setup
db.app = app
db.init_app(app)

# api setup
api = Api(app, prefix="/api/v1")

login_manager = LoginManager()
login_manager.init_app(app)


def application(environ=None, start_response=None):
    global app

    # api controllersm dynamic import to prevent Chinese Lock
    for m in ["controller", ]:
        import_module("pinhole.api.%s" % m)

    # web app controllers dynamic import to prevent Chinese Lock
    for m in ["main", "static", "auth", "upload"]:
        import_module("pinhole.webapp.%s" % m)

    if not environ or not start_response:
        return app
    else:
        return app(environ, start_response)

try:
    db.create_all()
except Exception as ex:
    import traceback
    traceback.print_exc()
