import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='24#2006',
            charset='utf8'
        )
        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the database already exists
            cursor.execute("SHOW DATABASES LIKE 'fitness_tracker'")
            result = cursor.fetchone()
            if not result:
                # Create the database only if it doesn't exist
                cursor.execute("CREATE DATABASE fitness_tracker")

            # Connect to the existing database
            connection.database = "fitness_tracker"

            # Create tables if they don't exist
            create_tables(connection)

            return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return None


def create_tables(connection):
    cursor = connection.cursor()

    # First check if daily_calorie_goal column exists in users table
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns 
            WHERE table_name = 'users'
            AND column_name = 'daily_calorie_goal'
        """)
        column_exists = cursor.fetchone()[0]
        
        # Add the column if it doesn't exist
        if not column_exists:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN daily_calorie_goal INT DEFAULT 2000
            """)
            connection.commit()
    except Error as e:
        print(f"Error checking/adding column: {e}")
    
    # Create users table
    try: 
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                age INT NOT NULL,
                weight FLOAT NOT NULL,
                height FLOAT NOT NULL,
                goal VARCHAR(50) NOT NULL,
                is_vegetarian BOOLEAN NOT NULL,
                daily_calorie_goal INT DEFAULT 2000
                )
            """)
    except Error as e:
        print(f"Error creating 'users' table: {e}")
    
    # Create workouts table
    cursor.execute("SHOW TABLES LIKE 'workouts'")
    result = cursor.fetchone()
    if not result:
        try:
            cursor.execute("""
                CREATE TABLE workouts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    exercise VARCHAR(255) NOT NULL,
                    sets INT NOT NULL,
                    reps INT NOT NULL,
                    weight FLOAT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        except Error as e:
            print(f"Error creating 'workouts' table: {e}")

    # Create calories table
    cursor.execute("SHOW TABLES LIKE 'calorie_tracker'")
    result = cursor.fetchone()
    if not result:
        try:
            cursor.execute("""
                CREATE TABLE calorie_tracker (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    food_item VARCHAR(255) NOT NULL,
                    calories INT NOT NULL,
                    meal_type VARCHAR(50) NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        except Error as e:
            print(f"Error creating 'calorie_tracker' table: {e}")
    
    connection.commit()

def calculate_bmi(weight, height):
    try:
        weight = float(weight)
        height = float(height) / 100
        bmi = weight / (height ** 2)
        if bmi <= 0 or bmi >= 50:
            return None
        return round(bmi, 2)
    except ValueError:
        return None

def recommend_exercises(goal, age):
    if age <= 30:
        if goal == "Lose Weight":
            return ["Running", "HIIT", "Swimming", "Kickboxing", "Jump Rope", "Zumba", "Mountain Climbers", "Spinning", "Burpees", "Rowing"]
        elif goal == "Build Muscle":
            return ["Weightlifting", "Bodyweight Exercises", "Squats", "Deadlifts", "Pull-ups", "Bench Press", "Lunges", "Dumbbell Rows", "Overhead Press", "Chest Fly"]
        elif goal == "Improve Endurance":
            return ["Long-distance Running", "Cycling", "Rowing", "Swimming", "Boxing", "Trail Running", "Interval Training", "Speed Skating", "Cross-country Skiing", "Aerobic Dancing"]
       

    elif 31 <= age <= 50:
        if goal == "Lose Weight":
            return ["Brisk Walking", "Running", "Cycling", "Circuit Training", "Elliptical Training", "Dance Workouts", "Yoga", "Stepper Workouts", "Resistance Band Training", "Aerobic Kickboxing"]
        elif goal == "Build Muscle":
            return ["Strength Training", "Pilates", "Resistance Bands", "Kettlebell Workouts", "Push-ups", "Planks", "Chin-ups", "Incline Dumbbell Press", "Cable Workouts", "Deadlifts"]
        elif goal == "Improve Endurance":
            return ["Hiking", "Cycling", "Swimming", "Low-Impact Aerobics", "Rowing Machine", "Stair Climbing", "Elliptical Workouts", "Endurance Yoga", "Speed Walking", "CrossFit"]
       
    

    else:
        if goal == "Lose Weight":
            return ["Walking", "Chair Yoga", "Balance Exercises", "Meditation", "Water Aerobics", "Light Dancing", "Stretching", "Slow Cycling", "Gentle Pilates", "Resistance Band Exercises"]
        elif goal == "Build Muscle":
            return ["Light Resistance Training", "Chair-Based Exercises", "Leg Raises", "Wall Push-ups", "Seated Dumbbell Exercises", "Core Strengthening", "Wrist Curls", "Ankle Weight Exercises", "Elastic Band Workouts", "Modified Squats"]
        elif goal == "Improve Endurance":
            return ["Water Exercises", "Walking", "Tai Chi", "Chair-Based Exercises", "Stretching Routines", "Breathing Exercises", "Balance Workouts", "Light Jogging", "Step-ups", "Slow Dancing"]
        
    return []

def recommend_diet(goal, age, veg):
    if age < 18:
        if veg:
            return "Young individuals need a balanced diet: include milk, paneer, lentils, nuts, fresh fruits, whole grains, and green vegetables."
        else:
            return "Young individuals need proteins and fats: include eggs, chicken, fish, dairy products, healthy oils, and lean meats."
    elif 18 <= age < 40:
        if veg:
            if goal == "Lose Weight":
                return "Low-calorie diet: vegetables, legumes, quinoa, avoid processed carbs, include chia seeds, and oats."
            elif goal == "Build Muscle":
                return "High protein: tofu, paneer, nuts, seeds, whole grains, chickpeas, and lentils."
            elif goal == "Improve Endurance":
                return "Carbs and protein: brown rice, oats, lentils, sweet potatoes, and bananas."
           
        else:
            if goal == "Lose Weight":
                return "Lean proteins: fish, chicken, eggs, lots of vegetables, low-fat yogurt, and berries."
            elif goal == "Build Muscle":
                return "High-protein: eggs, chicken, turkey, fatty fish like salmon, bone broth, and quinoa."
            elif goal == "Improve Endurance":
                return "Complex carbs: sweet potatoes, lean meat, green vegetables, avocado, and nuts."
            
    elif age >= 40:
        if veg:
            if goal == "Lose Weight":
                return "Fiber-rich diet: leafy greens, whole grains, avoid fried food, add flaxseeds, and eat apples."
            elif goal == "Build Muscle":
                return "Light protein: tofu, beans, sprouts, low-fat dairy, almond butter, and lentils."
            elif goal == "Improve Endurance":
                return "Antioxidants: berries, nuts, whole grains, lentils, dark chocolate, and spinach."
           
        else:
            if goal == "Lose Weight":
                return "Focus on lean meat and lots of fiber: fish, chicken, vegetables, clear soups, and apples."
            elif goal == "Build Muscle":
                return "Moderate protein: fish, chicken, eggs, legumes, Greek yogurt, and quinoa."
            elif goal == "Improve Endurance":
                return "Healthy fats and carbs: fish, nuts, oats, olive oil, and avocados."
            

    return "No specific recommendation. Ensure a balanced diet with regular exercise."


class FitnessTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personalized Workout Tracker")
        self.root.geometry("500x800")
        self.root.config(bg="#f4f4f9")
        
        self.connection = create_database_connection()
        if not self.connection:
            messagebox.showerror("Error", "Could not connect to database")
            self.root.destroy()
            return
            
        self.current_user = None
        self.setup_gui()

    def setup_gui(self):
        # Create main container frames
        button_frame = tk.Frame(self.root, bg="#f4f4f9")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        # Left button frame
        left_frame = tk.Frame(button_frame, bg="#f4f4f9")
        left_frame.pack(side="left", padx=10)
        
        # Right button frame
        right_frame = tk.Frame(button_frame, bg="#f4f4f9")
        right_frame.pack(side="right", padx=10)
        
        # Data display frame
        data_frame = tk.Frame(self.root, bg="#f4f4f9")
        data_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Left side buttons
        create_profile_button = tk.Button(left_frame, text="Create Profile", command=self.create_profile_window,
                                        font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=10, pady=5)
        create_profile_button.pack(pady=5)
        
        switch_profile_button = tk.Button(left_frame, text="Switch Profile", command=self.switch_profile_window,
                                        font=("Helvetica", 12), bg="#FF9800", fg="white", relief="flat", padx=10, pady=5)
        switch_profile_button.pack(pady=5)
        
        update_profile_button = tk.Button(left_frame, text="Update Profile", command=self.update_profile_window,
                                        font=("Helvetica", 12), bg="#2196F3", fg="white", relief="flat", padx=10, pady=5)
        update_profile_button.pack(pady=5)
        
        log_workout_button = tk.Button(left_frame, text="Log Workout", command=self.log_workout_window,
                                     font=("Helvetica", 12), bg="#FF5722", fg="white", relief="flat", padx=10, pady=5)
        log_workout_button.pack(pady=5)
        
        # Right side buttons
        view_workouts_button = tk.Button(right_frame, text="View Workouts", command=self.display_workouts,
                                       font=("Helvetica", 12), bg="#1034a6", fg="white", relief="flat", padx=10, pady=5)
        view_workouts_button.pack(pady=5)
        
        log_calories_button = tk.Button(right_frame, text="Log Calories", command=self.log_calories_window,
                                      font=("Helvetica", 12), bg="#E91E63", fg="white", relief="flat", padx=10, pady=5)
        log_calories_button.pack(pady=5)
        
        view_calories_button = tk.Button(right_frame, text="View Calorie History", command=self.display_calories,
                                       font=("Helvetica", 12), bg="#673AB7", fg="white", relief="flat", padx=10, pady=5)
        view_calories_button.pack(pady=5)
        
        # Data display section at the bottom
        self.profile_label = tk.Label(data_frame, text="Profile info will be shown here.",
                                    font=("Helvetica", 15), bg="#f4f4f9", fg="#000080")
        self.profile_label.pack(pady=10)
        
        self.bmi_label = tk.Label(data_frame, text="BMI info will be displayed here.",
                                 font=("Helvetica", 15), bg="#f4f4f9", fg="#000080")
        self.bmi_label.pack(pady=10)
        
        self.recommendations_label = tk.Label(data_frame, text="Diet and Exercise recommendations will be shown here.",
                                            font=("Helvetica", 15), bg="#f4f4f9", wraplength=350, fg="#000080")
        self.recommendations_label.pack(pady=10)
    def update_profile_window(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return

        self.update_window = tk.Toplevel(self.root)
        self.update_window.title("Update Profile")
        self.update_window.geometry("500x800")
        self.update_window.config(bg="#f4f4f9")

        tk.Label(self.update_window, text="Update Profile", font=("Helvetica", 16, "bold"), bg="#f4f4f9").pack(pady=20)

        tk.Label(self.update_window, text="Age:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.update_age_entry = tk.Entry(self.update_window, font=("Helvetica", 12))
        self.update_age_entry.insert(0, str(self.current_user['age']))
        self.update_age_entry.pack(pady=5)

        tk.Label(self.update_window, text="Weight (kg):", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.update_weight_entry = tk.Entry(self.update_window, font=("Helvetica", 12))
        self.update_weight_entry.insert(0, str(self.current_user['weight']))
        self.update_weight_entry.pack(pady=5)

        tk.Label(self.update_window, text="Height (cm):", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.update_height_entry = tk.Entry(self.update_window, font=("Helvetica", 12))
        self.update_height_entry.insert(0, str(self.current_user['height']))
        self.update_height_entry.pack(pady=5)

        tk.Label(self.update_window, text="Fitness Goal:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=5)
        self.update_goal_var = tk.StringVar(value=self.current_user['goal'])
        goal_options = ["Lose Weight", "Build Muscle", "Improve Endurance"]
        goal_menu = tk.OptionMenu(self.update_window, self.update_goal_var, *goal_options)
        goal_menu.config(font=("Helvetica", 12))
        goal_menu.pack(pady=5)

        self.update_veg_var = tk.BooleanVar(value=self.current_user['is_vegetarian'])
        veg_checkbox = tk.Checkbutton(self.update_window, text="Vegetarian", 
                                 variable=self.update_veg_var, bg="#f4f4f9",
                                 font=("Helvetica", 12))
        veg_checkbox.pack(pady=5)

        tk.Label(self.update_window, text="Daily Calorie Goal:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.update_calorie_goal_entry = tk.Entry(self.update_window, font=("Helvetica", 12))
        self.update_calorie_goal_entry.insert(0, str(self.current_user['daily_calorie_goal']))
        self.update_calorie_goal_entry.pack(pady=5)

        tk.Button(self.update_window, text="Update Profile", command=self.update_profile,
              font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10).pack(pady=20)

    def update_profile(self):
        try:
            age = int(self.update_age_entry.get())
            weight = float(self.update_weight_entry.get())
            height = float(self.update_height_entry.get())
            goal = self.update_goal_var.get()
            is_vegetarian = self.update_veg_var.get()
            daily_calorie_goal = int(self.update_calorie_goal_entry.get())

            if age <= 0 or age > 100 or weight <= 0 or height <= 0 or daily_calorie_goal <= 0 or daily_calorie_goal > 3500:
                raise ValueError("Invalid input values")

            cursor = self.connection.cursor()
            cursor.execute("""
            UPDATE users 
            SET age = %s, weight = %s, height = %s, goal = %s, 
                is_vegetarian = %s, daily_calorie_goal = %s
            WHERE id = %s
            """, (age, weight, height, goal, is_vegetarian, daily_calorie_goal, self.current_user['id']))
        
            self.connection.commit()
        
        # Update current_user with new values
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (self.current_user['id'],))
            self.current_user = cursor.fetchone()
        
            self.update_profile_display()
            self.update_window.destroy()
            messagebox.showinfo("Success", "Profile updated successfully!")

        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid values for all fields")
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    

    def create_profile_window(self):
        self.profile_window = tk.Toplevel(self.root)
        self.profile_window.title("Create Profile")
        self.profile_window.geometry("500x800")
        self.profile_window.config(bg="#f4f4f9")

        tk.Label(self.profile_window, text="Name:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.name_entry = tk.Entry(self.profile_window, font=("Helvetica", 12))
        self.name_entry.pack(pady=5)

        tk.Label(self.profile_window, text="Age:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.age_entry = tk.Entry(self.profile_window, font=("Helvetica", 12))
        self.age_entry.pack(pady=5)

        tk.Label(self.profile_window, text="Weight (kg):", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.weight_entry = tk.Entry(self.profile_window, font=("Helvetica", 12))
        self.weight_entry.pack(pady=5)

        tk.Label(self.profile_window, text="Height (cm):", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.height_entry = tk.Entry(self.profile_window, font=("Helvetica", 12))
        self.height_entry.pack(pady=5)

        tk.Label(self.profile_window, text="Fitness Goal:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=5)
        self.goal_var = tk.StringVar(value="Lose Weight")
        goal_options = ["Lose Weight", "Build Muscle", "Improve Endurance"]
        goal_menu = tk.OptionMenu(self.profile_window, self.goal_var, *goal_options)
        goal_menu.config(font=("Helvetica", 12))
        goal_menu.pack(pady=5)

        self.veg_var = tk.BooleanVar()
        tk.Label(self.profile_window, font=("Helvetica", 12), bg="#f4f4f9").pack(pady=5)
        veg_checkbox = tk.Checkbutton(self.profile_window, text="Check for Vegetarian",font=("Helvetica", 12),
                                    variable=self.veg_var, bg="#f4f4f9",)
        veg_checkbox.pack(pady=5)

        tk.Label(self.profile_window, text="Daily Calorie Goal:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.calorie_goal_entry = tk.Entry(self.profile_window, font=("Helvetica", 12))
        self.calorie_goal_entry.insert(0, "2000")  # Default value
        self.calorie_goal_entry.pack(pady=5)

        tk.Button(self.profile_window, text="Create Profile", command=self.create_profile,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10).pack(pady=20)
        
        
    def create_profile(self):
        username = self.name_entry.get()
        try:
            age = int(self.age_entry.get())
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            goal = self.goal_var.get()
            is_vegetarian = self.veg_var.get()
            daily_calorie_goal = int(self.calorie_goal_entry.get())

            if not username or age <= 0 or age > 100 or weight <= 0 or height <= 0 or daily_calorie_goal <= 0 or daily_calorie_goal>3500:
                raise ValueError("Invalid input values")

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO users (username, age, weight, height, goal, is_vegetarian, daily_calorie_goal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, age, weight, height, goal, is_vegetarian, daily_calorie_goal))
            
            self.connection.commit()
            
            # Fetch the newly created user
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            self.current_user = cursor.fetchone()
            
            self.update_profile_display()
            self.profile_window.destroy()
            messagebox.showinfo("Success", "Profile created successfully!")

        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid values for all fields")
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            
    def log_calories_window(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return

        self.calories_window = tk.Toplevel(self.root)
        self.calories_window.title("Log Calories")
        self.calories_window.geometry("400x400")
        self.calories_window.config(bg="#f4f4f9")

        tk.Label(self.calories_window, text="Food Item:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.food_entry = tk.Entry(self.calories_window, font=("Helvetica", 12))
        self.food_entry.pack(pady=5)

        tk.Label(self.calories_window, text="Calories:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.calories_entry = tk.Entry(self.calories_window, font=("Helvetica", 12))
        self.calories_entry.pack(pady=5)

        tk.Label(self.calories_window, text="Meal Type:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.meal_type_var = tk.StringVar(value="Breakfast")
        meal_options = ["Breakfast", "Lunch", "Dinner", "Snack"]
        meal_menu = tk.OptionMenu(self.calories_window, self.meal_type_var, *meal_options)
        meal_menu.config(font=("Helvetica", 12))
        meal_menu.pack(pady=5)

        tk.Button(self.calories_window, text="Log Calories", command=self.log_calories,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10).pack(pady=20)

    def log_calories(self):
        try:
            food_item = self.food_entry.get()
            calories = int(self.calories_entry.get())
            meal_type = self.meal_type_var.get()

            if not food_item or calories <= 0:
                raise ValueError("Invalid input values")

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO calorie_tracker (user_id, food_item, calories, meal_type)
                VALUES (%s, %s, %s, %s)
            """, (self.current_user['id'], food_item, calories, meal_type))
            
            self.connection.commit()
            self.calories_window.destroy()
            messagebox.showinfo("Success", "Calories logged successfully!")

        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid values for all fields")
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def display_calories(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return

        calories_window = tk.Toplevel(self.root)
        calories_window.title("Calorie History")
        calories_window.geometry("800x400")
        calories_window.config(bg="#f4f4f9")

        # Create a frame for the calorie entries
        calories_frame = tk.Frame(calories_window, bg="#f4f4f9")
        calories_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add title and daily goal
        tk.Label(calories_frame, text=f"Daily Calorie Goal: {self.current_user['daily_calorie_goal']}",
                font=("Helvetica", 16, "bold"), bg="#f4f4f9").pack(pady=10)

        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get today's total calories
            cursor.execute("""
                SELECT SUM(calories) as total_calories
                FROM calorie_tracker
                WHERE user_id = %s AND DATE(date) = CURDATE()
            """, (self.current_user['id'],))
            
            total_result = cursor.fetchone()
            total_calories = total_result['total_calories'] or 0
            
            tk.Label(calories_frame, text=f"Today's Total: {total_calories} calories",
                    font=("Helvetica", 14), bg="#f4f4f9").pack(pady=5)

            # Get detailed calorie entries
            cursor.execute("""
                SELECT food_item, calories, meal_type, date
                FROM calorie_tracker
                WHERE user_id = %s
                ORDER BY date DESC
            """, (self.current_user['id'],))
            
            entries = cursor.fetchall()

            if not entries:
                tk.Label(calories_frame, text="No calorie entries logged yet",
                        font=("Helvetica", 12), bg="#f4f4f9").pack(pady=20)
                return

            # Create headers
            headers_frame = tk.Frame(calories_frame, bg="#f4f4f9")
            headers_frame.pack(fill=tk.X, pady=10)
            
            headers = ["Date", "Food Item", "Calories", "Meal Type"]
            for header in headers:
                tk.Label(headers_frame, text=header, font=("Helvetica", 12, "bold"),
                        bg="#f4f4f9", width=15).pack(side=tk.LEFT, padx=5)

            # Create scrollable frame for entries
            canvas = tk.Canvas(calories_frame, bg="#f4f4f9")
            scrollbar = tk.Scrollbar(calories_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f4f4f9")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Add entries
            for entry in entries:
                entry_frame = tk.Frame(scrollable_frame, bg="#f4f4f9")
                entry_frame.pack(fill=tk.X, pady=2)
                
                date_str = entry['date'].strftime("%Y-%m-%d %H:%M")
                tk.Label(entry_frame, text=date_str, font=("Helvetica", 11),
                        bg="#f4f4f9", width=15).pack(side=tk.LEFT, padx=5)
                tk.Label(entry_frame, text=entry['food_item'], font=("Helvetica", 11),
                        bg="#f4f4f9", width=15).pack(side=tk.LEFT, padx=5)
                tk.Label(entry_frame, text=str(entry['calories']), font=("Helvetica", 11),
                        bg="#f4f4f9", width=15).pack(side=tk.LEFT, padx=5)
                tk.Label(entry_frame, text=entry['meal_type'], font=("Helvetica", 11),
                        bg="#f4f4f9", width=15).pack(side=tk.LEFT, padx=5)

            # Pack the canvas and scrollbar
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            
    def get_user_by_username(self, username):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

    def update_profile_display(self):
        if self.current_user:
            
            try:
                # Fetch the latest user data to ensure we have all fields
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE id = %s", (self.current_user['id'],))
                self.current_user = cursor.fetchone()
                
                # now update the display
                bmi = calculate_bmi(self.current_user['weight'], self.current_user['height'])
                exercise_recommendations = recommend_exercises(self.current_user['goal'], self.current_user['age'])
                diet_recommendations = recommend_diet(self.current_user['goal'], self.current_user['age'], 
                                                   self.current_user['is_vegetarian'])

                # Update profile label with all information including calorie goal
                profile_text = (f"Name: {self.current_user['username']}\n"
                              f"Age: {self.current_user['age']}\n"
                              f"Weight: {self.current_user['weight']}\n"
                              f"Height: {self.current_user['height']}\n"
                              f"Goal: {self.current_user['goal']}\n"
                              f"Daily Calorie Goal: {self.current_user.get('daily_calorie_goal', 2000)}")
                
                self.profile_label.config(text=profile_text)

                # update other lables
                if bmi:
                    if bmi >= 50:
                        self.bmi_label.config(text="Invalid BMI data. Please check your inputs.")
                    elif bmi <= 18.5:
                        self.bmi_label.config(text=f"Underweight BMI: {bmi}")
                    elif 18.5 < bmi <= 24.9:
                        self.bmi_label.config(text=f"Healthy BMI: {bmi}")
                    elif 25 <= bmi <= 29.9:
                        self.bmi_label.config(text=f"Overweight BMI: {bmi}")
                    else:
                        self.bmi_label.config(text=f"Obese BMI: {bmi}")
                
                self.recommendations_label.config(text=f"Recommended Exercises: {', '.join(exercise_recommendations)}\n"
                                                    f"Recommended Diet: {diet_recommendations}")
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error updating profile display: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating profile: {str(e)}")

    def switch_profile_window(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT username FROM users")
        users = cursor.fetchall()
        
        if not users:
            messagebox.showerror("Error", "No profiles available")
            return

        self.switch_window = tk.Toplevel(self.root)
        self.switch_window.title("Switch Profile")
        self.switch_window.geometry("350x150")
        self.switch_window.config(bg="#f4f4f9")

        self.profile_selector = tk.StringVar()
        self.profile_selector.set(users[0][0])
        
        profile_dropdown = tk.OptionMenu(self.switch_window, self.profile_selector, *[user[0] for user in users])
        profile_dropdown.config(font=("Helvetica", 12))
        profile_dropdown.pack(pady=15)

        tk.Button(self.switch_window, text="Switch Profile", command=self.switch_profile,
        font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10).pack(pady=15)

    def switch_profile(self):
        selected_username = self.profile_selector.get()
        self.current_user = self.get_user_by_username(selected_username)
        if self.current_user:
            self.update_profile_display()
            self.switch_window.destroy()
            messagebox.showinfo("Success", f"Switched to profile: {selected_username}")
        else:
            messagebox.showerror("Error", "Could not switch profile")

    def display_profile(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return
        self.update_profile_display()

    def log_workout_window(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return

        self.workout_window = tk.Toplevel(self.root)
        self.workout_window.title("Log Workout")
        self.workout_window.geometry("400x400")
        self.workout_window.config(bg="#f4f4f9")

        tk.Label(self.workout_window, text="Exercise Name:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.exercise_entry = tk.Entry(self.workout_window, font=("Helvetica", 12))
        self.exercise_entry.pack(pady=5)

        tk.Label(self.workout_window, text="Sets:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.sets_entry = tk.Entry(self.workout_window, font=("Helvetica", 12))
        self.sets_entry.pack(pady=5)

        tk.Label(self.workout_window, text="Reps:", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.reps_entry = tk.Entry(self.workout_window, font=("Helvetica", 12))
        self.reps_entry.pack(pady=5)

        tk.Label(self.workout_window, text="Weight (kg):", font=("Helvetica", 12), bg="#f4f4f9").pack(pady=10)
        self.weight_entry_workout = tk.Entry(self.workout_window, font=("Helvetica", 12))
        self.weight_entry_workout.pack(pady=5)

        tk.Button(self.workout_window, text="Log Workout", command=self.log_workout,
                 font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="flat", padx=20, pady=10).pack(pady=20)

    def log_workout(self):
        try:
            exercise = self.exercise_entry.get()
            sets = int(self.sets_entry.get())
            reps = int(self.reps_entry.get())
            weight = float(self.weight_entry_workout.get())

            if not exercise or sets < 0 or reps < 0 or weight < 0:
                raise ValueError("Invalid input values")

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO workouts (user_id, exercise, sets, reps, weight)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.current_user['id'], exercise, sets, reps, weight))
            
            self.connection.commit()
            self.workout_window.destroy()
            messagebox.showinfo("Success", "Workout logged successfully!")

        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid values for all fields")
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def display_workouts(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please create or select a profile first")
            return

        workouts_window = tk.Toplevel(self.root)
        workouts_window.title("Workouts Log")
        workouts_window.geometry("800x400")
        workouts_window.config(bg="#f4f4f9")

        # Create a frame for the workouts
        workouts_frame = tk.Frame(workouts_window, bg="#f4f4f9")
        workouts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add title
        tk.Label(workouts_frame, text="Workout History", 
                font=("Helvetica", 16, "bold"), bg="#f4f4f9").pack(pady=10)

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT exercise, sets, reps, weight, date 
                FROM workouts 
                WHERE user_id = %s 
                ORDER BY date DESC
            """, (self.current_user['id'],))
            
            workouts = cursor.fetchall()

            if not workouts:
                tk.Label(workouts_frame, text="No workouts logged yet",
                        font=("Helvetica", 12), bg="#f4f4f9").pack(pady=20)
                return

            # Create headers
            headers_frame = tk.Frame(workouts_frame, bg="#f4f4f9")
            headers_frame.pack(fill=tk.X, pady=10)
            
            headers = ["Date", "Exercise", "Sets", "Reps", "Weight (kg)"]
            for header in headers:
                tk.Label(headers_frame, text=header, font=("Helvetica", 12, "bold"),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)

            # Create scrollable frame for workout entries
            canvas = tk.Canvas(workouts_frame, bg="#f4f4f9")
            scrollbar = tk.Scrollbar(workouts_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f4f4f9")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Add workout entries
            for workout in workouts:
                workout_frame = tk.Frame(scrollable_frame, bg="#f4f4f9")
                workout_frame.pack(fill=tk.X, pady=2)
                
                date_str = workout['date'].strftime("%Y-%m-%d %H:%M")
                tk.Label(workout_frame, text=date_str, font=("Helvetica", 11),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)
                tk.Label(workout_frame, text=workout['exercise'], font=("Helvetica", 11),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)
                tk.Label(workout_frame, text=str(workout['sets']), font=("Helvetica", 11),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)
                tk.Label(workout_frame, text=str(workout['reps']), font=("Helvetica", 11),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)
                tk.Label(workout_frame, text=str(workout['weight']), font=("Helvetica", 11),
                        bg="#f4f4f9", width=12).pack(side=tk.LEFT, padx=5)

            # Pack the canvas and scrollbar
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FitnessTracker()
    app.run()
