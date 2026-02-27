from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration from environment
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app/static/screenshots')
    app.config['DATABASE'] = os.getenv('DATABASE_PATH', os.path.join(os.getcwd(), 'database/trading_journal.db'))
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE_MB', 16)) * 1024 * 1024
    
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    
    # Initialize database
    from app.models.database import Database
    Database(app.config['DATABASE'])
    
    # Run migrations
    from app.models.migrations import Migration
    migration = Migration(app.config['DATABASE'])
    try:
        migration.run_all_migrations()
    except Exception as e:
        print(f"Migration error: {e}")
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get(int(user_id), app.config['DATABASE'])
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    from app.routes.trades import bp as trades_bp
    from app.routes.screenshots import bp as screenshots_bp
    from app.routes.tags import bp as tags_bp
    from app.routes.statistics import bp as statistics_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.landing import bp as landing_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(screenshots_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    
    return app