import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.models import db, Order

payments_bp = Blueprint('payments', __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@payments_bp.route('/checkout', methods=['GET'])
def checkout():
    return render_template('checkout.html')

@payments_bp.route('/create-order', methods=['POST'])
def create_order():
    try:
        report_type = request.form.get('report_type')
        amount = int(request.form.get('amount', 201))
        
        new_order = Order(
            name=request.form.get('name'),
            email=request.form.get('email'),
            mobile=request.form.get('mobile'),
            gender=request.form.get('gender'),
            birth_date=request.form.get('birth_date'),
            birth_time=request.form.get('birth_time'),
            birth_place=request.form.get('birth_place'),
            language=request.form.get('language'),
            report_type=report_type,
            amount=amount,
            address=request.form.get('address') if report_type == 'premium' else None
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('payments.pay_order', order_id=new_order.id))
    except Exception:
        flash("Failed to process transaction structure framework parameters.", "error")
        return redirect(url_for('main.index'))

@payments_bp.route('/pay/<int:order_id>', methods=['GET'])
def pay_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('payment.html', order=order)

@payments_bp.route('/submit-proof/<int:order_id>', methods=['POST'])
def submit_proof(order_id):
    order = Order.query.get_or_404(order_id)
    utr = request.form.get('utr', '').strip()
    
    if len(utr) != 12 or not utr.isdigit():
        flash("Invalid UTR layout structural parsing format.", "error")
        return redirect(url_for('payments.pay_order', order_id=order.id))
        
    file = request.files.get('screenshot')
    if file and allowed_file(file.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(f"utr_{utr}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        order.utr = utr
        order.screenshot = filename
        db.session.commit()
        return render_template('success.html', order=order)
        
    flash("Valid proof screenshot attachment required.", "error")
    return redirect(url_for('payments.pay_order', order_id=order.id))

@payments_bp.route('/admin/verify/<int:order_id>', methods=['POST'])
@login_required
def verify_order_payment(order_id):
    order = Order.query.get_or_404(order_id)
    order.payment_status = 'completed'
    db.session.commit()
    flash(f"Order #{order.id} payment verified successfully!", "success")
    return redirect(url_for('main.dashboard'))
