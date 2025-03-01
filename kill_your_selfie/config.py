# pylint: disable=C0111
from os import environ
from dotenv import load_dotenv


load_dotenv()


class Config:
    """app configuration"""
    DB_USERNAME = environ.get("DB_USERNAME")
    DB_PASSWORD = environ.get("DB_PASSWORD")
    DB_HOST = environ.get("DB_HOST")
    DB_PORT = environ.get("DB_PORT")
    DB_DATABASE = environ.get("DB_DATABASE")
    SECRET = environ.get("FLASK_SECRET")
    NTFY_AUTH = environ.get("NTFY_AUTH")
    NTFY_ENDPOINT = environ.get("NTFY_ENDPOINT")
