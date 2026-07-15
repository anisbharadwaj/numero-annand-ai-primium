from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import AdminUser

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember_me') else False
        
        admin = AdminUser.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin, remember=remember)
            return redirect(url_for('main.dashboard'))
            
        flash("Invalid operator access credentials.", "error")
    return render_template('login.html')

@auth_bp.route('/admin/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash("Session terminated securely.", "success")
    return redirect(url_for('auth.login'))
