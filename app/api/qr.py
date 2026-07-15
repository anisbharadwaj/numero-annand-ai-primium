import io
import urllib.parse
from flask import Blueprint, send_file, request, current_app, jsonify
import qrcode
from app.models import Order

api_bp = Blueprint('api', __name__)

@api_bp.route('/qr/<string:order_ref>')
def generate_upi_qr(order_ref):
    order = Order.query.filter_by(order_ref=order_ref).first_or_404()
    
    # Base configuration bindings
    upi_id = current_app.config['UPI_ID']
    payee_name = current_app.config['PAYEE_NAME']
    transaction_note = f"Numero Annand AI Order {order_ref}"
    amount = f"{order.amount}.00"
    
    # Safely escape parameters to construct valid banking protocol link
    params = {
        "pa": upi_id,
        "pn": payee_name,
        "tn": transaction_note,
        "am": amount,
        "cu": "INR"
    }
    
    # Construct target raw string
    upi_uri = f"upi://pay?{urllib.parse.urlencode(params)}"
    
    # Generate QR memory payload
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@api_bp.route('/orders/<string:order_ref>', methods=['GET'])
def get_order_status(order_ref):
    order = Order.query.filter_by(order_ref=order_ref).first_or_404()
    return jsonify({
        "order_ref": order.order_ref,
        "payment_status": order.payment_status,
        "amount": order.amount
    })
