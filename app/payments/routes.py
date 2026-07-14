from flask import Blueprint, render_template, request, send_file, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from upi_qr_generator import generate_qr
import os

payments_bp = Blueprint('payments', __name__, template_folder='templates')

@payments_bp.route('/', methods=['GET', 'POST'])
@login_required
def qr_payment():
    """Page to input UPI details and generate QR code."""
    if request.method == 'POST':
        upi = request.form['upi_id']
        name = request.form.get('name', 'StudyIQ')
        amount = request.form.get('amount', '')
        note = request.form.get('note', '')
        try:
            img_path = generate_qr(upi, payee_name=name, amount=amount, note=note,
                                   save_path='static/upi_qr.png')
            return send_file('static/upi_qr.png', mimetype='image/png')
        except Exception as e:
            flash('QR generation failed', 'danger')
    return render_template('payments.html')
