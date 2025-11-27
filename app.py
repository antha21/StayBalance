import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, MealEntry, WorkoutEntry, UserProfile,User
from sqlalchemy import func
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
    user = User.query.first()
    if not user:
        return render_template(
            "profile.html",
            user=None,
            profile=None,
            last_workout="—",
            meals_logged=0,
            weekly_goal_pct=None,
            achievements={}
        )

    profile = UserProfile.query.filter_by(user_id=user.id).first()
    today = date.today()
    week_ago = today - timedelta(days=6)

    # Last Workout
    last_workout_entry = (
        WorkoutEntry.query.filter_by(user_id=user.id)
        .order_by(WorkoutEntry.date.desc())
        .first()
    )
    last_workout = last_workout_entry.date if last_workout_entry else "—"

    # Meals this week
    meals_logged = (
        db.session.query(func.count(MealEntry.id))
        .filter(
            MealEntry.user_id == user.id,
            MealEntry.date >= week_ago,
            MealEntry.date <= today
        )
        .scalar()
    )

    # Weekly goal %
    workouts_week = (
        db.session.query(func.count(WorkoutEntry.id))
        .filter(
            WorkoutEntry.user_id == user.id,
            WorkoutEntry.date >= week_ago,
            WorkoutEntry.date <= today
        )
        .scalar()
    )

    workout_days = []
    if profile and profile.workout_days:
        workout_days = [d.strip().lower() for d in profile.workout_days.split(",")]

    weekly_goal = len(workout_days)
    weekly_goal_pct = None
    if weekly_goal > 0:
        weekly_goal_pct = round((workouts_week / weekly_goal) * 100)

    ## achievements calculations

    total_workouts = WorkoutEntry.query.filter_by(user_id=user.id).count()
    total_meals = MealEntry.query.filter_by(user_id=user.id).count()

    # 3-day or more streak
    workout_dates = sorted(
        [w.date for w in WorkoutEntry.query.filter_by(user_id=user.id).all()]
    )
    streak = 1
    max_streak = 1
    for i in range(1, len(workout_dates)):
        if workout_dates[i] == workout_dates[i-1] + timedelta(days=1):
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1

    
    high_intensity = (
        WorkoutEntry.query.filter_by(user_id=user.id, intensity="High").first()
        is not None
    )

    # check if you have some meals in all 3 places
    balanced_plate = (
        MealEntry.query.filter(
            MealEntry.user_id == user.id,
            MealEntry.protein_g > 0,
            MealEntry.carbs_g > 0,
            MealEntry.fats_g > 0
        ).first()
        is not None
    )

    # achievements data
    achievements = {
        "workouts_10": total_workouts >= 10,
        "meals_10": total_meals >= 10,
        "streak_3": max_streak >= 3,
        "high_intensity": high_intensity,
        "balanced_plate": balanced_plate,
    }

    return render_template(
        "profile.html",
        user=user,
        userinfo={
            "name": user.name,
            "email": user.email,
            "height": getattr(profile, "height_cm", None),
            "weight": getattr(profile, "current_weight_kg", None),
        },
        profile=profile,
        last_workout=last_workout,
        meals_logged=meals_logged,
        weekly_goal_pct=weekly_goal_pct,
        achievements=achievements,
    )

@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    user = User.query.first()
    if not user:
        flash("No user exists to edit.")
        return redirect(url_for("profile"))

    profile = UserProfile.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        # create profile if missing
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)

        # Safely update fields from form
        user.name = request.form.get("name") or user.name

        height = request.form.get("height")
        weight = request.form.get("weight")
        goal = request.form.get("goal")
        workout_days = request.form.get("workout_days")

        try:
            profile.height_cm = float(height) if height else None
        except ValueError:
            profile.height_cm = None

        try:
            profile.current_weight_kg = float(weight) if weight else None
        except ValueError:
            profile.current_weight_kg = None

        profile.fitness_goal = goal or profile.fitness_goal
        profile.workout_days = workout_days or profile.workout_days

        db.session.commit()
        return redirect(url_for("profile"))

    return render_template("profile_edit.html", user=user, profile=profile)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)