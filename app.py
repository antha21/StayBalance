import os
from flask import Flask, render_template
from models import db
from sqlalchemy import func

from models import db, MealEntry, WorkoutEntry, UserProfile
from datetime import date, timedelta

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
    user_id = 1

    if not user_id:
        # Later: redirect to login or show message
        return render_template("stats.html", no_user=True)

    today = date.today()
    week_ago = today - timedelta(days=6)  # last 7 days inclusive

    # ---- Daily calories/macros (today) ----
    today_meals = (
        db.session.query(
            func.coalesce(func.sum(MealEntry.calories), 0),
            func.coalesce(func.sum(MealEntry.protein_g), 0),
            func.coalesce(func.sum(MealEntry.carbs_g), 0),
            func.coalesce(func.sum(MealEntry.fats_g), 0),
        )
        .filter(MealEntry.user_id == user_id, MealEntry.date == today)
        .one()
    )
    calories_today, protein_today, carbs_today, fats_today = today_meals

    # ---- Workout stats (last 7 days) ----
    workouts_last_week = (
        db.session.query(func.count(WorkoutEntry.id))
        .filter(
            WorkoutEntry.user_id == user_id,
            WorkoutEntry.date >= week_ago,
            WorkoutEntry.date <= today,
        )
        .scalar()
    )

    workout_minutes_last_week = (
        db.session.query(func.coalesce(func.sum(WorkoutEntry.duration_minutes), 0))
        .filter(
            WorkoutEntry.user_id == user_id,
            WorkoutEntry.date >= week_ago,
            WorkoutEntry.date <= today,
        )
        .scalar()
    )

    # ---- Meals last 7 days (for table) ----
    recent_meals = (
        MealEntry.query
        .filter(
            MealEntry.user_id == user_id,
            MealEntry.date >= week_ago,
            MealEntry.date <= today,
        )
        .order_by(MealEntry.date.desc())
        .all()
    )

    # ---- Recent workouts (for table) ----
    recent_workouts = (
        WorkoutEntry.query
        .filter(
            WorkoutEntry.user_id == user_id,
            WorkoutEntry.date >= week_ago,
            WorkoutEntry.date <= today,
        )
        .order_by(WorkoutEntry.date.desc())
        .all()
    )

    # ---- Target goals (for comparison, optional) ----
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    return render_template(
        "stats.html",
        calories_today=calories_today,
        protein_today=protein_today,
        carbs_today=carbs_today,
        fats_today=fats_today,
        workouts_last_week=workouts_last_week,
        workout_minutes_last_week=workout_minutes_last_week,
        recent_meals=recent_meals,
        recent_workouts=recent_workouts,
        profile=profile,
        today=today,
        week_ago=week_ago,
    )

@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)