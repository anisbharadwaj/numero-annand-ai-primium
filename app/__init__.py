import os
from flask import Flask, render_subplots, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.payments.routes import payments_bp
    from app.api.qr import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Custom user loader simulation for single Admin
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "admin":
            return User("admin", os.environ.get('ADMIN_USERNAME', 'admin'))
        return None

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    # Create missing directories and DB structures
    with app.app_context():
        os.makedirs(os.path.join(app.root_path, '../instance'), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, '../logs'), exist_ok=True)
        db.create_all()

    return app
