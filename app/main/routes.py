from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Order, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    pending_count = Order.query.filter_by(payment_status='pending').count()
    completed_count = Order.query.filter_by(payment_status='completed').count()
    
    # Calculate sum total securely 
    revenue_query = db.session.query(db.func.sum(Order.amount)).filter_by(payment_status='completed').scalar()
    total_revenue = revenue_query if revenue_query else 0
    
    return render_template(
        'dashboard.html', 
        orders=orders, 
        pending_count=pending_count, 
        completed_count=completed_count,
        total_revenue=total_revenue
    )
