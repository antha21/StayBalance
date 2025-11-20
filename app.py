import os
from flask import Flask, render_template
from models import db

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "fitmeal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change_this_later"

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fitness")
def fitness():
    return render_template("fitness.html")

@app.route("/meals")
def meals():
    return render_template("meals.html")

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)