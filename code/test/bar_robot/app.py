from flask import Flask, render_template, request, redirect, url_for, jsonify
from motor.stepper import StepperMotor
from motor.servo import ServoMotor
from motor.scale import Scale
import json

app = Flask(__name__)

# Initialize motors
stepper = StepperMotor()
servo = ServoMotor()
scale = Scale()

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
    if sequence:
        stepper.execute_sequence(sequence)
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

@app.route('/stepper/move', methods=['POST'])
def move_stepper():
    position = request.form['position']
    stepper.move_to_position(position)
    return redirect(url_for('stepper_status'))

@app.route('/servo/move', methods=['POST'])
def move_servo():
    position = request.form['position']
    servo.move_to_position(position)
    return redirect(url_for('servo_status'))

if __name__ == '__main__':
    app.run(debug=True)
