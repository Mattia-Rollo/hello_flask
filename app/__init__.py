from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = '1bcc352a61e08df3e51ccc4c'
db = SQLAlchemy(app)

from app import routes

app.app_context().push()
