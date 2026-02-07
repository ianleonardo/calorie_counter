# AI Health Coach - Flask Version

A Flask-based web application that provides AI-powered nutrition analysis from food images, following the MVC (Model-View-Controller) architectural pattern.

## Features

- 🥗 Multi-language support (English, Bahasa Indonesia, Simplified Chinese, Filipino)
- 📸 Image upload and analysis using Google Gemini AI
- 📊 Personalized calorie calculations based on user profile
- 🎯 Daily calorie targets and meal impact analysis
- 💡 AI-powered nutrition feedback and suggestions
- 📱 Responsive web design with modern UI

## Architecture

The application follows MVC pattern:

### Models (`models/`)
- `user_profile.py` - User profile and nutrition result data structures
- `calculator.py` - Calorie calculation logic using Mifflin-St Jeor equation
- `ai_service.py` - Google Gemini AI integration for food analysis
- `translations.py` - Multi-language support

### Controllers (`controllers/`)
- `main_controller.py` - Main application routes and business logic

### Views (`templates/`)
- `base.html` - Base template with common layout
- `index.html` - Main application interface

### Static Assets (`static/`)
- `css/style.css` - Custom styling with Tailwind CSS
- `js/main.js` - Frontend JavaScript functionality

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file:
```
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_flask_secret_key_here
FLASK_DEBUG=True
```

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Select your preferred language
2. Fill in your profile information (age, weight, height, activity level, goals)
3. Upload a photo of your meal
4. Click "Analyze Nutrition" to get detailed nutritional insights

## API Endpoints

- `GET /` - Main application page
- `POST /analyze` - Analyze uploaded food image
- `POST /update_profile` - Update user profile and calculate daily targets

## Technologies Used

- **Backend**: Flask 2.3.3
- **AI**: Google Gemini API
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Image Processing**: Pillow
- **Environment Management**: python-dotenv
