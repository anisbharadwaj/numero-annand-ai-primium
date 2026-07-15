from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import AdminUser, Order

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_route():
    # Bootstrap fallback admin profile automatically if zero admins present
    if not AdminUser.query.filter_by(username='admin').first():
        default_admin = AdminUser(username='admin')
        default_admin.set_password('AnnandAdmin2026!')
        db.session.add(default_admin)
        db.session.commit()

    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard_route'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('auth.dashboard_route'))
        else:
            flash('Invalid admin secure credentials execution block.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout_route():
    logout_user()
    flash('Logged out out securely.', 'info')
    return redirect(url_for('main.index_route'))

@auth_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard_route():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action') # VERIFY or REJECT
        order = Order.query.get(order_id)
        if order:
            if action == 'VERIFY':
                order.payment_status = 'VERIFIED'
            elif action == 'REJECT':
                order.payment_status = 'REJECTED'
            db.session.commit()
            flash(f"Order reference {order.order_ref} mutated successfully to {order.payment_status}.", "success")
            
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('dashboard.html', orders=orders)
