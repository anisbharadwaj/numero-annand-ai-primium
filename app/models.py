from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birth_date = db.Column(db.String(20), nullable=False)
    birth_time = db.Column(db.String(20), nullable=False)
    birth_place = db.Column(db.String(150), nullable=False)
    language = db.Column(db.String(30), nullable=False)
    report_type = db.Column(db.String(20), nullable=False)  # 'digital' or 'premium'
    amount = db.Column(db.Integer, nullable=False)          # 201 or 501
    address = db.Column(db.Text, nullable=True)
    utr = db.Column(db.String(12), unique=True, nullable=True)
    screenshot = db.Column(db.String(200), nullable=True)
    payment_status = db.Column(db.String(20), default='pending') # 'pending' or 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
