from flask import Flask
import os
from dotenv import load_dotenv

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
    
    # Register blueprints
    from controllers.main_controller import main_bp
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
