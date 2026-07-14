from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models import StudyResource

studyiq_bp = Blueprint('studyiq', __name__, template_folder='templates')

@studyiq_bp.route('/')
@login_required
def study_home():
    """StudyIQ home: list categories or featured playlists."""
    resources = StudyResource.query.all()
    return render_template('studyiq.html', resources=resources)

@studyiq_bp.route('/search')
@login_required
def search_resources():
    """Search resources by query parameter."""
    query = request.args.get('q', '')
    results = StudyResource.query.filter(StudyResource.title.contains(query)).all()
    return render_template('studyiq.html', resources=results)

@studyiq_bp.route('/bookmark/<int:res_id>')
@login_required
def bookmark(res_id):
    """(Stub) Bookmark a resource for the user."""
    # Implementation left as exercise (would require user-specific bookmarks table)
    flash('Bookmarked!', 'info')
    return redirect(url_for('studyiq.study_home'))
