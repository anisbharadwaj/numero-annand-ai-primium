import os
import base64
from flask import Blueprint, jsonify, current_app

qr_bp = Blueprint('api_qr', __name__)

@qr_bp.route('/api/qr', methods=['GET'])
def get_payment_qr():
    try:
        # Calculate the absolute location of your uploaded image file on Vercel
        static_dir = current_app.static_folder
        image_path = os.path.join(static_dir, 'images', 'payment_qr.png')
        
        # Safe structural check to prevent missing file layout errors
        if not os.path.exists(image_path):
            return jsonify({
                "status": "error", 
                "message": "Target original payment_qr.png asset file not found in static/images/ directory."
            }), 404
            
        # Read your exact binary image data and convert it safely to a web stream layout
        with open(image_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            
        return jsonify({
            "status": "success",
            "data": {
                "qr_image_base64": f"data:image/png;base64,{base64_data}"
            }
        }), 200
        
    except Exception:
        return jsonify({"status": "error", "message": "Failed to compile image metadata stream."}), 500
