import os
from dotenv import load_dotenv

# Load environment variables from .env file (development)
load_dotenv()

class Config:
    """Centralized configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Vercel API integration
    VERCEL_TOKEN = os.getenv('VERCEL_TOKEN')
    VERCEL_PROJECT = os.getenv('VERCEL_PROJECT')  # project ID or name
    VERCEL_TEAM = os.getenv('VERCEL_TEAM')        # (optional) Team ID

    # Auth and session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400  # seconds

    # CSRF protection (Flask-WTF uses SECRET_KEY)
    WTF_CSRF_ENABLED = True

    # Other security headers can be set via Flask-Talisman if desired
