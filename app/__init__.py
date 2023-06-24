from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = '1bcc352a61e08df3e51ccc4c'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from app import routes

app.app_context().push()
