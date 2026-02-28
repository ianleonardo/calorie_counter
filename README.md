# AI Health Coach - Flask Version

A Flask-based web application that provides AI-powered nutrition analysis from food images, following the MVC (Model-View-Controller) architectural pattern.

## Features

- 🔐 Google OAuth login
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
- `translations.py` - UI text translations

### Controllers (`controllers/`)
- `auth_controller.py` - Google OAuth login/logout and `login_required` decorator
- `main_controller.py` - Main application routes and business logic

### Views (`templates/`)
- `base.html` - Base template with common layout
- `login.html` - Google sign-in page
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
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
SECRET_KEY=your_flask_secret_key_here
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Navigate to **APIs & Services → OAuth consent screen** → choose External → fill in app name and emails
4. Navigate to **APIs & Services → Credentials → + CREATE CREDENTIALS → OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URI: `http://localhost:8080/auth/callback`
5. Copy the **Client ID** and **Client Secret** into your `.env` file

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:8080`

## Usage

1. Sign in with your Google account
2. Fill in your profile information (age, weight, height, activity level, goals)
3. Upload a photo of your meal
4. Click "Analyze Nutrition" to get detailed nutritional insights

## API Endpoints

- `GET /login` - Google sign-in page
- `GET /auth/google` - Initiate Google OAuth flow
- `GET /auth/callback` - Google OAuth callback
- `GET /logout` - Sign out
- `GET /` - Main application page (requires login)
- `POST /analyze` - Analyze uploaded food image (requires login)
- `POST /update_profile` - Update user profile and calculate daily targets (requires login)

## Technologies Used

- **Backend**: Flask 2.3.3
- **Authentication**: Google OAuth 2.0 via Authlib
- **AI**: Google Gemini API
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Image Processing**: Pillow
- **Environment Management**: python-dotenv
