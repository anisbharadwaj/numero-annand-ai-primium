from flask import Blueprint, jsonify
from app.models import StudyResource

api_studyiq_bp = Blueprint('api_studyiq', __name__, url_prefix='/api/studyiq')

@api_studyiq_bp.route('/resources')
def get_resources():
    """Return all study resources as JSON."""
    resources = StudyResource.query.all()
    data = [{'id': r.id, 'title': r.title, 'url': r.url, 'category': r.category}
            for r in resources]
    return jsonify(resources=data)
