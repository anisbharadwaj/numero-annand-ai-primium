from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Optional for guest users
    subscription_tier = db.Column(db.String(20), default='basic')  # 'guest', 'basic', 'premium'
    ai_messages_used = db.Column(db.Integer, default=0)
    ai_message_reset_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='en')  # 'en', 'hi', 'as'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_ai_message_limit(self):
        """Returns remaining AI messages for the user based on subscription."""
        if self.subscription_tier == 'premium':
            return float('inf')  # Unlimited
        elif self.subscription_tier == 'basic':
            limit = 30
        else:  # guest
            limit = 5
        
        # Reset counter if 24 hours have passed
        if datetime.utcnow() - self.ai_message_reset_at > timedelta(hours=24):
            self.ai_messages_used = 0
            self.ai_message_reset_at = datetime.utcnow()
            db.session.commit()
        
        return max(0, limit - self.ai_messages_used)
    
    def increment_ai_messages(self):
        """Increment AI message counter and return if user has remaining messages."""
        if self.subscription_tier == 'premium':
            return True
        self.ai_messages_used += 1
        db.session.commit()
        return self.get_ai_message_limit() >= 0

class AIChat(db.Model):
    __tablename__ = 'ai_chats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # NULL for guests
    session_id = db.Column(db.String(100), nullable=True)  # For guest tracking
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='en')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
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
