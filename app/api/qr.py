import io
import base64
from urllib.parse import quote
import segno
from flask import Blueprint, request, jsonify

qr_bp = Blueprint('api_qr', __name__)

@qr_bp.route('/api/qr', methods=['GET'])
def get_payment_qr():
    try:
        # UPDATED: Using your exact PhonePe verified merchant details
        payee_vpa = "7099805039-2@axl"
        payee_name = quote("Ananda Sarmah")
        transaction_note = quote("Numero Annand AI Premium")
        
        # Safely pull transaction amounts (₹201 or ₹501)
        amount_raw = request.args.get('amount', '201')
        
        # Build the correct deep link protocol structure
        upi_uri = f"upi://pay?pa={payee_vpa}&pn={payee_name}&tn={transaction_note}&am={amount_raw}&cu=INR"
        
        # Create a scannable, clean QR grid layout
        qr = segno.make(upi_uri, error='L')
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=8, border=2)
        buffer.seek(0)
        
        base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return jsonify({
            "status": "success",
            "data": {
                "upi_url": upi_uri,
                "qr_image_base64": f"data:image/png;base64,{base64_image}"
            }
        }), 200
        
    except Exception:
        return jsonify({"status": "error", "message": "Failed to generate clear QR payload."}), 500
