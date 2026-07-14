from flask import Blueprint, jsonify
import os

api_logs_bp = Blueprint('api_logs', __name__, url_prefix='/api/logs')

@api_logs_bp.route('/')
def tail_logs():
    """Return the last 50 lines of the application log."""
    try:
        with open('logs/app.log', 'r') as f:
            lines = f.readlines()
        last_lines = lines[-50:] if len(lines) > 50 else lines
        return jsonify(logs=last_lines)
    except Exception as e:
        return jsonify(error="Could not read logs", detail=str(e)), 500
