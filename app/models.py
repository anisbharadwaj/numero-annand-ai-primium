from app import db
from flask_login import UserMixin
from datetime import datetime

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    birth_time = db.Column(db.String(20), nullable=False)
    birth_place = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(30), nullable=False)
    report_type = db.Column(db.String(50), nullable=False) # 'digital' or 'printed'
    address = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(20), default="Pending") # Pending, Verified, Rejected
    utr = db.Column(db.String(50), nullable=False)
    screenshot = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
