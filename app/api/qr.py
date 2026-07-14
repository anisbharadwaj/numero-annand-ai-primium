from flask import Blueprint, jsonify, request
from upi_qr_generator import generate_qr
import os
import base64

api_qr_bp = Blueprint('api_qr', __name__, url_prefix='/api/qr')

@api_qr_bp.route('/generate', methods=['GET'])
def api_generate_qr():
    """Generate a UPI QR code and return it as data URI."""
    upi = request.args.get('upi')
    name = request.args.get('name', 'StudyIQ')
    amount = request.args.get('amount', '')
    note = request.args.get('note', '')
    if not upi:
        return jsonify(error="UPI ID is required"), 400
    try:
        img_path = generate_qr(upi, name, amount, note, save_path='temp_qr.png')
        with open(img_path, 'rb') as f:
            img_data = f.read()
        data_uri = "data:image/png;base64," + base64.b64encode(img_data).decode()
        return jsonify(qrData=data_uri)
    except Exception as e:
        return jsonify(error="QR generation failed", detail=str(e)), 500
