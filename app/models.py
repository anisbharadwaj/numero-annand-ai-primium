from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime  
import uuid  

db = SQLAlchemy()  


def generate_uuid():  
    return str(uuid.uuid4())  


class User(db.Model):  
    __tablename__ = 'users'  

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)  
    name = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password_hash = db.Column(db.String(256), nullable=False)  
    phone = db.Column(db.String(20))  
    role = db.Column(db.String(20), default='customer')  
    is_active = db.Column(db.Boolean, default=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

    orders = db.relationship('Order', backref='user', lazy=True)  
    reports = db.relationship('Report', backref='user', lazy=True)  

    def to_dict(self):  
        return {  
            'id': self.id,  
            'name': self.name,  
            'email': self.email,  
            'phone': self.phone,  
            'role': self.role,  
            'is_active': self.is_active,  
            'created_at': self.created_at.isoformat() if self.created_at else None  
        }  


class Admin(db.Model):  
    __tablename__ = 'admins'  

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)  
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  
    permissions = db.Column(db.String(500), default='all')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

    user = db.relationship('User', backref='admin_profile')  


class Order(db.Model):  
    __tablename__ = 'orders'  

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)  
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  
    order_number = db.Column(db.String(20), unique=True, nullable=False)  
    amount = db.Column(db.Float, nullable=False)  
    plan_type = db.Column(db.String(50), nullable=False)  
    status = db.Column(db.String(20), default='pending')  
    payment_status = db
