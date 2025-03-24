import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import plotly.express as px
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load Dataset
df = pd.read_excel("Indian_Food_Unique_Dataset.xlsx")

# Normalize column names to avoid hidden spaces
df.columns = df.columns.str.strip()

# Verify column names
food_column = "Item Name"
disease_column = "Recommended for Disease"
nutritional_columns = ["Calories", "Carbs", "Proteins", "Fats", "Fiber", "Sugar", "Sodium", "Iron", "Calcium", "Potassium", "Phosphorus", "Glycemic Index"]

# Disease-specific thresholds
disease_thresholds = {
    "Diabetes": {"Glycemic Index": "< 50", "Sugar": "Low", "Fiber": "High"},
    "Kidney Disease": {"Sodium": "< 300 mg", "Phosphorus": "< 150 mg", "Potassium": "< 300 mg"},
    "Heart Disease": {"Saturated Fat": "< 5g", "Fiber": "High", "Sodium": "Low"},
    "Hypertension": {"Sodium": "< 200 mg", "Potassium": "High"},
    "Obesity": {"Calories": "< 200 kcal", "Protein": "High", "Fiber": "High"}
}

# Function to recommend foods based on disease
def recommend_food_for_disease(disease, top_n=5):
    """
    Recommends foods based on the disease and nutritional thresholds.
    """
    if disease in disease_thresholds:
        thresholds = disease_thresholds[disease]
        filtered_df = df.copy()

        # Apply thresholds
        if disease == "Diabetes":
            filtered_df = filtered_df[(filtered_df["Glycemic Index"] < 50) & 
                                     (filtered_df["Sugar"] < filtered_df["Sugar"].quantile(0.25)) & 
                                     (filtered_df["Fiber"] > filtered_df["Fiber"].quantile(0.75))]
        elif disease == "Kidney Disease":
            filtered_df = filtered_df[(filtered_df["Sodium"] < 300) & 
                                      (filtered_df["Phosphorus"] < 150) & 
                                      (filtered_df["Potassium"] < 300)]
        elif disease == "Heart Disease":
            filtered_df = filtered_df[(filtered_df["Fats"] < 5) & 
                                     (filtered_df["Fiber"] > filtered_df["Fiber"].quantile(0.75)) & 
                                     (filtered_df["Sodium"] < filtered_df["Sodium"].quantile(0.25))]
        elif disease == "Hypertension":
            filtered_df = filtered_df[(filtered_df["Sodium"] < 200) & 
                                     (filtered_df["Potassium"] > filtered_df["Potassium"].quantile(0.75))]
        elif disease == "Obesity":
            filtered_df = filtered_df[(filtered_df["Calories"] < 200) & 
                                     (filtered_df["Proteins"] > filtered_df["Proteins"].quantile(0.75)) & 
                                     (filtered_df["Fiber"] > filtered_df["Fiber"].quantile(0.75))]

        if filtered_df.empty:
            st.warning(f"No foods found for the disease: {disease}")
            return []

        # Calculate cosine similarity between disease profile and all foods
        disease_nutrition = filtered_df[nutritional_columns].mean().values.reshape(1, -1)
        food_nutrition = filtered_df[nutritional_columns].values
        similarities = cosine_similarity(disease_nutrition, food_nutrition).flatten()

        # Get the top N most similar foods
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        recommended_foods = filtered_df.iloc[top_indices]

        return recommended_foods
    else:
        st.error(f"No thresholds defined for the disease: {disease}")
        return []

# Function for login/signup
def authenticate():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        st.title("🍏 Welcome to NutriTrack")
        st.write("Your personalized disease-based nutrition tracker.")
        if st.button("Get Started 🚀"):
            st.session_state.page = "login"
            st.rerun()
    
    elif st.session_state.page == "login":
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login 🔑", key="login_button"):
            st.session_state.logged_in = True
            st.session_state.page = "profile_setup"
            st.rerun()
        if st.button("Go to Sign Up 📝", key="signup_redirect"):
            st.session_state.page = "signup"
            st.rerun()
    
    elif st.session_state.page == "signup":
        st.title("📝 Sign Up")
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        if st.button("Sign Up ✅", key="signup_button"):
            st.success("Account Created! Redirecting to Login...")
            time.sleep(1)
            st.session_state.page = "login"
            st.rerun()

