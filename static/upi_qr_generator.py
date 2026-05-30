import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Your UPI details
upi_id = "7099805039-2@axl"
name = "Ananda Sarmah"

upi_url = f"upi://pay?pa={upi_id}&pn={name}"

qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_H,
    box_size=10,
    border=4
)

qr.add_data(upi_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

img.save("upi_payment_qr.png")

print("QR generated successfully!")
