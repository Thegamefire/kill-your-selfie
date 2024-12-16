"""functions for authentication"""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import login_user

from . import models, database

_bcrypt = Bcrypt()


class AuthenticationError(Exception):
    """Authentication error"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"


class UserExistsError(Exception):
    """User already exists error"""
    def __init__(self, *args):
        super().__init__(*args)

def init_bcrypt(app: Flask) -> None:
    """initialise bcrypt with app (calls init_app on Bcrypt object)"""
    _bcrypt.init_app(app)

def authenticate_user(username: str, password: str) -> None:
    """Attempts to authenticate a user.
    Returns:
    - `success` if the user got logged in;
    - `err_wrong_password` if the password is wrong;
    - `err_not_found` if a user with the username doesn't exist.
    Raises AuthenticationError when the user can't be logged in.
    - Use AuthenticationError.message to retrieve the error message.
    """
    # Finds a user by filtering for the username
    user = models.User.query.filter_by(username=username).first()
    if user is None:
        raise AuthenticationError("User with that username doesn't exist")
    # Check if the password entered is the same as the user's password
    if _bcrypt.check_password_hash(user.password, password):
        # Use the login_user method to log in the user
        login_user(user, remember=True)
        return 'success'

    raise AuthenticationError("Wrong password")


def create_user(username: str, email: str, password: str, admin: bool = False) -> None:
    """Creates a new user. Raises UserExistsError when a user with
    the given username already exists.
    Use UserExistsError.message to retrieve the error message.
    """
    pw_hash = _bcrypt.generate_password_hash(password).decode(
        "utf-8"
    )
    new_user = models.User(
        username=username,
        email=email,
        password=pw_hash,
        admin=admin,
    )
    database.add(new_user)
    database.commit()
