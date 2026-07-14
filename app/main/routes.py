from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import StudyResource, Alert

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    """Home page - if logged in, redirect to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Project and system health dashboard."""
    # For demonstration, we could fetch CPU/memory via psutil here or via JS (see services/monitoring.py).
    return render_template('dashboard.html')

@main_bp.route('/alerts')
@login_required
def alerts():
    """Show active alerts (anomalies, conflicts)."""
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(20).all()
    return render_template('alerts.html', alerts=alerts)
