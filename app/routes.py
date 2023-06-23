from app import app
from flask import render_template
from app.models import Item

name='Mattia'
surname = 'Rollo'
@app.route('/')
def index():
    return render_template('index.html', name=name, surname=surname)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', name=name, surname=surname)

@app.route('/market')
def market():
    items = Item.query.all()
    return render_template('market.html', items=items)