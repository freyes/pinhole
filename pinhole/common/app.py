from __future__ import absolute_import

from os import path
from importlib import import_module

#from .models import db
from .extensions import celery, db, app, login_manager

TEMPLATES_DIR = path.join(path.dirname(path.abspath(__file__)), "..",
                          "webapp", "templates")


def application(environ=None, start_response=None):
    # wgi setup
    app.template_folder = TEMPLATES_DIR
    app.config.from_object("pinhole.common.settings")
    app.config.from_envvar('PINHOLE_SETTINGS', silent=True)

    # celery
    celery.config_from_object(app.config)

    # database setup
    if db.app is None:
        db.app = app
        db.init_app(app)

    if not hasattr(app, "login_manager") or app.login_manager is None:
        login_manager.init_app(app)
        from .models import User
        login_manager.user_loader(lambda id_: User.get_by(id=id_))

    # api controllersm dynamic import to prevent Chinese Lock
    for m in ["controller", ]:
        import_module("pinhole.api.%s" % m)

    # web app controllers dynamic import to prevent Chinese Lock
    for m in ["main", "static", "upload"]:
        import_module("pinhole.webapp.%s" % m)

    if not environ or not start_response:
        return app
    else:
        return app(environ, start_response)


application()

try:
    db.create_all()
except:
    pass
