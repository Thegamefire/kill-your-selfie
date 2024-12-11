import psycopg2
import os
from dotenv import load_dotenv
from flask import Flask, render_template

app = Flask(__name__)

load_dotenv()
db_username = os.environ.get("USER_NAME")
db_password = os.environ.get("PASSWORD")
db_host = os.environ.get("HOST")
db_port = os.environ.get("PORT")
db_database = os.environ.get('DATABASE')

@app.route("/")
def homepage():
    return render_template('index.html')

if __name__ == '__main__':  
   app.run()