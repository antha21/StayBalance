from datetime import date, datetime, timedelta
from app import app
from models import db, User, UserProfile, WorkoutEntry, MealEntry


def seed():
    with app.app_context():
        print("Dropping and creating tables...")
        db.drop_all()
        db.create_all()

        # ---------- USERS ----------
        user1 = User(
            email="test@staybalanced.com",
            password_hash="test123",  # TODO: hash later
            name="Test User",
            created_at=datetime.now(),
        )
        user2 = User(
            email="demo@staybalanced.com",
            password_hash="demo123",  # TODO: hash later
            name="Demo User",
            created_at=datetime.now(),
        )

        db.session.add_all([user1, user2])
        db.session.commit()
        print(f"Created users: {user1.id} (test), {user2.id} (demo)")

        # ---------- PROFILES (SURVEY DATA + GOALS) ----------
        profile1 = UserProfile(
            user_id=user1.id,
            fitness_goal="Build Muscle",
            activity_level="Active",
            diet_type="No Restrictions",
            allergies="None",
            workout_days="Mon,Wed,Fri",
            notifications_enabled=True,
            target_weight_kg=80,
            current_weight_kg=78,
            height_cm=178,
            daily_calorie_goal=2600,
            daily_protein_goal_g=150,
            daily_carb_goal_g=260,
            daily_fat_goal_g=70,
        )

        profile2 = UserProfile(
            user_id=user2.id,
            fitness_goal="Lose Weight",
            activity_level="Lightly Active",
            diet_type="No Restrictions",
            allergies="Peanuts",
            workout_days="Tue,Thu,Sat",
            notifications_enabled=False,
            target_weight_kg=65,
            current_weight_kg=72,
            height_cm=165,
            daily_calorie_goal=1900,
            daily_protein_goal_g=110,
            daily_carb_goal_g=180,
            daily_fat_goal_g=60,
        )

        db.session.add_all([profile1, profile2])
        db.session.commit()

        # ---------- WORKOUTS & MEALS FOR LAST 5 DAYS ----------
        today = date.today()

        # Helper to add workout
        def add_workout(user, day_offset, name, muscle_group,
                        sets, reps, minutes, intensity, status="completed"):
            d = today - timedelta(days=day_offset)
            w = WorkoutEntry(
                user_id=user.id,
                date=d,
                workout_name=name,
                muscle_group=muscle_group,
                sets=sets,
                reps=reps,
                duration_minutes=minutes,
                intensity=intensity,
                status=status,
            )
            db.session.add(w)

        # Helper to add meal
        def add_meal(user, day_offset, meal_type, name,
                     calories, protein, carbs, fats):
            d = today - timedelta(days=day_offset)
            m = MealEntry(
                user_id=user.id,
                date=d,
                meal_type=meal_type,
                meal_name=name,
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fats_g=fats,
            )
            db.session.add(m)

        # ---------- USER 1: Test User ----------
        # Workouts over last 5 days
        add_workout(user1, 0, "Upper Body Day", "Chest", 4, 10, 45, "Medium")
        add_workout(user1, 1, "Leg Day", "Legs", 5, 8, 50, "High")
        add_workout(user1, 3, "Cardio Session", "Full Body", 0, 0, 30, "Low", status="completed")

        # Meals over last 5 days
        # Today
        add_meal(user1, 0, "Breakfast", "Oatmeal & Berries", 400, 15, 60, 8)
        add_meal(user1, 0, "Lunch", "Chicken & Rice", 650, 45, 70, 15)
        add_meal(user1, 0, "Dinner", "Salmon & Veggies", 700, 40, 40, 30)
        add_meal(user1, 0, "Snack", "Greek Yogurt", 200, 18, 15, 4)

        # Yesterday
        add_meal(user1, 1, "Breakfast", "Eggs & Toast", 450, 25, 35, 18)
        add_meal(user1, 1, "Lunch", "Turkey Sandwich", 550, 30, 55, 12)
        add_meal(user1, 1, "Dinner", "Pasta & Meatballs", 800, 35, 90, 22)

        # 3 days ago (lighter day)
        add_meal(user1, 3, "Lunch", "Chicken Salad", 450, 35, 25, 14)
        add_meal(user1, 3, "Dinner", "Stir Fry Veggies & Tofu", 600, 28, 65, 18)

        # ---------- USER 2: Demo User ----------
        # Workouts
        add_workout(user2, 0, "Light Cardio", "Full Body", 0, 0, 25, "Low")
        add_workout(user2, 2, "Beginner Full-Body", "Full Body", 3, 12, 35, "Medium")

        # Meals
        add_meal(user2, 0, "Breakfast", "Smoothie Bowl", 350, 20, 50, 8)
        add_meal(user2, 0, "Lunch", "Grilled Chicken Wrap", 550, 35, 50, 16)
        add_meal(user2, 0, "Dinner", "Veggie Soup & Bread", 500, 18, 60, 10)

        add_meal(user2, 2, "Lunch", "Quinoa Salad", 480, 20, 55, 14)
        add_meal(user2, 2, "Dinner", "Baked Fish & Rice", 650, 40, 55, 18)

        # Commit all workouts/meals
        db.session.commit()

        # Debug summary
        meal_count = MealEntry.query.count()
        workout_count = WorkoutEntry.query.count()
        user_count = User.query.count()
        print(f"Seeding complete. Users: {user_count}, Meals: {meal_count}, Workouts: {workout_count}")


if __name__ == "__main__":
    seed()
