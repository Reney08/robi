
from flask import Blueprint, render_template, request, jsonify
# from flask_socketio import emit
# import RPi.GPIO as GPIO

class Views:
    def __init__(self, app, servo, servo_moves, socketio):
        self.app = app
        self.servo = servo
        self.servo_moves = servo_moves
        self.socketio = socketio
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', step_count=self.servo_moves.get_current_pos())

        @self.app.route('/move', methods=['POST'])
        def move():
            direction = request.json.get('direction')
            steps = request.json.get('steps', 1)  # Default to 1 step if not provided
            print(f"Received request: direction={direction}, steps={steps}")

            if direction == 'left':
                self.servo_moves.go_left(steps)
            elif direction == 'right':
                self.servo_moves.go_right(steps)

            step_count = self.servo_moves.get_current_pos()
            self.socketio.emit('update_step_count', {'step_count': step_count})
            return jsonify(step_count=step_count)

        @self.app.route('/move_to_position', methods=['POST'])
        def move_to_position():
            position = request.json.get('position')
            self.servo.move_to(position)
            step_count = self.servo_moves.get_current_pos()
            self.socketio.emit('update_step_count', {'step_count': step_count})
            return jsonify(step_count=step_count)
