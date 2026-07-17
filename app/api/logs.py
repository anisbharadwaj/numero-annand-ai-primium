"""Logs API endpoint for Vercel"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request, jsonify
from models import db, Log
from datetime import datetime

def handler():
    """Handle log creation and retrieval"""
    if request.method == 'POST':
        data = request.get_json()
        log = Log(
            user_id=data.get('user_id'),
            action=data.get('action'),
            details=data.get('details'),
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'status': 'logged'}), 201
    
    logs = Log.query.order_by(Log.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': l.id,
        'user_id': l.user_id,
        'action': l.action,
        'details': l.details,
        'created_at': l.created_at.isoformat()
    } for l in logs])
