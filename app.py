import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, MealEntry, WorkoutEntry, UserProfile,User
from sqlalchemy import func
from datetime import date, timedelta, datetime, time

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SESSION_PERMANENT"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "fitmeal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change_this_later"

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fitness", methods=["POST", "GET"])
def fitness():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    user_id = targetId
    workouts = (
        db.session.query(WorkoutEntry)
        .filter(WorkoutEntry.user_id == user_id)
        .order_by(WorkoutEntry.date.asc())
        .all()
    )

    today = date.today()

    workout_mins = (
        db.session.query(
            func.coalesce(func.sum(WorkoutEntry.duration_minutes), 0)
        )
        .filter(WorkoutEntry.user_id == user_id, WorkoutEntry.date == today)
        .one()
    )

    dates = []
    result = []
    for workout in workouts:
        if workout.date not in dates:
            dates.append(workout.date)
            date_index = dates.index(workout.date)
            result.insert(date_index, {
                "day_of_week": workout.date.strftime("%a").capitalize(),
                "day":workout.date.strftime("%d"),
                "month": workout.date.strftime("%b"),
                "workouts": []
            })
        date_index = dates.index(workout.date)
        result[date_index].get("workouts").append(workout)

    current_time = datetime.now().time()
    greeting = "Good evening."
    if current_time < time(4, 00):
        greeting = "Good night."
    elif current_time < time(12, 00):
        greeting = "Good morning."
    elif current_time < time(19, 00):
        greeting = "Good afternooon"


    
    return render_template("fitness.html", 
        dates = result,
        greeting = greeting,
        workout_mins = workout_mins[0]
    )

@app.route("/fitness/edit", methods=["POST", "GET"])
def edit_workout():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    user_id = targetId
    if request.method == "GET":
        workout = db.session.query(WorkoutEntry).filter(WorkoutEntry.user_id == user_id, WorkoutEntry.id == request.args.get("workout")).one_or_none()
        if workout != None:
            session["edit_query"] = workout.id
        else:
            session["edit_query"] = None
        return render_template("workoutform.html", workout=workout)
        
    if request.method == "POST":
        if (request.form.get("date") == None):
            old = db.session.query(WorkoutEntry).filter(WorkoutEntry.user_id == user_id, WorkoutEntry.id == session["edit_query"]).one_or_none()
            
            if (old != None):
                db.session.delete(old)
                db.session.commit()
                return redirect(url_for("fitness", success = True))

        old = db.session.query(WorkoutEntry).filter(WorkoutEntry.user_id == user_id, WorkoutEntry.id == session["edit_query"]).one_or_none()
        status = "in progress..."
        if (old != None):
            db.session.delete(old)
            status = old.status
        
        db.session.add(WorkoutEntry(
            user_id=user_id,
            date= datetime.strptime(request.form.get("date"),"%Y-%m-%d"),
            workout_name=request.form.get("workout_name"),
            muscle_group=request.form.get("muscle_group"),
            sets=request.form.get("sets"),
            reps=request.form.get("reps"),
            duration_minutes=request.form.get("duration_minutes"),
            intensity=request.form.get("intensity"),
            status=status,
        ))
        db.session.commit()
        return redirect(url_for("fitness", success = True))
    return render_template("workoutform.html")

@app.route("/meals", methods=["POST", "GET"])
def meals():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    user_id = targetId
    query = (
        db.session.query(MealEntry)
        .filter(MealEntry.user_id == user_id)
        .order_by(MealEntry.date.asc())
        .all()
    )

    
    today = date.today()

    calorie_count = (
        db.session.query(
            func.coalesce(func.sum(MealEntry.calories), 0)
        )
        .filter(MealEntry.user_id == user_id, MealEntry.date == today)
        .one()
    )

    dates = []
    result = []
    for meal in query:
        if meal.date not in dates:
            dates.append(meal.date)
            date_index = dates.index(meal.date)
            result.insert(date_index, {
                "day_of_week": meal.date.strftime("%a").capitalize(),
                "day":meal.date.strftime("%d"),
                "month": meal.date.strftime("%b"),
                "meals": []
            })
        date_index = dates.index(meal.date)
        result[date_index].get("meals").append(meal)

    current_time = datetime.now().time()
    greeting = "Good evening."
    if current_time < time(4, 00):
        greeting = "Good night."
    elif current_time < time(12, 00):
        greeting = "Good morning."
    elif current_time < time(19, 00):
        greeting = "Good afternooon"


    
    return render_template("meals.html", 
        dates = result,
        greeting = greeting,
        calorie_count = calorie_count[0]
    )

# @app.route("/meals/edit", methods=["POST", "GET"])
# def new_meal():
#     user_id = 1
#     if request.method == "GET":
#         meal = db.session.query(MealEntry).filter(MealEntry.user_id == user_id, MealEntry.id == request.args.get("meal")).one()
#         return render_template("mealform.html", meal=meal)
#     return render_template("mealform.html")

