from app import app, db
from flask import render_template, redirect, url_for, flash
from app.models import Item, User
from app.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, current_user

name = "Mattia"
surname = "Rollo"


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", name=name, surname=surname)


@app.route("/market")
def market():
    items = current_user.items
    # items = Item.query.filter_by(owner=current_user.id).all()
    return render_template("market.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for("market"))
    if form.errors != {}:  # if there are not errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg[0], category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f"Success! You are logged in as: {attempted_user.username}",
                category="success",
            )
            return redirect(url_for("market"))
        else:
            flash(
                f"Username and password are not match! Please try again",
                category="danger",
            )
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect("/")
