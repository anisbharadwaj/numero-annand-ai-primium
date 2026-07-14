from flask import Blueprint, jsonify, current_app
import requests
import os

api_deploy_bp = Blueprint('api_deploy', __name__, url_prefix='/api/deployments')

@api_deploy_bp.route('/')
def list_deployments():
    """Fetch recent deployments from Vercel API."""
    token = current_app.config['VERCEL_TOKEN']
    project = current_app.config['VERCEL_PROJECT']
    if not token or not project:
        return jsonify(error="Vercel not configured"), 500
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://api.vercel.com/v12/projects/{project}/deployments"
    try:
        resp = requests.get(url, headers=headers)
    except Exception as e:
        return jsonify(error="Failed to reach Vercel API", detail=str(e)), 502
    if resp.status_code != 200:
        return jsonify(error="Vercel API error", status=resp.status_code), resp.status_code
    data = resp.json()
    # Return only needed fields to client
    deployments = [{
        'id': d.get('uid'),
        'url': d.get('url'),
        'state': d.get('state'),
        'created': d.get('created'),
        'duration': d.get('duration'),
        'githubCommit': d.get('meta', {}).get('githubCommitSha') or d.get('meta', {}).get('commitId')
    } for d in data.get('deployments', [])]
    return jsonify(deployments=deployments)
