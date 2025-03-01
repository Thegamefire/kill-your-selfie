"""functions for database interaction"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as sql_txt

from typing import Sequence
from sqlalchemy.engine import Row

db = SQLAlchemy()

add = db.session.add
commit = db.session.commit
rollback = db.session.rollback


def register_app(app: Flask) -> None:
    """register Flask app with SQLAlchemy instance"""
    db.init_app(app)


def get_sql_data(query) -> Sequence[Row]:
    """get data from raw SQL query"""
    return db.session.execute(sql_txt(query)).fetchall()
