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
    cocktail_files = glob.glob('./json/cocktails/*.json')
    cocktails = [os.path.splitext(os.path.basename(file))[0] for file in cocktail_files]
    return render_template('index.html', cocktails=cocktails)

@app.route('/<selected_cocktail>')
def selected_cocktail(selected_cocktail):
    ingredients_file = f'./json/cocktails/{selected_cocktail}.json'
    if os.path.exists(ingredients_file):
        with open(ingredients_file) as f:
            ingredients = json.load(f)
    else:
        ingredients = {}
    return render_template('selected_cocktail.html', cocktail=selected_cocktail, ingredients=ingredients)

@app.route('/start_mixing', methods=['POST'])
def start_mixing():
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
    return render_template('status.html')

@app.route('/stepper/status')
def stepper_status():
    status = stepper.get_status()
    return render_template('stepper_status.html', status=status)

@app.route('/servo/status')
def servo_status():
    status = servo.get_status()
    return render_template('servo_status.html', status=status)

@app.route('/scale/status')
def scale_status():
    status = scale.get_status()
    return render_template('scale_status.html', status=status)

@app.route('/scale/weight')
def scale_weight():
    if args.scale:
        weight = scale.get_weight()
        if weight is not None:
            return jsonify({'weight': weight})
        return jsonify({'error': 'Scale is inactive.'})
    return jsonify({'error': 'Scale is not activated.'})

@app.route('/scale/activate', methods=['POST'])
def scale_activate():
    if args.scale:
        scale.activate()
        return jsonify({'status': 'Scale activated'})
    return jsonify({'error': 'Scale is not activated.'})

@app.route('/scale/deactivate', methods=['POST'])
def scale_deactivate():
    if args.scale:
        scale.deactivate()
        return jsonify({'status': 'Scale deactivated'})
    return jsonify({'error': 'Scale is not activated.'})


@app.route('/servo/move', methods=['GET', 'POST'])
def servo_move():
    if request.method == 'POST':
        if 'inactive_pos' in request.form and 'active_pos' in request.form and 'waiting_pos' in request.form:
            # Handle updating servo positions
            inactive_pos = int(request.form['inactive_pos'])
            active_pos = int(request.form['active_pos'])
            waiting_pos = int(request.form['waiting_pos'])
            
            servo.inactive_pos = inactive_pos
            servo.active_pos = active_pos
            servo.waiting_pos = waiting_pos
            
            return redirect(url_for('servo_status'))
        else:
            # Handle moving the servo
            position = request.form['position']
            if position == 'active':
                servo.move_to_active()
            elif position == 'inactive':
                servo.move_to_inactive()
            elif position == 'waiting':
                servo.move_to_waiting()
            return redirect(url_for('servo_status'))
    
    return render_template('servo_move.html')

@app.route('/stepper/move', methods=['GET', 'POST'])
def stepper_move():
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

@app.route('/shutdown')
def shutdown():
    stepper.shutdown()
    servo.shutdown()
    scale.shutdown()
    return "System shutdown complete."

if __name__ == '__main__':
    app.run(debug=False)
