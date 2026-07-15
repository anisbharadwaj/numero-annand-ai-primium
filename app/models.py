from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    birth_time = db.Column(db.String(20), nullable=False)
    birth_place = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(30), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')  # Pending, Verified, Rejected
    utr = db.Column(db.String(50), nullable=True, unique=True)
    screenshot_base64 = db.Column(db.Text, nullable=True)  # Base64 string for direct Vercel database handling
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "report_type": self.report_type,
            "amount": self.amount,
            "payment_status": self.payment_status,
            "utr": self.utr,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
