import io
import qrcode
from urllib.parse import quote
from flask import send_file

UPI_ID = "7099805039@ybl"
NAME = "ANANDA SARMAH"

def generate_qr(amount, customer_name="Customer"):
    note = f"Numero Annand AI Premium - {customer_name}"

    upi = (
        f"upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={quote(NAME)}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={quote(note)}"
    )

    qr = qrcode.make(upi)

    img = io.BytesIO()
    qr.save(img, format="PNG")
    img.seek(0)

    return send_file(img, mimetype="image/png")
