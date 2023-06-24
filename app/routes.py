from app import app
from flask import render_template
from app.models import Item
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

@app.route('/register')
def register_page():
    form = RegisterForm()
    return render_template('register.html', form=form)