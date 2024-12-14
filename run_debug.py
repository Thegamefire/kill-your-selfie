"""Run a debug webserver"""
from kill_your_selfie.app import app

if __name__ == "__main__":
    app.run(debug=True)
