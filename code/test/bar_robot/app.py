from flask import Flask, render_template, request, redirect, url_for, jsonify
from motor.stepper import StepperMotor
from motor.servo import ServoMotor
from motor.scale import Scale
import json
import argparse

app = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Bar Robot Application')
parser.add_argument('-quick', action='store_true', help='Skip initialization and move stepper to nullPos + 10')
args = parser.parse_args()

# Initialize motors
stepper = StepperMotor()
servo = ServoMotor()
scale = Scale()

# Ensure stepper motor is initialized
if args.quick:
    stepper.load_max_pos()  # Load max_pos from positions.json
    stepper.move_to_position(stepper.nullPos + 10)
    stepper.aktuellePos = stepper.nullPos + 10
    stepper.initialized = True
else:
    stepper.init()

@app.route('/')
def index():
    with open('./json/available_cocktails.json') as f:
        cocktails = json.load(f)
    return render_template('index.html', cocktails=cocktails)

@app.route('/<selected_cocktail>')
def selected_cocktail(selected_cocktail):
    return render_template('selected_cocktail.html', cocktail=selected_cocktail)

@app.route('/start_mixing', methods=['POST'])
def start_mixing():
    cocktail = request.form['cocktail']
    sequence = stepper.load_sequence(cocktail)
    if sequence:
        stepper.execute_sequence(sequence)
        return redirect(url_for('index'))
    return redirect(url_for('selected_cocktail', selected_cocktail=cocktail))
    
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

@app.route('/servo/move', methods=['POST'])
def move_servo():
    position = request.form['position']
    servo.move_to_position(position)
    return redirect(url_for('servo_status'))

@app.route('/stepper/move', methods=['GET', 'POST'])
def stepper_move():
    if request.method == 'POST':
        try:
            steps = int(request.form['steps'])
            position_name = request.form['position_name']
            target_position = stepper.aktuellePos + steps
            stepper.move_to_position(target_position)

            # Save the new position to positions.json
            stepper.positions[position_name] = stepper.aktuellePos
            with open('./json/positions.json', 'w') as f:
                json.dump(stepper.positions, f, indent=4)

            return redirect(url_for('stepper_status'))
        except KeyError:
            return "Bad Request: Missing form data.", 400

    return render_template('stepper_move.html')

@app.route('/shutdown')
def shutdown():
    stepper.shutdown()
    servo.shutdown()
    scale.shutdown()
    return "System shutdown complete."

if __name__ == '__main__':
    app.run(debug=True)
