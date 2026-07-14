from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
from config import Config

# Initialize extensions without app context
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Flask application factory."""
    app = Flask(__name__, static_folder=None)  # disable default static_folder
    app.config.from_object(Config)

    # Initialize logging to a file
    handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

    # Register Blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.studyiq.routes import studyiq_bp
    from app.payments.routes import payments_bp
    from app.api.deployments import api_deploy_bp
    from app.api.qr import api_qr_bp
    from app.api.studyiq import api_studyiq_bp
    from app.api.logs import api_logs_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(studyiq_bp, url_prefix='/studyiq')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(api_deploy_bp)
    app.register_blueprint(api_qr_bp)
    app.register_blueprint(api_studyiq_bp)
    app.register_blueprint(api_logs_bp)

    # Error handlers
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 Error: {error}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Error: {error}")
        return render_template('errors/500.html'), 500

    return app
