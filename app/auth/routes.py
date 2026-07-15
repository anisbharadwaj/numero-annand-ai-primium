import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        env_user = os.environ.get('ADMIN_USERNAME', 'admin')
        env_pass = os.environ.get('ADMIN_PASSWORD', 'AdminNumeroAnnand2026!')
        
        if username == env_user and password == env_pass:
            user = User("admin", username)
            login_user(user)
            flash('Admin Authentication Successful!', 'success')
            return redirect(url_for('payments.dashboard'))
        else:
            flash('Invalid admin credentials provided.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))
