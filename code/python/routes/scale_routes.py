
from flask import Blueprint, render_template

servo_routes = Blueprint('servo_routes', __name__)

@servo_routes.route('/status')
def servo_status():
    return render_template('servo_status.html')
