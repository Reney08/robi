from flask import Flask, render_template, request, redirect, url_for, jsonify
from motor.stepper import StepperMotor
from motor.servo import ServoMotor
from motor.scale import Scale
from motor.pump import Pump
from fileHandler import FileHandler
from flask_sqlalchemy import SQLAlchemy
from databaseHandler import DatabaseHandler, db

import json
import argparse
import os
import glob

app = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Bar Robot Application')
parser.add_argument('-quick', action='store_true', help='Skip initialization and move stepper to Standartposition')
args = parser.parse_args()


# Initialize FileHandler for settings
settingsFileHandler = FileHandler('./json/settings.json')
settings = settingsFileHandler.readJson()

# Load liquid mappings from JSON file
with open('./json/liquids_mapping.json') as f:
    liquids = json.load(f)


#Database Configuration
#DB_USERNAME = "robi"
#DB_PASSWORD = "Keins123!"
#DB_NAME = "barroboterdatabase"
#DB_HOST = "localhost"
#DB_PORT = "3306"

#app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@localhost/{DB_NAME}"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#db_handler = DatabaseHandler(app)

# Initialize motors
stepper = StepperMotor()
servo = ServoMotor(address=0x41, channel=0)
pump1 = Pump(address=0x40, channel=0)
scale = Scale()
    
# Ensure stepper motor is initialized
if args.quick:
    stepper.load_positions()  # Load max_pos from positions.json
    stepper.quick_init()
    stepper.initialized = True
else:
    stepper.init()

@app.route('/')
def index():
    # List all cocktail JSON files and render the index page
    cocktail_files = glob.glob('./json/cocktails/*.json')
    cocktails = [os.path.splitext(os.path.basename(file))[0] for file in cocktail_files]
    # cocktails = db_handler.get_all_cocktails()
    return render_template('index.html', cocktails=cocktails)

@app.route('/<selected_cocktail>')
def selected_cocktail(selected_cocktail):
    # Load ingredients for the selected cocktail and render the page
    ingredients_file = f'./json/cocktails/{selected_cocktail}.json'
    if os.path.exists(ingredients_file):
        with open(ingredients_file) as f:
            ingredients = json.load(f)
    else:
        ingredients = {}
    return render_template('selected_cocktail.html', cocktail=selected_cocktail, ingredients=ingredients)

@app.route('/start_mixing', methods=['POST'])
def start_mixing():
    # Start mixing the selected cocktail
    cocktail = request.form['cocktail']
    with open(f'./json/cocktails/{cocktail}.json') as f:
        ingredients = json.load(f)
    
    sequence = []
    for ingredient, volume in ingredients.items():
        if volume > 0:
            position = liquids[ingredient]
            times = volume // 25
            for _ in range(times):
                sequence.append({"position": position, "wait_time": 5})
    
    sequence.append({"position": "finished", "wait_time": 10})
    
    stepper.execute_sequence(sequence)
    return redirect(url_for('index'))
    
@app.route('/status')
def status():
    # Render the status page
    return render_template('status.html')

@app.route('/stepper/status')
def stepper_status():
    # Get and render the status of the stepper motor
    status = stepper.get_status()
    return render_template('stepper_status.html', status=status)

@app.route('/servo/status')
def servo_status():
    # Get and render the status of the servo motor
    status = servo.get_status()
    return render_template('servo_status.html', status=status)

@app.route('/scale/status')
def scale_status():
    # Get and render the weight from the scale
    weight = scale.get_weight()
    return render_template('scale_status.html', weight=weight)

@app.route('/stepper/move', methods=['GET', 'POST'])
def stepper_move():
    # Handle stepper motor movements and render the move page
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'move_and_save':
                steps = int(request.form['steps'])
                position_name = request.form['position_name']
                stepper.move_and_save_position(steps, position_name)
            elif action == 'edit_position':
                position_name = request.form['position_name']
                new_value = int(request.form['new_value'])
                stepper.edit_position(position_name, new_value)
            elif action == 'delete_position':
                position_name = request.form['position_name']
                stepper.delete_position(position_name)
            elif action == 'move_to_standartPos':
                stepper.move_to_position(stepper.standartPos)
            return redirect(url_for('stepper_move'))
        except KeyError:
            return "Bad Request: Missing form data.", 400

    return render_template('stepper_move.html', null_position=stepper.nullPos, max_position=stepper.maxPos, positions=stepper.positions)

@app.route('/scale/weight')
def scale_weight():
    # Get the weight from the scale and return it as JSON
    weight = scale.get_weight()
    if weight is not None:
        return jsonify({'weight': weight})
    return jsonify({'error': 'Scale is inactive.'})

@app.route('/scale/activate', methods=['POST'])
def scale_activate():
    # Activate the scale and return the status as JSON
    scale.activate()
    return jsonify({'status': 'Scale activated'})

@app.route('/scale/deactivate', methods=['POST'])
def scale_deactivate():
    # Deactivate the scale and return the status as JSON
    scale.deactivate()
    return jsonify({'status': 'Scale deactivated'})

@app.route('/pump', methods=['GET', 'POST'])
def pump():
    """Handle pump status retrieval and control pump movement."""
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'activate':
                pump1.activate()
            elif action == 'deactivate':
                pump1.deactivate()
            elif action == 'set_pwm':
                new_pwm = int(request.form.get('pwm_value'))
                if pump1.pulse_min <= new_pwm <= pump1.pulse_max:
                    pump1.pca.set_pwm(pump1.channel, 0, new_pwm)
                    pump1.active_pos = new_pwm
                else:
                    return "Bad Request: PWM value out of range.", 400
            return redirect(url_for('pump'))
        except (KeyError, ValueError):
            return "Bad Request: Invalid input.", 400

    elif request.method == 'GET':
        status = pump1.get_status()
        return jsonify({
            'status': status['current_position'],
            'pwm_value': pump1.active_pos if status['current_position'] == 'active' else pump1.inactive_pos
        })

    return render_template('pump.html', status=pump1.get_status(), min_pwm=pump1.pulse_min, max_pwm=pump1.pulse_max)

@app.route('/shutdown')
def shutdown():
    # Shutdown all motors and return a shutdown message
    stepper.shutdown()
    servo.shutdown()
    scale.shutdown()
    exit()
    return "System shutdown complete."

if __name__ == '__main__':
    app.run(debug=False)
