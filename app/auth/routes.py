from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User
from flask_login import login_user, logout_user, login_required
import pyotp

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email/password and TOTP setup."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Input validation should be more robust in reality
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return redirect(url_for('auth.register'))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please set up 2FA.', 'success')
        # After account creation, redirect to TOTP setup page
        return redirect(url_for('auth.setup_2fa', email=email))
    return render_template('register.html')

@auth_bp.route('/setup-2fa')
def setup_2fa():
    """Show QR code for TOTP setup (Google Authenticator)."""
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first_or_404()
    uri = user.get_totp_uri()
    return render_template('setup_2fa.html', otp_uri=uri)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Email/password login (then 2FA)."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Temporarily store user id in session for 2FA
            request.session = {'2fa_user_id': user.id}
            return redirect(url_for('auth.two_factor'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """TOTP verification step."""
    if '2fa_user_id' not in request.session:
        return redirect(url_for('auth.login'))
    user = User.query.get(request.session['2fa_user_id'])
    if request.method == 'POST':
        token = request.form['token']
        if user.verify_totp(token):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid 2FA token', 'danger')
    return render_template('two_factor.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the user."""
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('main.index'))