@app.route("/meals/edit", methods=["POST", "GET"])
def new_meal():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    user_id = targetId
    if request.method == "GET":
        meal = db.session.query(MealEntry).filter(MealEntry.user_id == user_id, MealEntry.id == request.args.get("meal")).one_or_none()
        if meal != None:
            session["edit_query"] = meal.id
        else:
            session["edit_query"] = None
        return render_template("mealform.html", meal=meal)
        
    if request.method == "POST":
        if (request.form.get("date") == None):
            old = db.session.query(MealEntry).filter(MealEntry.user_id == user_id, MealEntry.id == session["edit_query"]).one_or_none()
            
            if (old != None):
                db.session.delete(old)
                db.session.commit()
                return redirect(url_for("meals", success = True))

        old = db.session.query(MealEntry).filter(MealEntry.user_id == user_id, MealEntry.id == session["edit_query"]).one_or_none()
        
        if (old != None):
            db.session.delete(old)
        
        db.session.add(MealEntry(
            user_id=user_id,
                date=datetime.strptime(request.form.get("date"),"%Y-%m-%d"),
                meal_type=request.form.get("meal_type"),
                meal_name=request.form.get("meal_name"),
                calories=request.form.get("calories"),
                protein_g=request.form.get("protein_g"),
                carbs_g=request.form.get("carbs_g"),
                fats_g=request.form.get("fats_g")
        ))
        db.session.commit()
        return redirect(url_for("meals", success = True))
    return render_template("mealform.html")

@app.route("/stats")
def stats():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    user_id = targetId

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
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
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
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("login"))

    user = User.query.filter(
        User.id == targetId
    ).first()
    # user = User.query.first()
    if not user:
        # flash("No user exists to edit.")
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

@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "GET":
        
        # print(session)
        try:
            if not (session["user_id"] is None):
                return redirect(url_for("profile"))
        except:
            print("User has not logged in.")

        return render_template("login.html")

    username = request.form.get("username")
    passwd = request.form.get("password")

    user = User.query.filter(
        ((User.email == username) | (User.name == username)) & (User.password_hash == passwd) # 100% secure login 👍
    ).first()

    if not (user is None):
        session["user_id"] = user.id
        return redirect(url_for("profile"))

    return redirect(url_for("login"))

@app.route("/logout",methods=["GET"])
def logout():
    session.pop("user_id",None)
    return redirect(url_for("login"))

@app.route("/survey", methods=["GET", "POST"])
def survey():
    targetId = None
    try:
        if (session["user_id"]):
            targetId = session["user_id"]
    except:
        return redirect(url_for("signup"))

    user = User.query.filter(
        User.id == targetId
    ).first()

    # print(user)
    userProfile = UserProfile.query.filter(
        UserProfile.user_id == targetId
    ).first()

    # print(userProfile)

    if request.method == "POST":
        # later: save to DB
        # print(userProfile)
        # print(request.form.get("activity_level"))
        userProfile.activity_level = request.form.get("activity_level")
        # print(request.form.get("fitness_goal"))
        userProfile.fitness_goal = request.form.get("fitness_goal")
        

        # print(request.form.getlist("dietary_restrictions"))
        userProfile.allergies = "None"
        userProfile.diet_type = ""
        for item in request.form.getlist("dietary_restrictions"):
            userProfile.diet_type += item+","
            if (item in ["Gluten-Free","Dairy-Free","Nut Allergy"]):
                if (userProfile.allergies == "None"):
                    userProfile.allergies = item+","
                else:
                    userProfile.allergies += item+","

        
        userProfile.current_weight_kg = float(request.form.get("current_weight_kg")) if request.form.get("current_weight_kg") else 0
        userProfile.target_weight_kg = float(request.form.get("target_weight_kg")) if request.form.get("target_weight_kg") else 0
        userProfile.height_cm = float(request.form.get("height_cm")) if request.form.get("height_cm") else 0

        # --- Nutrition Goals ---
        userProfile.daily_calorie_goal = int(request.form.get("daily_calorie_goal")) if request.form.get("daily_calorie_goal") else 0
        userProfile.daily_protein_goal_g = int(request.form.get("daily_protein_goal_g")) if request.form.get("daily_protein_goal_g") else 0
        userProfile.daily_carb_goal_g = int(request.form.get("daily_carb_goal_g")) if request.form.get("daily_carb_goal_g") else 0
        userProfile.daily_fat_goal_g = int(request.form.get("daily_fat_goal_g")) if request.form.get("daily_fat_goal_g") else 0

        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("survey.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    Email = request.form.get("username")
    passwd = request.form.get("password")
    name = request.form.get("name")

    user3 = User(
        email=Email,
        password_hash=passwd,  # TODO: hash later
        name=name,
        created_at=datetime.now(),
    )    

    try:
        db.session.add(user3)
        db.session.commit()      
    except:
        # flash("Email already exists...")
        return redirect(url_for("signup"))

    profile = UserProfile(
        user_id = user3.id,
        fitness_goal="...",
        activity_level="...",
        diet_type="...",
        allergies="...",
        workout_days="None",
        notifications_enabled=False,
        target_weight_kg=0,
        current_weight_kg=0,
        height_cm=0,
        daily_calorie_goal=0,
        daily_protein_goal_g=0,
        daily_carb_goal_g=0,
        daily_fat_goal_g=0,
    )
    db.session.add(profile)
    db.session.commit()

    session["user_id"] = user3.id
    return redirect(url_for("survey"))

@app.route("/forgot",methods=["GET","POST"])
def forgot():
    session.pop('_flashes', None)
    if request.method == "GET":
        return render_template("forgot.html")

    got = request.form.get("username")

    usernameRequest = "User does not exist."
    try:
        userTemp = User.query.filter(
            (User.email == got) | (User.name == got)
        ).first()
    except Exception as e:
        print(e)
        return redirect(url_for("forgot"))

    if not (userTemp is None):
        flash("Password:"+str(userTemp.password_hash))
        # return redirect(url_for("login"))

    return render_template("forgot.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)