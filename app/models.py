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

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 'admin', 'editor', 'moderator', 'viewer'
    description = db.Column(db.String(255), nullable=True)
    permissions = db.Column(db.JSON, default=dict)  # e.g. {"orders": ["view", "edit"], "users": ["view"]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin_users = db.relationship('AdminUser', backref='role', lazy=True)

class AdminRole(db.Model):
    """Junction table for AdminUser roles (many-to-many)"""
    __tablename__ = 'admin_roles'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # 'create', 'update', 'delete', 'verify', 'export'
    resource_type = db.Column(db.String(50), nullable=False)  # 'order', 'user', 'blog', 'page'
    resource_id = db.Column(db.String(50), nullable=True)
    old_values = db.Column(db.JSON, nullable=True)  # Before state
    new_values = db.Column(db.JSON, nullable=True)  # After state
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    admin = db.relationship('AdminUser', backref='audit_logs')

class CMSPage(db.Model):
    __tablename__ = 'cms_pages'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    seo_title = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.String(500), nullable=True)
    featured_image = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    author = db.relationship('AdminUser', backref='cms_pages')

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    excerpt = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # 'numerology', 'tips', 'testimonials'
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    featured_image = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    author = db.relationship('AdminUser', backref='blog_posts')

class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # 'payment', 'reports', 'general'
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5 stars
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)

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
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
