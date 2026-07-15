import io
from urllib.parse import quote

import segno
from flask import Blueprint, send_file, abort

from app.models import Order

qr_bp = Blueprint('api_qr', __name__)

# Official PhonePe merchant VPA for Numero Annand AI Premium.
UPI_ID = "7099805039-2@axl"
PAYEE_NAME = "Ananda Sarmah"


def _upi_uri(amount, note):
    return (
        "upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={quote(PAYEE_NAME)}"
        f"&am={amount}"
        "&cu=INR"
        f"&tn={quote(note)}"
    )


def _png_response(uri):
    qr = segno.make(uri, error="m")
    buf = io.BytesIO()
    # Standard dark-on-light QR for maximum scanner compatibility.
    qr.save(buf, kind="png", scale=9, border=3, dark="#000000", light="#ffffff")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@qr_bp.route('/api/qr/<int:order_id>.png', methods=['GET'])
def order_qr(order_id):
    """Generate an amount-specific UPI QR for a given order."""
    order = Order.query.get_or_404(order_id)
    note = f"Numero Premium Order #{order.id}"
    return _png_response(_upi_uri(order.amount, note))


@qr_bp.route('/api/qr.png', methods=['GET'])
def generic_qr():
    """Generic UPI QR (no fixed amount) for the merchant VPA."""
    uri = (
        "upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={quote(PAYEE_NAME)}"
        "&cu=INR"
        f"&tn={quote('Numero Annand AI Premium')}"
    )
    return _png_response(uri)
