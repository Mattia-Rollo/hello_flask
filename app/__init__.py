import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Configurazione database: PostgreSQL per produzione, SQLite per sviluppo
if os.environ.get('DATABASE_URL'):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///market.db"

# Secret key da variabile d'ambiente o fallback per sviluppo
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', '1bcc352a61e08df3e51ccc4c')

# Configurazioni aggiuntive per produzione
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from app import routes

app.app_context().push()
