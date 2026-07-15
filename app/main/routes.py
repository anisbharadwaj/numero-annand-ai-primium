from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index_route():
    return render_template('index.html')

@main_bp.route('/pricing')
def pricing_route():
    return render_template('pricing.html')
