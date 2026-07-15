"""
QR Code Auto Generator for Numero Annand AI Premium
Uses Python QRCode library - no external websites needed
Generates QR dynamically based on amount
"""

import qrcode
import qrcode.constants
import base64
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

UPI_ID = os.getenv('UPI_ID', '7099805039-2@axl')
UPI_PAYEE = os.getenv('UPI_PAYEE', 'Ananda Sarmah')

def generate_upi_uri(amount: float, note: str = "Numero Annand AI Premium") -> str:
    """Generate UPI payment URI dynamically"""
    return (
        f"upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={UPI_PAYEE}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={note.replace(' ', '%20')}"
    )

def generate_qr_png(amount: float = 201, note: str = "Numero Annand AI Premium") -> BytesIO:
    """Generate QR code image and return as PNG bytes"""
    upi_uri = generate_upi_uri(amount, note)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def generate_qr_base64(amount: float = 201, note: str = "Numero Annand AI Premium") -> str:
    """Generate QR and return base64 data URI"""
    img_bytes = generate_qr_png(amount, note)
    b64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"

def get_upi_deep_link(amount: float = 201, note: str = "Numero Annand AI Premium") -> str:
    """Get the UPI deep link for direct payment apps"""
    return generate_upi_uri(amount, note)

# Quick test
if __name__ == "__main__":
    # Test QR generation for ₹201
    qr_base64 = generate_qr_base64(201)
    print(f"✅ QR Generated for ₹201")
    print(f"Base64 length: {len(qr_base64)} chars")
    print(f"UPI URI: {generate_upi_uri(201)}")
    
    # Test QR generation for ₹501
    qr_base64_501 = generate_qr_base64(501)
    print(f"✅ QR Generated for ₹501")
    print(f"UPI URI: {generate_upi_uri(501)}")
