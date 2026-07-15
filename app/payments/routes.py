import base64
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Order

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    package = request.args.get('package', 'digital')
    amount = 201 if package == 'digital' else 501
    report_type = "Digital PDF Report" if package == 'digital' else "Printed Premium Report"

    if request.method == 'POST':
        # File parsing to base64
        screenshot_file = request.files.get('screenshot')
        screenshot_b64 = ""
        if screenshot_file and screenshot_file.filename != '':
            screenshot_b64 = base64.b64encode(screenshot_file.read()).decode('utf-8')

        new_order = Order(
            name=request.form.get('name'),
            dob=request.form.get('dob'),
            birth_time=request.form.get('birth_time'),
            birth_place=request.form.get('birth_place'),
            mobile=request.form.get('mobile'),
            email=request.form.get('email'),
            gender=request.form.get('gender'),
            language=request.form.get('language'),
            report_type=request.form.get('report_type'),
            address=request.form.get('address', ''),
            amount=int(request.form.get('amount')),
            utr=request.form.get('utr'),
            screenshot_base64=screenshot_b64,
            payment_status='Pending'
        )
        try:
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('payments.success', order_id=new_order.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating application request. Double check if UTR was used before.', 'danger')

    return render_template('checkout.html', amount=amount, report_type=report_type)

@payments_bp.route('/payment')
def payment_screen():
    amount = request.args.get('amount', '201')
    return render_template('payment.html', amount=amount)

@payments_bp.route('/success/<int:order_id>')
def success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('success.html', order=order)

@payments_bp.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('dashboard.html', orders=orders)

@payments_bp.route('/verify/<int:order_id>/<string:status>')
@login_required
def verify_payment(order_id, status):
    if status not in ['Verified', 'Rejected']:
        flash('Invalid status assignment.', 'danger')
        return redirect(url_for('payments.dashboard'))
        
    order = Order.query.get_or_404(order_id)
    order.payment_status = status
    db.session.commit()
    flash(f'Order ID #{order.id} status modified to {status} successfully.', 'success')
    return redirect(url_for('payments.dashboard'))
