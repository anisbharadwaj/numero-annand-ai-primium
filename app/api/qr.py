from flask import request, jsonify, send_file
import qrcode
import qrcode.image.svg
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

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
