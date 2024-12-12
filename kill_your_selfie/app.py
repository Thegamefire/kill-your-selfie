import psycopg2
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta


login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
bcrypt=Bcrypt(app)

print('Hash for lol =')
lol_hash = bcrypt.generate_password_hash('lol').decode('utf-8')
print(lol_hash)

load_dotenv()
db_username = os.environ.get("USER_NAME")
db_password = os.environ.get("PASSWORD")
db_host = os.environ.get("HOST")
db_port = os.environ.get("PORT")
db_database = os.environ.get('DATABASE')
secret_key = os.environ.get('SECRET')

app.config['SQLALCHEMY_DATABASE_URI']=f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = secret_key


class Occurence(db.Model):
    __tablename__ = "occurence"
    
    time = db.Column(db.TIMESTAMP, primary_key=True)
    location = db.Column(db.String(80), unique=False, nullable=True)
    target = db.Column(db.String(80), unique=False, nullable=False)
    context = db.Column(db.String(), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Occurence %r>' % self.time

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False, unique=False)
    admin = db.Column(db.Boolean, nullable=False,unique=False)
    
    def __repr__(self):
        return '<User %r>' % self.username

# # Initialize app with extension
# db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()


@app.route("/")
@app.route("/home")
def homepage():
    return render_template('index.html')

@app.route('/base')
def basepage():
    return render_template('base.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['GET','POST'])
def login():
    # If a post request was made, find the user by 
    # filtering for the username
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form.get("username")).first()
        if (user==None):
            flash("User with that Username doesn't exist")
        # Check if the password entered is the 
        # same as the user's password
        elif bcrypt.check_password_hash(user.password, request.form.get("password")):
            # Use the login_user method to log in the user
            login_user(user, remember=True)
            return redirect( url_for('homepage'))
        else:
            flash('Incorrect password')
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method=='POST':
        if current_user.admin:
            pw_hash = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
            new_user = User(
                username=request.form.get("username"),
                email=request.form.get("email"),
                password=pw_hash,
                admin={'on':True,None:False}[request.form.get('admin-state')]
            )

            db.session.add(new_user)
            db.session.commit()
            flash('User added')
            return render_template('register.html')
        else:
            flash('Login as admin to register new users')
    return render_template("register.html")
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))



@app.route("/new_record", methods=['GET', 'POST'])
@login_required
def new_record():
    loc_options = []
    trgt_options = []
    for occurence in Occurence.query.all():
        if not occurence.location in loc_options:
            loc_options.append(occurence.location)
        if not occurence.target in trgt_options:
            trgt_options.append(occurence.target)
    if request.method=='POST':
        try:
            time_dt = datetime.strptime(request.form.get('time'), "%Y-%m-%dT%H:%M")
            new_occ = Occurence(
                time=time_dt,
                location=request.form.get('location'),
                target=request.form.get('target'),
                context=request.form.get('context')
                )
            db.session.add(new_occ)
            db.session.commit()
            flash('Occurence added')
        except ValueError:
            flash('You need to at least fill out Time correctly')
    return render_template("new_record.html", loc_options=loc_options, trgt_options=trgt_options)

if __name__ == '__main__':  
   app.run(debug=True)
