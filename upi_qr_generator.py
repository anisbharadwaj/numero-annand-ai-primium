"""
Simple UPI QR code generator using the `qrcode` library.
This replaces any missing script for QR code generation.
"""
import qrcode

def generate_qr(upi_id, payee_name='StudyIQ', amount='', note='', save_path='upi_qr.png'):
    """
    Generate a UPI QR code and save as PNG.
    upi_id: UPI ID (e.g. 'abc@upi')
    payee_name: Recipient name
    amount:   Amount string (e.g. '100')
    note:     Transaction note
    save_path: file path to save PNG
    Returns the file path.
    """
    # Construct UPI payment URI (per UPI spec)
    upi_uri = f"upi://pay?pa={upi_id}&pn={payee_name}"
    if amount:
        upi_uri += f"&am={amount}"
    if note:
        upi_uri += f"&tn={note}"
    upi_uri += "&cu=INR"  # currency

    # Generate QR code image
    qr_img = qrcode.make(upi_uri)
    qr_img.save(save_path)
    return save_path
