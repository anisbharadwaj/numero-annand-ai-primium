import io
import urllib.parse
import qrcode
from flask import Blueprint, request, send_file, jsonify
from app.models import Order

api_bp = Blueprint('api', __name__)

@api_bp.route('/qr')
def generate_upi_qr():
    amount = request.args.get('amount', '201')
    upi_id = "7099805039@ybl"
    payee_name = "Ananda Sarmah"
    transaction_note = "Numero Annand AI Premium Purchase"

    # Precise RFC compliant structure URL-encoded to clean "Bad URI" errors across applications
    upi_payload = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(payee_name)}&tn={urllib.parse.quote(transaction_note)}&am={amount}&cu=INR"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@api_bp.route('/orders', methods=['GET'])
def get_orders_api():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])
