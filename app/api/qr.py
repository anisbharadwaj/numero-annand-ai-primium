from flask import Blueprint, request
from upi_qr_generator import generate_qr

api_qr_bp = Blueprint("api_qr", __name__)

@api_qr_bp.route("/api/qr")
def qr():

    amount = request.args.get("amount", "201")
    customer = request.args.get("name", "Customer")

    return generate_qr(amount, customer)
