# pylint: disable=C0111
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import text as sql_txt

db = SQLAlchemy()


def register_app(app: Flask) -> None:
    """register Flask app with SQLAlchemy instance"""
    db.init_app(app)


def get_sql_data(query) -> None:
    """get data from raw SQL query"""
    return db.session.execute(sql_txt(query)).fetchall()


def add_object(model_object: Model) -> None:
    """add object to database"""
    db.session.add(model_object)


def commit() -> None:
    """commit transaction"""
    db.session.commit()
