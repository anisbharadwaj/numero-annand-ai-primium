import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "numero_annand_secret_fallback_123890!@#")
    # Use local SQLite on Windows, fallback to an in-memory or PostgreSQL structure if on production Vercel
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///numero_annand.db")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB Max upload limit for payment proofs
