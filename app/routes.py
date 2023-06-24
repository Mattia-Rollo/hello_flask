from app import app,db
from flask import render_template, redirect, url_for, flash
from app.models import Item, User
from app.forms import RegisterForm

name='Mattia'
surname = 'Rollo'
@app.route('/')
def home_page():
    return render_template('index.html', name=name, surname=surname)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', name=name, surname=surname)

@app.route('/market')
def market():
    items = Item.query.all()
    return render_template('market.html', items=items)

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address= form.email_address.data,
                              password_hash=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('market'))
    if form.errors != {}: #if there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'there was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)