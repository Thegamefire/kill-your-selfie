"""main app process"""
# pylint: disable=C0301
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, logout_user, login_required, current_user

from .config import Config
from . import database, models, auth, stats, occurrences

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


@app.route("/debug-ui")
def basepage():
    """displays the base html template"""
    flash("Debug ui")
    flash("another message")
    flash("oooOOOoo")
    return render_template("form.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """login page"""
    if request.method == "POST":
        message, success = auth.authenticate_user(request.form.get("username"), request.form.get("password"))
        if success:
            return redirect(url_for("home") if (next_url := request.args.get("next")) is None else url_for(next_url))
        else:
            flash(f"Error: {message}")

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
        monthly_line_data=stats.line_data('month'),
        yearly_line_data=stats.line_data('year'),
        location_map=stats.location_map_data(),
    )


@app.route('/user-settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """user settings page"""
    if request.method == "POST":
        try:
            auth.update_user(
                current_user.id,
                request.form.get("username"),
                request.form.get("email"),
                request.form.get("new-password"),
                request.form.get("current-password"),
            )
            flash("Settings updated")
        except auth.AuthenticationError as exc:
            flash(str(exc))
    return render_template("user_settings.html", active="user-settings")


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


@app.route("/new-occurrence", methods=["GET", "POST"])
@login_required
def new_occurrence():
    """page to register a new occurrence"""
    if request.method == "POST":
        occurrences.add_occurrence(
            # exception handling for datetime is not really needed since
            # form has built in validation
            datetime.strptime(request.form.get("time"), "%Y-%m-%dT%H:%M"),
            request.form.get("location"),
            request.form.get("target"),
            request.form.get("context"),
        )

    return render_template(
        "new_occurrence.html",
        active="new-occurrence",
        location_options=occurrences.get_location_options(),
        target_options=occurrences.get_target_options(),
    )


@app.route("/map-location", methods=["GET", "POST"])
@login_required
@auth.admin_required
def map_location():
    """page to map locations to geographical coordinates"""
    location_options = occurrences.get_location_options()
    location_options.sort()
    if len(location_options) == 0:
        location_options = [""]  # Add at least one element to the list so it is iterable

    if request.method == 'POST':
        occurrences.map_location(
            request.form.get("location"),
            float(request.form.get("latitude")),
            float(request.form.get("longitude")),
        )

    return render_template(
        "map_location.html",
        active="map-location",
        loc_options=location_options,
    )
