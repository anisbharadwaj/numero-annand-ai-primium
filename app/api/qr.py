import os
import io
import base64
from flask import Blueprint, jsonify, current_app, send_file, Response
from app.models import Order
import segno

qr_bp = Blueprint('api_qr', __name__)

# UPI Configuration
UPI_ID = '7099805039-2@axl'
PAYEE_NAME = 'Ananda Sarmah'
CURRENCY = 'INR'

def generate_upi_qr(amount, order_id):
    """Generate a UPI QR code for the given amount and order ID."""
    # UPI deep link format: upi://pay?pa=UPI_ID&pn=PAYEE_NAME&am=AMOUNT&tr=TRANSACTION_REF&tn=DESCRIPTION
    upi_string = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME.replace(' ', '%20')}&am={amount}&tr={order_id}&cu={CURRENCY}&tn=Numerology%20Report%20Order%20{order_id}"
    
    # Generate QR code using segno
    qr = segno.make(upi_string, version=1, mode='byte', error='m', micro=False)
    
    # Create PNG image in memory
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=8, border=1)  # scale=8 for good resolution
    buffer.seek(0)
    
    return buffer

@qr_bp.route('/api/qr/order/<int:order_id>', methods=['GET'])
def order_qr(order_id):
    """Generate and return a QR code image for an order payment."""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Generate the QR code
        qr_buffer = generate_upi_qr(order.amount, order_id)
        
        # Return as PNG image
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'payment_qr_{order_id}.png'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/api/qr/preview/<int:amount>', methods=['GET'])
def preview_qr(amount):
    """Generate a preview QR code for the given amount (no order ID)."""
    try:
        # Use a preview transaction reference
        preview_ref = f'PREVIEW_{amount}'
        
        # Generate the QR code
        qr_buffer = generate_upi_qr(amount, preview_ref)
        
        # Return as PNG image
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'payment_qr_preview_{amount}.png'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/api/qr', methods=['GET'])
def get_payment_qr():
    """Legacy endpoint - returns info about the QR system."""
    return jsonify({
        "status": "success",
        "message": "Dynamic QR code generation is active",
        "upi_id": UPI_ID,
        "payee": PAYEE_NAME,
        "endpoints": {
            "order_qr": "/api/qr/order/<order_id>",
            "preview_qr": "/api/qr/preview/<amount>"
        }
    })
=======
UPI_ID = os.getenv('UPI_ID', '7099805039-2@axl')
UPI_PAYEE = os.getenv('UPI_PAYEE', 'Ananda Sarmah')

def generate_qr():
    """Generate dynamic UPI QR code"""
    amount = request.args.get('amount', '201')
    transaction_note = request.args.get('note', 'Numero Annand AI Premium')
    
    # Build UPI URI
    upi_uri = (
        f"upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={UPI_PAYEE}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={transaction_note.replace(' ', '%20')}"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return send_file(
        img_bytes,
        mimetype='image/png',
        as_attachment=False,
        download_name='payment_qr.png'
    )

def generate_qr_data(amount=201, note='Numero Annand AI Premium'):
    """Generate QR code data as base64 for JSON responses"""
    import base64
    
    upi_uri = (
        f"upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={UPI_PAYEE}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={note.replace(' ', '%20')}"
    )
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    base64_str = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"
>>>>>>> origin/main
