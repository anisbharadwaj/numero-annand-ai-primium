import os
import uuid
import urllib.parse
import segno
from io import BytesIO
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import Order, Admin

main_bp = Blueprint("main", __name__)

# --- DYNAMIC UPI QR GENERATION ENDPOINT ---
@main_bp.route("/api/qr")
def generate_upi_qr():
    """Generates a compliant UPI QR image stream dynamically using Segno."""
    amount = request.args.get("amount", "201")
    order_id = request.args.get("order_id", "TEMP")
    
    payee_upi = "7099805039@ybl"
    payee_name = "Ananda Sarmah"
    transaction_note = f"Numero Annand Premium Order {order_id}"
    
    # Strictly URL encode fields to ensure compliance with UPI structural deep linking across apps
    encoded_name = urllib.parse.quote(payee_name)
    encoded_note = urllib.parse.quote(transaction_note)
    
    upi_uri = f"upi://pay?pa={payee_upi}&pn={encoded_name}&tn={encoded_note}&am={amount}&cu=INR"
    
    buffer = BytesIO()
    qrcode = segno.make(upi_uri, error='H')
    qrcode.save(buffer, kind='png', scale=6)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")

# --- USER LANDING & ORDERING UI ---
@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/pricing")
def pricing():
    return render_template("pricing.html")

@main_bp.route("/checkout")
def checkout():
    report_type = request.args.get("type", "digital")
    amount = 501 if report_type == "printed" else 201
    return render_template("checkout.html", report_type=report_type, amount=amount)

@main_bp.route("/process_checkout", methods=["POST"])
def process_checkout():
    try:
        order_id = "NUMANND-" + str(uuid.uuid4().hex[:8]).upper()
        report_type = request.form.get("report_type")
        amount = 501 if report_type == "printed" else 201

        # File Handling for verification screenshots
        file = request.files.get("screenshot")
        filename = None
        if file and file.filename != '':
            filename = secure_filename(f"{order_id}_{file.filename}")
            # Ensure upload folder setup safely within environment context limits
            upload_path = os.path.join(current_app.root_path, '..', 'static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))

        new_order = Order(
            order_id=order_id,
            name=request.form.get("name"),
            dob=request.form.get("dob"),
            birth_time=request.form.get("birth_time"),
            birth_place=request.form.get("birth_place"),
            mobile=request.form.get("mobile"),
            email=request.form.get("email"),
            gender=request.form.get("gender"),
            language=request.form.get("language"),
            report_type=report_type,
            address=request.form.get("address", ""),
            amount=amount,
            utr=request.form.get("utr"),
            screenshot=filename,
            payment_status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for("main.success", order_id=order_id))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while tracking your order submission: {str(e)}", "danger")
        return redirect(url_for("main.pricing"))

@main_bp.route("/success/<order_id>")
def success(order_id):
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    return render_template("success.html", order=order)

# --- ADMIN SYSTEM UTILITIES ---
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    # Automatically seed an initial admin account if none exists for quick start
    if not Admin.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("AnnandAI@2026", method="scrypt")
        default_admin = Admin(username="admin", password_hash=hashed_pw)
        db.session.add(default_admin)
        db.session.commit()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            flash("Welcome back backoffice workspace.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid tracking credentials submitted.", "danger")
    return render_template("login.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("dashboard.html", orders=orders)

@main_bp.route("/admin/verify/<int:order_id>/<string:status>")
@login_required
def verify_payment(order_id, status):
    order = Order.query.get_or_404(order_id)
    if status in ["Verified", "Rejected"]:
        order.payment_status = status
        db.session.commit()
        flash(f"Order {order.order_id} updated status successfully to {status}.", "success")
    return redirect(url_for("main.dashboard"))

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

# --- ERROR PAGE BLOCKS ---
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500
