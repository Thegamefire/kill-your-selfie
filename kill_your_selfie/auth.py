"""functions for authentication"""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import login_user

from . import models

_bcrypt = Bcrypt()

def init_bcrypt(app: Flask) -> None:
    """initialise bcrypt with app (calls init_app on Bcrypt object)"""
    _bcrypt.init_app(app)


def authenticate_user(username: str, password: str) -> str:
    """Attempts to authenticate a user.
    Returns:
    - `success` if the user got logged in;
    - `err_wrong_password` if the password is wrong;
    - `err_not_found` if a user with the username doesn't exist.
    """
    # Finds a user by filtering for the username
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        return "err_not_found"
    # Check if the password entered is the same as the user's password
    if _bcrypt.check_password_hash(user.password, password):
        # Use the login_user method to log in the user
        login_user(user, remember=True)
        return 'success'

    return 'err_wrong_password'
