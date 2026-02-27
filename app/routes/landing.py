from flask import Blueprint, render_template

bp = Blueprint('landing', __name__)

@bp.route('/welcome')
def index():
    return render_template('landing.html')