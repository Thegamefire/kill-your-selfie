"""main app process"""
# pylint: disable=C0301
from datetime import datetime, timedelta

import folium
import folium.plugins
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, logout_user, login_required, current_user

from .config import Config
from . import database, models, util, auth


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
    ### Chart Data
    ## Weekly Bar Graph
    weekly_bar_data = []
    occurences_per_day = database.get_sql_data(
        "SELECT DATE_TRUNC('day', time)::date AS day, COUNT(time) AS amount FROM occurence GROUP BY DATE_TRUNC('day', time) ORDER BY DATE_TRUNC('day', time) ASC"
    )
    # filter selection on days from last 7 days
    for day in occurences_per_day:
        if (day[0] >= (datetime.now() - timedelta(days=7)).date() and day[0] <= datetime.now().date()):
            weekly_bar_data.append((day[0].strftime("%A"), day[1])) # add tuple consisting of name of weekday and amount of uses on that day

    # add the weekdays without entries to the data
    weekdays = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    first_day = int((datetime.now() - timedelta(days=7)).strftime("%w")) + 1 # get the index of the first weekday of our selection
    weekdays = weekdays[first_day:] + weekdays[:first_day] # shift the array to start with the first weekday we want

    i = 0
    while i < len(weekdays): # add empty weekdays that don't appear in the database
        if i>=len(weekly_bar_data):
            weekly_bar_data.append((weekdays[i], 0))
        elif weekdays[i] != weekly_bar_data[i][0]:
            weekly_bar_data.insert(i, (weekdays[i], 0))
        i += 1

    ## Location Map
    location_map_data = []
    occurences_per_location = database.get_sql_data(
        'SELECT l.label, l.latitude, l.longitude, COUNT(o.time) as amount FROM "location" l JOIN "occurence" o ON o.location_label = l.label GROUP BY l.label, l.latitude, l.longitude'
    )
    for location in occurences_per_location:
        if location[1] is not None and location[2] is not None: # Coordinates are in database
            location_map_data.append((location[1], location[2], location[3])) # Add Latitude, Longitude and Amount

    location_map = folium.Map([51.05, 3.73], zoom_start=6)
    folium.plugins.HeatMap(location_map_data).add_to(location_map)
    location_map_iframe = location_map.get_root()._repr_html_()

    return render_template("index.html", weekly_bar_data=weekly_bar_data, location_map=location_map_iframe)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """new user register page"""
    if request.method == "POST":
        pw_hash = auth._bcrypt.generate_password_hash(request.form.get("password")).decode(
            "utf-8"
        )
        new_user = models.User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=pw_hash,
            admin={"on": True, None: False}[request.form.get("admin-state")],
        )

        database.add_object(new_user)
        database.commit()
        flash("User added")
        return render_template("register.html")
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
    loc_options = util.get_location_options()
    trgt_options = []

    for occurence in models.Occurence.query.all():
        if not occurence.target in trgt_options:
            trgt_options.append(occurence.target)
    if request.method == "POST":
        try:
            time_dt = datetime.strptime(request.form.get("time"), "%Y-%m-%dT%H:%M")
            new_occurence = models.Occurence(
                time=time_dt,
                location_label=request.form.get("location"),
                target=request.form.get("target"),
                context=request.form.get("context"),
            )
            if new_occurence.location not in loc_options:
                new_location = models.Location(
                    label=new_occurence.location_label,
                    latitude=None,
                    longitude=None
                )
                database.add_object(new_location)
            database.add_object(new_occurence)
            database.commit()
            flash("Occurence added")
        except ValueError:
            flash("You need to at least fill out Time correctly")
    return render_template(
        "new_record.html", loc_options=loc_options, trgt_options=trgt_options
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
