from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    fitness_goal = db.Column(db.String(50))
    activity_level = db.Column(db.String(50))
    diet_type = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    workout_days = db.Column(db.String(100))
    notifications_enabled = db.Column(db.Boolean, default=False)

    target_weight_kg = db.Column(db.Float)
    daily_calorie_goal = db.Column(db.Integer)
    daily_protein_goal_g = db.Column(db.Integer)
    daily_carb_goal_g = db.Column(db.Integer)
    daily_fat_goal_g = db.Column(db.Integer)

    user = db.relationship("User", backref="profile", uselist=False)


class WorkoutEntry(db.Model):
    __tablename__ = "workout_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date)
    workout_name = db.Column(db.String(100))
    muscle_group = db.Column(db.String(50))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration_minutes = db.Column(db.Integer)
    intensity = db.Column(db.String(20))
    status = db.Column(db.String(20))

    user = db.relationship("User", backref="workouts")


class MealEntry(db.Model):
    __tablename__ = "meal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date)
    meal_type = db.Column(db.String(20))  # Breakfast, Lunch, etc.
    meal_name = db.Column(db.String(100))

    calories = db.Column(db.Integer)
    protein_g = db.Column(db.Integer)
    carbs_g = db.Column(db.Integer)
    fats_g = db.Column(db.Integer)

    user = db.relationship("User", backref="meals")