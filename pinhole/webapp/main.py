from flask import session, render_template
from flask.ext.login import login_required
from pinhole.common.app import app
from pinhole.common.models import User


@app.route('/')
@login_required
def index():
    tpl_vars = {}
    if 'user_id' in session:
        tpl_vars["user"] = User.get_by(id=session["user_id"])

    return render_template("index.tpl", **tpl_vars)
