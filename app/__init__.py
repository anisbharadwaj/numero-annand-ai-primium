import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Safe fallback configuration settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secure-premium-key-928130')
    
    # If no database link is in environment variables, use memory storage to avoid read-only system crashes
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extension Modules
    from app.models import db, AdminUser
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # Register Blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.payments.routes import payments_bp
    from app.api.qr import qr_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(qr_bp)

    # Initialize context safely without crashing if file storage is locked out
    try:
        with app.app_context():
            db.create_all()
            from werkzeug.security import generate_password_hash
            if not AdminUser.query.filter_by(username='admin').first():
                hashed_pwd = generate_password_hash('AnnandSarmaAI2026')
                master_admin = AdminUser(username='admin', password_hash=hashed_pwd)
                db.session.add(master_admin)
                db.session.commit()
    except Exception:
        pass # Prevents the serverless node from crashing completely if disk writing fails

    return app
