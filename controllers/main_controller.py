from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
from PIL import Image
import io
import base64
import re

from models.user_profile import UserProfile, NutritionResult
from models.calculator import CalorieCalculator
from models.ai_service import AIService
from models.translations import Translations

main_bp = Blueprint('main', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    """Main page with language selection and profile form."""
    language = request.args.get('lang', 'English')
    translations = Translations.get_translation(language)
    
    # Get user profile from session or use defaults
    profile = session.get('user_profile', {})
    
    return render_template('index.html', 
                         translations=translations,
                         language=language,
                         available_languages=Translations.get_available_languages(),
                         profile=profile)

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """Handle image upload and nutrition analysis."""
    try:
        # Get form data with validation
        language = request.form.get('language', 'English')
        translations = Translations.get_translation(language)
        
        # Debug: Log received form data
        current_app.logger.info(f"Received form data: {dict(request.form)}")
        
        # Get form values with defaults
        gender = request.form.get('gender')
        age = request.form.get('age', '25')
        weight = request.form.get('weight', '70')
        height = request.form.get('height', '170')
        activity_level = request.form.get('activity_level')
        goal = request.form.get('goal')
        diet_type = request.form.get('diet_type')
        
        # Debug: Log individual values
        current_app.logger.info(f"Parsed values - gender: {gender}, activity: {activity_level}, goal: {goal}, diet: {diet_type}")
        
        # Validate required fields
        if not all([gender, activity_level, goal, diet_type]):
            return jsonify({'error': 'Please fill in all profile fields'}), 400
        
        # Create user profile
        try:
            profile = UserProfile(
                gender=gender,
                age=int(age),
                weight=float(weight),
                height=float(height),
                activity_level=activity_level,
                goal=goal,
                diet_type=diet_type
            )
        except (ValueError, TypeError) as e:
            return jsonify({'error': 'Invalid profile data'}), 400
        
        # Save profile to session
        session['user_profile'] = {
            'gender': profile.gender,
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
            'activity_level': profile.activity_level,
            'goal': profile.goal,
            'diet_type': profile.diet_type
        }
        
        # Calculate daily target calories with error handling
        try:
            gender_idx = profile.get_gender_index(translations['genders'])
            activity_idx = profile.get_activity_index(translations['activities'])
            goal_idx = profile.get_goal_index(translations['goals'])
        except ValueError as e:
            return jsonify({'error': f'Invalid profile selection: {str(e)}'}), 400
        
        daily_target = CalorieCalculator.calculate_target_calories(
            gender_idx, profile.age, profile.weight, profile.height, 
            activity_idx, goal_idx
        )
        
        # Handle image upload
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Process image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get AI analysis
        ai_service = AIService()
        processed_image = ai_service.process_image(image)
        analysis_data = ai_service.get_nutrition_analysis(
            processed_image, profile.goal, profile.diet_type, language
        )
        
        # Create nutrition result
        result = NutritionResult.from_dict(analysis_data)
        
        # Calculate meal impact
        meal_impact_pct = CalorieCalculator.calculate_meal_impact_percentage(
            result.total_calories, daily_target
        )
        progress_ratio = CalorieCalculator.calculate_progress_ratio(
            result.total_calories, daily_target
        )
        
        # Convert image to base64 for display
        buffered = io.BytesIO()
        processed_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'result': {
                'food_items': result.food_items,
                'total_calories': result.total_calories,
                'macros': result.macros,
                'health_score': result.health_score,
                'burn_off': result.burn_off,
                'is_diet_compliant': result.is_diet_compliant,
                'analysis': result.analysis,
                'suggestion': result.suggestion,
                'daily_target': daily_target,
                'meal_impact_pct': int(meal_impact_pct),
                'progress_ratio': progress_ratio,
                'image_data': img_str
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        
        if "RATE_LIMIT_EXCEEDED" in error_msg:
            # Extract wait time from error message if available
            wait_time = 30  # default
            match = re.search(r"retry in ([0-9\.]+)s", error_msg)
            if match:
                wait_time = int(float(match.group(1)))
            
            return jsonify({
                'error': 'RATE_LIMIT',
                'message': f'Please wait {wait_time} seconds before trying again.',
                'wait_time': wait_time
            }), 429
        else:
            current_app.logger.error(f"Analysis error: {e}")
            return jsonify({
                'error': 'ANALYSIS_ERROR',
                'message': 'An error occurred during analysis. Please try again.'
            }), 500

@main_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile in session."""
    try:
        # Debug: Log received form data
        current_app.logger.info(f"Update profile received form data: {dict(request.form)}")
        
        # Get form values with validation
        gender = request.form.get('gender')
        age = request.form.get('age', '25')
        weight = request.form.get('weight', '70')
        height = request.form.get('height', '170')
        activity_level = request.form.get('activity_level')
        goal = request.form.get('goal')
        diet_type = request.form.get('diet_type')
        
        # Debug: Log individual values
        current_app.logger.info(f"Update profile values - gender: {gender}, activity: {activity_level}, goal: {goal}, diet: {diet_type}")
        
        # Validate required fields
        if not all([gender, activity_level, goal, diet_type]):
            return jsonify({'error': 'Please fill in all profile fields'}), 400
        
        profile = {
            'gender': gender,
            'age': int(age),
            'weight': float(weight),
            'height': float(height),
            'activity_level': activity_level,
            'goal': goal,
            'diet_type': diet_type
        }
        
        session['user_profile'] = profile
        
        # Calculate and return daily target
        language = request.form.get('language', 'English')
        translations = Translations.get_translation(language)
        
        # Handle index lookup with error handling
        try:
            gender_idx = translations['genders'].index(profile['gender'])
            activity_idx = translations['activities'].index(profile['activity_level'])
            goal_idx = translations['goals'].index(profile['goal'])
        except ValueError as e:
            return jsonify({'error': f'Invalid profile selection: {str(e)}'}), 400
        
        daily_target = CalorieCalculator.calculate_target_calories(
            gender_idx, profile['age'], profile['weight'], profile['height'],
            activity_idx, goal_idx
        )
        
        return jsonify({
            'success': True,
            'daily_target': daily_target
        })
        
    except Exception as e:
        current_app.logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500
