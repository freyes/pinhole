from os import path
from flask import send_from_directory
from pinhole.common.app import app

__DOT = path.join(path.dirname(path.abspath(__file__)), "static")


@app.route('/media/<path:filename>')
def send_file(filename):
    return send_from_directory(__DOT, filename)
