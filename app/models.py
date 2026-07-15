from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_ref = db.Column(db.String(12), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    birth_time = db.Column(db.String(20), nullable=False)
    birth_place = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(15), nullable=False)
    language = db.Column(db.String(30), nullable=False)
    report_type = db.Column(db.String(30), nullable=False) # 'digital' or 'printed'
    address = db.Column(db.Text, nullable=True) # Conditional based on printing
    amount = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(20), default='PENDING') # PENDING, VERIFIED, REJECTED
    utr = db.Column(db.String(50), nullable=True)
    screenshot = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
