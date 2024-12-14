# pylint: disable=C0111
from flask_sqlalchemy import SQLAlchemy
from .app import app

db = SQLAlchemy(app)
