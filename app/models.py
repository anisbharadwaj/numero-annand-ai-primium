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
    payment_status = db.Column(db.String(20), default='unpaid')  
    upi_transaction_id = db.Column(db.String(100))  
    admin_verified = db.Column(db.Boolean, default=False)  
    verified_by = db.Column(db.String(36), db.ForeignKey('admins.id'))  
    report_generated = db.Column(db.Boolean, default=False)  
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'))  
    customer_data = db.Column(db.Text)  
    notes = db.Column(db.Text)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

    def to_dict(self):  
        return {  
            'id': self.id,  
            'user_id': self.user_id,  
            'order_number': self.order_number,  
            'amount': self.amount,  
            'plan_type': self.plan_type,  
            'status': self.status,  
            'payment_status': self.payment_status,  
            'upi_transaction_id': self.upi_transaction_id,  
            'admin_verified': self.admin_verified,  
            'report_generated': self.report_generated,  
            'customer_data': self.customer_data,  
            'created_at': self.created_at.isoformat() if self.created_at else None,  
            'updated_at': self.updated_at.isoformat() if self.updated_at else None  
        }  


class Payment(db.Model):  
    __tablename__ = 'payments'  

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)  
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)  
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  
    amount = db.Column(db.Float, nullable=False)  
    upi_transaction_id = db.Column(db.String(100))  
    payment_method = db.Column(db.String(50),
