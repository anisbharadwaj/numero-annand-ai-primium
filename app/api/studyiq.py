"""StudyIQ - Numerology Analysis API endpoint for Vercel"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handler(request):
    """Vercel serverless function for numerology analysis"""
    from flask import jsonify
    from studyiq.routes import analyze_numerology
    
    data = request.get_json() or {}
    result = analyze_numerology(data)
    return jsonify(result)
