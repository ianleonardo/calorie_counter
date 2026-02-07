class CalorieCalculator:
    @staticmethod
    def calculate_target_calories(gender_idx, age, weight, height, activity_idx, goal_idx):
        """
        Mifflin-St Jeor Equation to calculate BMR and TDEE.
        """
        # 1. Base BMR
        if gender_idx == 0:  # Male
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # Female
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # 2. Activity Multiplier
        multipliers = [1.2, 1.375, 1.55, 1.725]  # Matches the index of the dropdown
        tdee = bmr * multipliers[activity_idx]

        # 3. Goal Adjustment
        if goal_idx == 0:  # Maintain
            target = tdee
        elif goal_idx == 1:  # Lose Weight
            target = tdee - 500
        else:  # Gain Muscle
            target = tdee + 400
            
        return int(target)
    
    @staticmethod
    def calculate_meal_impact_percentage(calories, daily_target):
        """Calculate what percentage of daily calories the meal represents."""
        if daily_target == 0:
            return 0
        return min((calories / daily_target) * 100, 100)
    
    @staticmethod
    def calculate_progress_ratio(calories, daily_target):
        """Calculate progress ratio for progress bar (0.0 to 1.0)."""
        if daily_target == 0:
            return 0
        return min(calories / daily_target, 1.0)