# Profile Setup with Detailed Questionnaire
def profile_setup():
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 1
        st.session_state.user_profile = {}

    if st.session_state.profile_step == 1:
        st.title("👤 Basic User Information")
        st.session_state.user_profile["Name"] = st.text_input("What is your name?")
        st.session_state.user_profile["Age"] = st.number_input("What is your age?", min_value=1, max_value=120, step=1)
        st.session_state.user_profile["Gender"] = st.selectbox("What is your gender?", ["Male", "Female", "Other"])
        st.session_state.user_profile["Height"] = st.number_input("What is your height (in cm)?", min_value=50, max_value=250, step=1)
        st.session_state.user_profile["Weight"] = st.number_input("What is your weight (in kg)?", min_value=20, max_value=300, step=1)
        if st.button("Next ➡️", key=f"next_step_{st.session_state.profile_step}"):
            st.session_state.profile_step = 2
            st.rerun()
    
    elif st.session_state.profile_step == 2:
        st.title("🏥 Health & Medical Conditions")
        st.session_state.user_profile["Medical Conditions"] = st.multiselect(
            "Do you have any diagnosed medical conditions?",
            ["Diabetes", "Kidney Disease", "Heart Disease", "Hypertension", "Obesity", "None"]
        )
        st.session_state.user_profile["Medications"] = st.radio(
            "Are you currently taking any medications that affect your diet?", ["Yes", "No"]
        )
        st.session_state.user_profile["Food Allergies"] = st.multiselect(
            "Do you have any food allergies or intolerances?", ["Lactose", "Gluten", "Nuts", "None"]
        )
        st.session_state.user_profile["Blood Pressure"] = st.radio(
            "Do you have high blood pressure or cholesterol issues?", ["Yes", "No"]
        )
        st.session_state.user_profile["Dietary Restrictions"] = st.selectbox(
            "Do you have any dietary restrictions?", ["Vegetarian", "Vegan", "Jain", "Halal", "None"]
        )
        if st.button("Next ➡️", key=f"next_step_{st.session_state.profile_step}"):
            st.session_state.profile_step = 3
            st.rerun()
    
    elif st.session_state.profile_step == 3:
        st.title("🍽️ Dietary Preferences & Eating Habits")
        st.session_state.user_profile["Diet Type"] = st.selectbox(
            "What is your preferred diet type?", ["Vegetarian", "Non-Vegetarian", "Vegan"]
        )
        st.session_state.user_profile["Meals Per Day"] = st.number_input(
            "How many meals do you eat per day?", min_value=1, max_value=10, step=1
        )
        st.session_state.user_profile["Dairy Consumption"] = st.radio(
            "Do you consume dairy products?", ["Yes", "No"]
        )
        st.session_state.user_profile["Processed Food"] = st.selectbox(
            "Do you consume processed or fast food often?", ["Rarely", "Sometimes", "Often"]
        )
        st.session_state.user_profile["Water Intake"] = st.number_input(
            "How much water do you drink per day (in liters)?", min_value=0.5, max_value=10.0, step=0.5
        )
        st.session_state.user_profile["Alcohol/Smoke"] = st.radio(
            "Do you consume alcohol or smoke?", ["Yes", "No"]
        )
        if st.button("Next ➡️", key=f"next_step_{st.session_state.profile_step}"):
            st.session_state.profile_step = 4
            st.rerun()
    
    elif st.session_state.profile_step == 4:
        st.title("🏋️ Activity Level & Lifestyle")
        st.session_state.user_profile["Activity Level"] = st.selectbox(
            "How active are you daily?",
            ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
        )
        st.session_state.user_profile["Physical Limitations"] = st.radio(
            "Do you have any physical limitations or disabilities?", ["Yes", "No"]
        )
        if st.button("Next ➡️", key=f"next_step_{st.session_state.profile_step}"):
            st.session_state.profile_step = 5
            st.rerun()
    
    elif st.session_state.profile_step == 5:
        st.title("🎯 Goals & Personalization")
        st.session_state.user_profile["Primary Goal"] = st.selectbox(
            "What is your primary goal?",
            ["Maintain Current Weight", "Lose Weight", "Gain Weight", "Manage Disease Symptoms"]
        )
        st.session_state.user_profile["Preferred Cuisine"] = st.selectbox(
            "Do you prefer a specific cuisine?", ["Indian", "Mediterranean", "Keto", "None"]
        )
        st.session_state.user_profile["Meal Plan Strictness"] = st.selectbox(
            "How strict do you want your meal plans to be?", ["Flexible", "Moderate", "Strict"]
        )
        if st.button("Finish Setup ✅", key="finish_setup"):
            st.success("Profile setup completed! Redirecting to Dashboard...")
            time.sleep(1)
            st.session_state.page = "dashboard"
            st.rerun()

