from flask import Flask, render_template, request, redirect, url_for, jsonify
from motor.stepper import StepperMotor
from motor.servo import ServoMotor
from motor.scale import Scale

import json
import argparse
import os
import glob

app = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Bar Robot Application')
parser.add_argument('-quick', action='store_true', help='Skip initialization and move stepper to Standartposition')
args = parser.parse_args()

# Initialize motors
stepper = StepperMotor()
servo = ServoMotor()
scale = Scale()

# Load liquid mappings from JSON file
with open('./json/liquids_mapping.json') as f:
    liquids = json.load(f)
    
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

@app.route('/shutdown')
def shutdown():
    # Shutdown all motors and return a shutdown message
    stepper.shutdown()
    servo.shutdown()
    scale.shutdown()
    return "System shutdown complete."

if __name__ == '__main__':
    app.run(debug=False)
