from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp

class User(UserMixin, db.Model):
    """User account (with 2FA)."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # TOTP secret for 2FA (base32 string)
    totp_secret = db.Column(db.String(16), nullable=False, default=pyotp.random_base32)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        """Return provisioning URI for Google Authenticator."""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(name=self.email, issuer_name="StudyDashboard")

    def verify_totp(self, token):
        """Verify a time-based OTP."""
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)  # allow 1 step clock skew

    def __repr__(self):
        return f"<User {self.email}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class StudyResource(db.Model):
    """Educational content item (YouTube playlist, note, etc.)."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    url = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<StudyResource {self.title}>"

class Deployment(db.Model):
    """Records of deployments fetched from Vercel."""
    id = db.Column(db.Integer, primary_key=True)
    vercel_id = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(300))
    date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    duration = db.Column(db.Float)
    commit = db.Column(db.String(40))

class LogEntry(db.Model):
    """Application log entry (from file or generated)."""
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

class Alert(db.Model):
    """Anomaly or conflict alert."""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
