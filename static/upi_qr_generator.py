import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Payment details
UPI_ID = "7099805039-2@ybl"
NAME = "ANANDA SARMAH"

# UPI payment link
upi_url = (
    f"upi://pay?"
    f"pa={UPI_ID}"
    f"&pn={NAME}"
    f"&mc=0000"
    f"&mode=02"
    f"&purpose=00"
)

# Create QR
qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_H,
    box_size=12,
    border=4,
)

qr.add_data(upi_url)
qr.make(fit=True)

img = qr.make_image(
    fill_color="black",
    back_color="white"
)

img.save("upi_payment_qr.png")

print("QR generated successfully!")
print("UPI:", UPI_ID)
