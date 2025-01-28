from flask import Blueprint, render_template

stepper_routes = Blueprint('stepper_routes', __name__)

@stepper_routes.route('/status')
def stepper_status():
    return render_template('stepper_status.html')
