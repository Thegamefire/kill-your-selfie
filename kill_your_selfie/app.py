"""main app process"""
# pylint: disable=C0301
from datetime import datetime, timedelta

import folium
import folium.plugins
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, logout_user, login_required, current_user
import sqlalchemy
import sqlalchemy.exc

from .config import Config
from . import database, models, util, auth, stats


login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
auth.init_bcrypt(app)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{Config.DB_USERNAME}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_DATABASE}"
)
app.config["SECRET_KEY"] = Config.SECRET

database.register_app(app)
models.create_tables(app)



@login_manager.user_loader
def load_user(user_id):
    """loads a user probably"""
    return models.User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    """redirect user to login page when they try to access a
    resource that requires login
    """
    return redirect(url_for("login", next=request.endpoint))


@app.route("/")
def index():
    """webroot, redirects to either home page or login page"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route("/base")
def basepage():
    """displays the base html template"""
    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """login page"""
    if request.method == "POST":
        try:
            auth.authenticate_user(request.form.get("username"), request.form.get("password"))
            return redirect(url_for("home") if (next_url := request.args.get("next")) is None else next_url)
        except auth.AuthenticationError as e:
            flash(f"Error: {e}")

    return render_template("login.html")


@app.route("/home")
@login_required
def home():
    """home page"""
    return render_template(
        "index.html",
        weekly_bar_data=stats.weekly_bar_data(),
        location_map=stats.location_map_data(),
    )


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """new user register page"""
    if request.method == "POST":
        auth.create_user(
            request.form.get("username"),
            request.form.get("email"),
            request.form.get("password"),
            request.form.get("admin-state") == "on",
        )
        flash("User added")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    """logs out the user"""
    logout_user()
    return redirect(url_for('index'))


@app.route("/new_record", methods=["GET", "POST"])
@login_required
def new_record():
    """page to register a new occurence"""
    location_options = util.get_location_options()
    target_options = []

    for occurence in models.Occurence.query.all():
        if not occurence.target in target_options:
            target_options.append(occurence.target)
    if request.method == "POST":
        try:
            time_dt = datetime.strptime(request.form.get("time"), "%Y-%m-%dT%H:%M")
            new_occurence = models.Occurence(
                time=time_dt,
                location_label=request.form.get("location"),
                target=request.form.get("target"),
                context=request.form.get("context"),
            )
            if new_occurence.location not in location_options:
                new_location = models.Location(
                    label=new_occurence.location_label,
                    latitude=None,
                    longitude=None
                )
                database.add(new_location)
            database.add(new_occurence)
            database.commit()
            flash("Occurence added")
        except ValueError:
            flash("You need to at least fill out Time correctly")
    return render_template(
        "new_record.html", location_options=location_options, target_options=target_options

    )


@app.route("/location_link", methods=["GET", "POST"])
@login_required
def location_link():
    """page to map locations to geographical coordinates"""
    loc_options = util.get_location_options()
    loc_options.sort()
    if len(loc_options) == 0:
        loc_options=[""] # Add at least one element to the list so it is iterable

    if request.method == 'POST':
        location = models.Location.query.filter_by(label=request.form.get("location")).first()
        location.latitude = float(request.form.get("latitude"))
        location.longitude = float(request.form.get("longitude"))
        database.commit()

    return render_template("location_link.html", loc_options = loc_options)
