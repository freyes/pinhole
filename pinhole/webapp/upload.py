from flask import render_template
from flask.ext.login import login_required
from pinhole.common.app import app


@app.route("/upload")
def upload():
    return render_template("upload.tpl")
