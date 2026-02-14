from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-later'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app/static/screenshots')
    app.config['DATABASE'] = os.path.join(os.getcwd(), 'database/trading_journal.db')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    
    # Initialize database
    from app.models.database import Database
    Database(app.config['DATABASE'])
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    from app.routes.trades import bp as trades_bp
    from app.routes.screenshots import bp as screenshots_bp
    from app.routes.tags import bp as tags_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(screenshots_bp)
    app.register_blueprint(tags_bp)
    
    return app