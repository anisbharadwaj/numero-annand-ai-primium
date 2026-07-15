import io
import base64
from urllib.parse import quote
import segno
from flask import Blueprint, request, jsonify, current_app

# Blueprint Architecture Setup
qr_bp = Blueprint('api_qr', __name__)

def generate_upi_uri(payee_vpa: str, payee_name: str, transaction_note: str, amount: float = None) -> str:
    """
    Generates a strictly formatted, URL-encoded upi://pay URI standard.
    This eliminates 'Bad URI' errors across strict banking apps (GPay, PhonePe, Paytm).
    """
    # Base mandatory keys for compliant UPI Deep Linking
    # pa: Payee VPA, pn: Payee Name, tn: Transaction Note, am: Amount, cu: Currency Code
    encoded_name = quote(payee_name.strip())
    encoded_note = quote(transaction_note.strip())
    
    uri = f"upi://pay?pa={payee_vpa.strip()}&pn={encoded_name}&tn={encoded_note}&cu=INR"
    
    # Securely append structural parameter formatting if an explicitly valid amount exists
    if amount and amount > 0:
        uri += f"&am={amount:.2f}"
        
    return uri

def generate_qr_base64(uri_string: str) -> str:
    """
    Constructs a structural QR vector image using Segno engine.
    Returns a production-ready clean inline Base64 PNG image stream string.
    """
    # Create the QR code with high-performance error correction capability (Quartile recovery margin)
    qr = segno.make(uri_string, error='Q')
    
    # Save target stream vector properties safely in micro-buffered virtual memory
    buffer = io.BytesIO()
    
    # Render crisp dark themed colors suitable for modern visual design (Scale 10 handles dense payloads cleanly)
    qr.save(
        buffer, 
        kind='png', 
        scale=10, 
        border=2,
        dark='#ffffff',      # High-contrast clean output
        light='#111625'     # Dark canvas theme back-drop alignment 
    )
    
    # Construct precise payload delivery target sequence
    buffer.seek(0)
    base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{base64_data}"

@qr_bp.route('/api/qr', methods=['GET'])
def get_payment_qr():
    """
    Secure REST API endpoint to retrieve dynamically constructed UPI QR codes.
    Accepts: ?amount=201 or ?amount=501
    """
    try:
        # Fetch configurations from parameters or application contexts securely
        payee_vpa = "7099805039@ybl"
        payee_name = "Ananda Sarmah"
        brand_note = "Numero Annand AI Premium Purchase"
        
        # Pull request arguments for standard item tiers safely
        amount_raw = request.args.get('amount')
        amount = None
        
        if amount_raw:
            try:
                # Sanitize conversion safely
                amount = float(amount_raw)
                if amount not in [201.0, 501.0]:
                    return jsonify({
                        "status": "error", 
                        "message": "Invalid payment processing tier asset structure requested."
                    }), 400
            except ValueError:
                return jsonify({
                    "status": "error", 
                    "message": "Malformed amount numeric criteria parameter syntax."
                }), 400

        # Construct optimized compliant deep string structure assets
        upi_uri = generate_upi_uri(
            payee_vpa=payee_vpa,
            payee_name=payee_name,
            transaction_note=brand_note,
            amount=amount
        )
        
        # Render target image output directly
        base64_image = generate_qr_base64(upi_uri)
        
        return jsonify({
            "status": "success",
            "data": {
                "upi_url": upi_uri,
                "qr_image_base64": base64_image,
                "meta": {
                    "amount": amount if amount else "user_defined",
                    "payee": payee_name,
                    "vpa": payee_vpa
                }
            }
        }), 200

    except Exception as e:
        # Prevent details leakage on core internal engine trace configurations
        return jsonify({
            "status": "error", 
            "message": "An internal system anomaly occurred while building the dynamic QR payload transaction asset."
        }), 500
