from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from servo_moves import ServoMoves
from servo import Servo
from config import ConfigManager
import views

class FlaskApp:
    def __init__(self, config_file: str):
        self.config_manager = ConfigManager(config_file)
        self.config_file = 'config.json'

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.config_manager.get('secret_key')
        self.socketio = SocketIO(self.app)

        print("Initializing ServoMoves in FlaskApp")
        self.servo_move = ServoMoves(step_pin=self.config_manager.get('step_pin'), 
                                     direction_pin=self.config_manager.get('direction_pin'), 
                                     enable_pin=self.config_manager.get('enable_pin'),
                                     socketio=self.socketio,
                                     velocity_settings=self.config_manager.get('velocity_settings'),
                                     config_file=self.config_file
                                    )
        
        print("Initializing Servo in FlaskApp")
        self.servo = Servo(positions=self.config_manager.get('servo_steps'), 
                           step_pin=self.config_manager.get('step_pin'), 
                           direction_pin=self.config_manager.get('direction_pin'), 
                           enable_pin=self.config_manager.get('enable_pin'),
                           socketio=self.socketio,
                           velocity_settings=self.config_manager.get('velocity_settings'),
                           distance_thresholds=self.config_manager.get('distance_thresholds'),
                           config_file=self.config_file)
        

        
        self.views = views.Views(self.app, self.servo, self.servo_move, self.socketio)

    def create_app(self):
        return self.app

    def cleanup(self) -> None:
        self.servo_move.cleanup()

if __name__ == '__main__':
    config_file = 'config.json'
    config = FlaskApp(config_file)    
    app = config.create_app()

    try:
        while True:
            step = input("Enter the position (e.g., pos1, pos2, ... pos10) or 'exit' to quit: ")
            if step.lower() == 'exit':
                break
            if step in config.servo.positions:
                config.servo.move_to(step)
            else:
                print("Invalid position. Please enter a valid position.")
    finally:
        config.cleanup()
