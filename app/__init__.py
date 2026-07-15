import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    app.config.from_object(config_class)

    # Initialize Extension Contexts
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login_route'
    login_manager.login_message_category = 'warning'

    # Ensure Upload Path Exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Structural Blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.payments.routes import payments_bp
    from app.api.qr import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(payments_bp, url_prefix='/order')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Global Custom Error Handling Contexts
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
