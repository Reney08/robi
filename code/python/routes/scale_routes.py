from flask import Blueprint, render_template

scale_routes = Blueprint('scale_routes', __name__)

@scale_routes.route('/status')
def scale_status():
    return render_template('scale_status.html')
