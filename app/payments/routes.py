import os
import random
import string
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Order

payments_bp = Blueprint('payments', __name__)

def generate_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@payments_bp.route('/checkout/<string:plan_type>', methods=['GET', 'POST'])
def checkout_route(plan_type):
    # Enforce clear business rules pricing models upfront
    if plan_type == 'printed':
        amount = 501
        report_label = "Premium Printed Report"
    else:
        plan_type = 'digital'
        amount = 201
        report_label = "Digital PDF Report"

    if request.method == 'POST':
        try:
            # Server-Side structural binding parsing
            dob_str = request.form.get('dob')
            dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
            
            ref = generate_reference()
            new_order = Order(
                order_ref=ref,
                name=request.form.get('name'),
                dob=dob_date,
                birth_time=request.form.get('birth_time'),
                birth_place=request.form.get('birth_place'),
                mobile=request.form.get('mobile'),
                email=request.form.get('email'),
                gender=request.form.get('gender'),
                language=request.form.get('language'),
                report_type=plan_type,
                address=request.form.get('address', ''),
                amount=amount,
                payment_status='PENDING'
            )
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('payments.payment_gateway_route', order_ref=ref))
        except Exception as e:
            db.session.rollback()
            flash("Error creating profile mapping. Ensure all input constraints match.", "danger")
            
    return render_template('checkout.html', plan_type=plan_type, amount=amount, report_label=report_label)

@payments_bp.route('/pay/<string:order_ref>', methods=['GET', 'POST'])
def payment_gateway_route(order_ref):
    order = Order.query.filter_by(order_ref=order_ref).first_or_404()
    
    if request.method == 'POST':
        utr = request.form.get('utr')
        file = request.files.get('screenshot')
        
        if not utr or len(utr) < 6:
            flash("Please enter a valid Transaction UTR reference ID.", "warning")
            return render_template('payment.html', order=order)
            
        filename = None
        if file and allowed_file(file.filename):
            sec_filename = secure_filename(file.filename)
            filename = f"{order.order_ref}_{sec_filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
        order.utr = utr
        order.screenshot = filename
        db.session.commit()
        
        return redirect(url_for('payments.success_route', order_ref=order.order_ref))
        
    return render_template('payment.html', order=order)

@payments_bp.route('/success/<string:order_ref>')
def success_route(order_ref):
    order = Order.query.filter_by(order_ref=order_ref).first_or_404()
    return render_template('success.html', order=order)
