from flask import Flask
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure OAuth
    oauth = OAuth(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
    # Store oauth in app extensions so controllers can access it
    app.extensions['oauth'] = oauth
    
    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.main_controller import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500
    
    @app.errorhandler(413)
    def too_large(error):
        return "File too large", 413
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Get the port from the environment variable, defaulting to 8080
    port = int(os.environ.get("PORT", 8080))
    
    # Bind to 0.0.0.0 and use the dynamic port
    app.run(host='0.0.0.0', port=port)

