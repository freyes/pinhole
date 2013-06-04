from flask import session, redirect, url_for, request, render_template, flash
from flask.ext.login import (login_required, login_user, logout_user,
                             confirm_login)
from pinhole.common.app import app, login_manager
from pinhole.common.models import User


@app.route('/')
@login_required
def index():
    tpl_vars = {}
    if 'user_id' in session:
        tpl_vars["user"] = User.get_by(id=session["user_id"])

    return render_template("index.tpl", **tpl_vars)


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST" and "username" in request.form:
        #import ipdb; ipdb.set_trace()
        username = request.form["username"]
        password = request.form["password"]
        user = User.get_by(username=username)

        if user and user.check_password(password):
            remember = request.form.get("remember", "no") == "yes"
            if login_user(user, remember=remember):
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username.")

    return render_template("auth/login.tpl")


login_manager.login_view = "login"


@app.route("/account/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("reauth.html")


@app.route("/account/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(userid):
    return User.get_by(id=userid)
