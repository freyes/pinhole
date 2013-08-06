from flask import render_template
from pinhole.common.app import app


@app.route("/upload")
def upload():
    return render_template("upload.tpl")
