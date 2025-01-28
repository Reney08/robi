
from flask import Blueprint, render_template

servo_routes = Blueprint('scale_routes', __name__)

@servo_routes.route('/status')
def servo_status():
    return render_template('scale_status.html')
