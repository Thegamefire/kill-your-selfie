"""main app process"""
# pylint: disable=C0301
from datetime import datetime, timedelta

import folium
import folium.plugins
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text as sql_txt

from .config import Config
from . import models


login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
bcrypt = Bcrypt(app)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{Config.DB_USERNAME}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_DATABASE}"
)
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = Config.SECRET



with app.app_context():
    db.create_all()


def get_SQL_data(query):
    return db.session.execute(sql_txt(query)).fetchall()

def get_location_options():
    loc_options=[]
    for location in models.Location.query.all():
        if not location.label in loc_options:
            loc_options.append(location.label)
    return loc_options



@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route("/base")
def basepage():
    return render_template("base.html")


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by
    # filtering for the username
    if request.method == "POST":
        user = models.User.query.filter_by(username=request.form.get("username")).first()
        if user == None:
            flash("User with that Username doesn't exist")
        # Check if the password entered is the
        # same as the user's password
        elif bcrypt.check_password_hash(user.password, request.form.get("password")):
            # Use the login_user method to log in the user
            login_user(user, remember=True)
            return redirect( url_for('home'))
        else:
            flash("Incorrect password")
    return render_template("login.html")


@app.route("/home")
@login_required
def home():
    ### Chart Data
    ## Weekly Bar Graph
    weekly_bar_data = []
    occurences_per_day = get_SQL_data(
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
    occurences_per_location = get_SQL_data(
        'SELECT l.label, l.latitude, l.longitude, COUNT(o.time) as amount FROM "location" l JOIN "occurence" o ON o.location_label = l.label GROUP BY l.label, l.latitude, l.longitude'
    )
    for location in occurences_per_location:
        if location[1] != None and location[2] != None: # Coordinates are in database
            location_map_data.append((location[1], location[2], location[3])) # Add Latitude, Longitude and Amount

    location_map = folium.Map([51.05, 3.73], zoom_start=6)
    folium.plugins.HeatMap(location_map_data).add_to(location_map)
    location_map_iframe = location_map.get_root()._repr_html_()

    return render_template("index.html", weekly_bar_data=weekly_bar_data, location_map=location_map_iframe)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == "POST":
        pw_hash = bcrypt.generate_password_hash(request.form.get("password")).decode(
            "utf-8"
        )
        new_user = models.User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=pw_hash,
            admin={"on": True, None: False}[request.form.get("admin-state")],
        )

        db.session.add(new_user)
        db.session.commit()
        flash("User added")
        return render_template("register.html")
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/new_record", methods=["GET", "POST"])
@login_required
def new_record():
    loc_options = get_location_options()
    trgt_options = []

    for occurence in models.Occurence.query.all():
        if not occurence.target in trgt_options:
            trgt_options.append(occurence.target)
    if request.method == "POST":
        try:
            time_dt = datetime.strptime(request.form.get("time"), "%Y-%m-%dT%H:%M")
            new_occ = models.Occurence(
                time=time_dt,
                location_label=request.form.get("location"),
                target=request.form.get("target"),
                context=request.form.get("context"),
            )
            if new_occ.location not in loc_options:
                new_loc = models.Location(
                    label=new_occ.location_label,
                    latitude=None,
                    longitude=None
                )
                db.session.add(new_loc)
            db.session.add(new_occ)
            db.session.commit()
            flash("Occurence added")
        except ValueError:
            flash("You need to at least fill out Time correctly")
    return render_template(
        "new_record.html", loc_options=loc_options, trgt_options=trgt_options
    )

@app.route("/location_link", methods=["GET", "POST"])
@login_required
def location_link():
    loc_options = get_location_options()
    loc_options.sort()
    if len(loc_options) == 0:
        loc_options=[""] # Add at least one element to the list so it is iterable

    if request.method == 'POST':
        location = models.Location.query.filter_by(label=request.form.get("location")).first()
        location.latitude = float(request.form.get("latitude"))
        location.longitude = float(request.form.get("longitude"))
        db.session.commit()

    return render_template("location_link.html", loc_options = loc_options)
