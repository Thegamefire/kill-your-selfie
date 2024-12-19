"""main app process"""
# pylint: disable=C0301
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, logout_user, login_required, current_user

from .config import Config
from . import database, models, auth, stats, occurences


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
            return redirect(url_for("home") if (next_url := request.args.get("next")) is None else url_for(next_url))
        except auth.AuthenticationError as e:
            flash(f"Error: {e}")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """logs out the user"""
    logout_user()
    return redirect(url_for('index'))


@app.route("/home")
@login_required
def home():
    """home page"""
    return render_template(
        "index.html",
        active="home",
        weekly_bar_data=stats.weekly_bar_data(),
        location_map=stats.location_map_data(),
    )


@app.route('/new-user', methods=['GET', 'POST'])
@login_required
@auth.admin_required
def new_user():
    """new user register page"""
    if request.method == "POST":
        auth.create_user(
            request.form.get("username"),
            request.form.get("email"),
            request.form.get("password"),
            request.form.get("admin-state") == "on",
        )
        flash("User added")

    return render_template("new_user.html", active="new-user")


@app.route("/new-occurence", methods=["GET", "POST"])
@login_required
def new_occurence():
    """page to register a new occurence"""
    if request.method == "POST":
        occurences.add_occurence(
            # exception handling for datetime is not really needed since
            # form has built in validation
            datetime.strptime(request.form.get("time"), "%Y-%m-%dT%H:%M"),
            request.form.get("location"),
            request.form.get("target"),
            request.form.get("context"),
        )

    return render_template(
        "new_occurence.html",
        active="new-occurence",
        location_options=occurences.get_location_options(),
        target_options=occurences.get_target_options(),
    )


@app.route("/map-location", methods=["GET", "POST"])
@login_required
@auth.admin_required
def map_location():
    """page to map locations to geographical coordinates"""
    location_options = occurences.get_location_options()
    location_options.sort()
    if len(location_options) == 0:
        location_options=[""] # Add at least one element to the list so it is iterable

    if request.method == 'POST':
        occurences.map_location(
            request.form.get("location"),
            float(request.form.get("latitude")),
            float(request.form.get("longitude")),
        )

    return render_template(
        "map_location.html",
        active="map-location",
        loc_options = location_options,
    )
