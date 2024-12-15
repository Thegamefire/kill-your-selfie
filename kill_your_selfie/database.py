# pylint: disable=C0111
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as sql_txt


db = SQLAlchemy()


def register_app(app: Flask) -> None:
    """register Flask app with SQLAlchemy instance"""
    db.init_app(app)


def get_sql_data(query) -> None:
    """get data from raw SQL query"""
    return db.session.execute(sql_txt(query)).fetchall()


add = db.session.add
commit = db.session.commit
rollback = db.session.rollback
