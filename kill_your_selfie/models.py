"""database models"""
from flask import Flask
from flask_login import UserMixin

from .database import db


class Location(db.Model):
    """mapping of location labels to geographic coordinates"""
    __tablename__ = "location"

    label = db.Column(db.String(80), primary_key=True)
    latitude = db.Column(db.Double, unique=False, nullable=True)
    longitude = db.Column(db.Double, unique=False, nullable=True)

    occurrences = db.relationship("Occurrence", back_populates="location")

    def __repr__(self):
        return f"<Location {self.label}>"

class Occurrence(db.Model):
    """a time when 'kill yourself' was said"""
    __tablename__ = "occurrence"

    time = db.Column(db.TIMESTAMP, primary_key=True)
    location_label = db.Column(db.String(80), db.ForeignKey('location.label'))
    target = db.Column(db.String(80), unique=False, nullable=False)
    context = db.Column(db.String(), unique=False, nullable=False)

    location = db.relationship("Location", back_populates="occurrences")

    def __repr__(self):
        return f"<Occurrence {self.time}>"


class User(UserMixin, db.Model):
    """application user"""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False, unique=False)
    admin = db.Column(db.Boolean, nullable=False, unique=False)

    def __repr__(self):
        return f"<User {self.username}>"


def create_tables(app: Flask) -> None:
    """create tables in database that do not exist yet"""
    with app.app_context():
        db.create_all()
