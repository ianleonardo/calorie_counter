class Translations:
    TRANSLATIONS = {
        "English": {
            "title": "🥗 AI Health Coach",
            "sidebar_title": "👤 Your Profile",
            "gender": "Gender",
            "age": "Age (years)",
            "weight": "Weight (kg)",
            "height": "Height (cm)",
            "activity": "Activity Level",
            "goal_label": "Current Goal",
            "diet_label": "Dietary Preference",
            "upload_label": "Upload your meal photo",
            "analyze_btn": "Analyze Nutrition",
            "analyzing": "🍎 Consulting the AI Nutritionist...",
            "calories": "Total Energy",
            "daily_target": "Daily Target",
            "meal_impact": "Meal Impact",
            "health_score": "Health Score",
            "compliant": "Diet Compliant",    
            "non_compliant": "Not Compliant",
            "macros": "📊 Macronutrients",
            "burn": "🔥 Time to Burn It Off",
            "feedback": "💡 AI Coach Feedback",
            "identified": "Identified Items",
            "pro_tip": "💪 Pro Tip",
            "walk": "Walking",
            "run": "Running",
            "swim": "Swimming",
            "min": "min",
            "goals": ["Maintain Weight", "Weight Loss", "Muscle Gain"],
            "diets": ["No Restriction", "Keto", "Vegan", "Vegetarian", "Paleo", "Low Carb"],
            "genders": ["Male", "Female"],
            "activities": ["Sedentary (Office Job)", "Lightly Active (1-3 days/wk)", "Moderately Active (3-5 days/wk)", "Very Active (6-7 days/wk)"],
            "impact_msg": "This meal is **{pct}%** of your daily needs."
        }
    }
    
    @classmethod
    def get_translation(cls, language):
        """Get translation dictionary for specified language."""
        return cls.TRANSLATIONS.get(language, cls.TRANSLATIONS["English"])
    
    @classmethod
    def get_available_languages(cls):
        """Get list of available languages."""
        return list(cls.TRANSLATIONS.keys())
