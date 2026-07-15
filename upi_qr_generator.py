import io
from urllib.parse import quote

import segno
from flask import send_file

# Official PhonePe merchant VPA for Numero Annand AI Premium.
UPI_ID = "7099805039-2@axl"
NAME = "Ananda Sarmah"


def build_upi_uri(amount, customer_name="Customer"):
    """Return a standards-compliant UPI intent string."""
    note = f"Numero Annand AI Premium - {customer_name}"
    return (
        "upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={quote(NAME)}"
        f"&am={amount}"
        "&cu=INR"
        f"&tn={quote(note)}"
    )


def generate_qr(amount, customer_name="Customer"):
    """Generate a dynamic UPI QR PNG for the given amount using segno."""
    upi = build_upi_uri(amount, customer_name)

    qr = segno.make(upi, error="h")
    img = io.BytesIO()
    qr.save(img, kind="png", scale=8, border=2)
    img.seek(0)

    return send_file(img, mimetype="image/png")