# Main App
st.set_page_config(page_title="Disease-Based NutriTracker", layout="wide", page_icon="🍏")

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

if not st.session_state.get("logged_in", False):
    authenticate()
elif st.session_state.page == "profile_setup":
    profile_setup()
else:
    with st.sidebar:
        selected = option_menu("Dashboard", ["Food Log/Recommendations", "Progress Tracking", "Goals & Reminders", "Account"],
                               icons=["🍽️", "📊", "🎯", "👤"], menu_icon="🏠", default_index=0)
    
    if selected == "Food Log/Recommendations":
        st.title("🍽️ Food Log/Recommendations")
        
        # Tabs for Food Log and Recommendations
        tab1, tab2 = st.tabs(["Food Log", "Recommendations"])
        
        with tab1:
            st.subheader("Log Your Food")
            meal_type = st.radio("Select Meal Type", ["Breakfast", "Lunch", "Dinner"], horizontal=True)
            servings = st.number_input("Number of Servings", min_value=1, max_value=10, step=1)
            
            # Filter food based on disease if applicable
            if disease_column and "user_profile" in st.session_state and "Medical Conditions" in st.session_state["user_profile"]:
                user_diseases = st.session_state["user_profile"]["Medical Conditions"]
                filtered_df = df[df[disease_column].apply(lambda x: any(disease in str(x) for disease in user_diseases))]
            else:
                filtered_df = df
            
            food_item = st.selectbox("Select Food", filtered_df[food_column].unique())
            if st.button("Log Food 📝", key="log_food_button"):
                if "logged_food" not in st.session_state:
                    st.session_state.logged_food = []
                st.session_state.logged_food.append({
                    "meal": meal_type,
                    "food": food_item,
                    "servings": servings,
                    "date": pd.Timestamp.today().strftime('%Y-%m-%d')
                })
                st.success(f"{food_item} logged for {meal_type} with {servings} serving(s)!")
            
            if "logged_food" in st.session_state:
                with st.expander("Nutrition Breakdown 📊"):
                    st.write(filtered_df[filtered_df[food_column] == food_item])
        
        with tab2:
            st.subheader("Get Personalized Food Recommendations")
            st.write("Based on your health conditions, here are some recommendations.")
            
            if "user_profile" in st.session_state and "Medical Conditions" in st.session_state["user_profile"]:
                user_diseases = st.session_state["user_profile"]["Medical Conditions"]
                selected_foods = []  # To store selected foods for logging

                for disease in user_diseases:
                    recommended_foods = recommend_food_for_disease(disease)
                    if not recommended_foods.empty:
                        st.subheader(f"Recommended Foods for {disease}:")
                        for i, row in recommended_foods.iterrows():
                            # Add a tick box for each recommended food with a unique key
                            if st.checkbox(f"{row[food_column]} - Calories: {row['Calories']}, Carbs: {row['Carbs']}g, Proteins: {row['Proteins']}g, Fats: {row['Fats']}g", 
                                          key=f"select_{row[food_column]}_{disease}_{i}"):
                                selected_foods.append({
                                    "meal": "Recommended Meal",
                                    "food": row[food_column],
                                    "servings": 1,
                                    "date": pd.Timestamp.today().strftime('%Y-%m-%d')
                                })
                    else:
                        st.warning(f"No recommendations found for {disease}.")

                # Button to log selected foods
                if st.button("Log Selected Foods 🍴", key="log_selected_foods"):
                    if selected_foods:
                        if "logged_food" not in st.session_state:
                            st.session_state.logged_food = []
                        st.session_state.logged_food.extend(selected_foods)
                        st.success(f"{len(selected_foods)} foods logged for Recommended Meal!")
                        st.rerun()  # Refresh the page to update the logged food list
                    else:
                        st.warning("No foods selected for logging.")
            else:
                st.warning("No health conditions selected in your profile.")
    
    elif selected == "Progress Tracking":
        st.title("📊 Progress Tracking")
        
        # Set Daily Calorie Goal
        st.subheader("Set Your Daily Calorie Goal")
        calorie_goal = st.number_input("Enter your daily calorie goal", min_value=0, value=1500, step=100)
        
        # Calculate remaining calories
        if "logged_food" in st.session_state and st.session_state["logged_food"]:
            total_calories_consumed = sum(df.loc[df[food_column] == log["food"], "Calories"].values[0] * log["servings"] for log in st.session_state["logged_food"] if "Calories" in df.columns)
        else:
            total_calories_consumed = 0
        
        remaining_calories = calorie_goal - total_calories_consumed
        
        # Display Calorie Goal, Consumed, and Remaining
        st.write(f"### Calories")
        st.write(f"**Remaining = Goal - Food + Exercise**")
        st.write(f"**{remaining_calories}** Remaining")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Base Goal**")
            st.write(f"{calorie_goal}")
        with col2:
            st.write(f"**Food**")
            st.write(f"{total_calories_consumed}")
        with col3:
            st.write(f"**Exercise**")
            st.write("0")  # Placeholder for exercise calories
        
        # Nutrient Tracking
        if "logged_food" in st.session_state and st.session_state["logged_food"]:
            nutrients = ["Calories", "Carbs", "Proteins", "Fats"]
            nutrient_values = {nutrient: sum(df.loc[df[food_column] == log["food"], nutrient].values[0] * log["servings"] for log in st.session_state["logged_food"] if nutrient in df.columns) for nutrient in nutrients}
            
            st.subheader("Nutrient Intake Bar Chart")
            fig_bar = px.bar(x=nutrient_values.keys(), y=nutrient_values.values(), labels={'x': 'Nutrient', 'y': 'Amount'}, title="Nutrient Consumption")
            st.plotly_chart(fig_bar)
            
            st.subheader("Nutrient Distribution Pie Chart")
            fig_pie = px.pie(values=nutrient_values.values(), names=nutrient_values.keys(), title="Nutrient Composition")
            st.plotly_chart(fig_pie)
        else:
            st.write("No food logged yet.")
    
    elif selected == "Goals & Reminders":
        st.title("🎯 Daily Goals & Reminders")
        goal = st.text_input("Set a goal for today")
        if st.button("Save Goal 💾", key="save_goal"):
            st.session_state["goal"] = goal
            st.success("Goal Saved!")
        if "goal" in st.session_state:
            if st.button("Mark as Completed ✅", key="complete_goal"):
                st.success("Goal Completed!")
        reminder_time = st.time_input("Set Reminder ⏰")
        if st.button("Set Alarm 🔔", key="set_alarm"):
            st.success(f"Alarm set for {reminder_time}")
    
    elif selected == "Account":
        st.title("👤 Account Details")
        
        if "user_profile" in st.session_state:
            user_profile = st.session_state["user_profile"]
            
            st.write("### User Information")
            account_data = {
                "Name": user_profile.get("Name", "N/A"),
                "Age": user_profile.get("Age", "N/A"),
                "Gender": user_profile.get("Gender", "N/A"),
                "Height (cm)": user_profile.get("Height", "N/A"),
                "Weight (kg)": user_profile.get("Weight", "N/A"),
                "Medical Conditions": ", ".join(user_profile.get("Medical Conditions", ["N/A"])),
                "Dietary Restrictions": user_profile.get("Dietary Restrictions", "N/A"),
                "Primary Goal": user_profile.get("Primary Goal", "N/A"),
            }
            
            account_df = pd.DataFrame(account_data.items(), columns=["Field", "Value"])
            st.table(account_df)
        
        if st.button("Logout 🔒", key="logout_button_account"):
            st.session_state.logged_in = False
            st.session_state.page = "home"
            st.rerun()

