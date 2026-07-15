import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-architect-key-change-in-prod-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///numero_annand.db')
    # Track modifications takes memory, turn off in production
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configurations
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True if os.environ.get('FLASK_ENV') == 'production' else False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Configs for Payment Proofs
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB Max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Business/UPI Variables
    UPI_ID = "7099805039@ybl"
    PAYEE_NAME = "Ananda Sarmah"
    BRAND_NAME = "Numero Annand AI Premium"
