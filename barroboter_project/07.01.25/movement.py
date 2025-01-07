from time import sleep
import RPi.GPIO as GPIO
# from flask_socketio import SocketIO

class Movement:
    def __init__(self, step_pin: int, direction_pin: int, enable_pin: int, socketio, velocity_settings: dict, max_steps=4050, us_delay=950):
        self.step_pin = step_pin
        self.direction_pin = direction_pin
        self.enable_pin = enable_pin
        self.pos = 0
        self.steps = 200
        self.us_delay = us_delay
        self.uS = 0.000001
        self.moving = False
        self.max_steps = max_steps
        self.socketio = socketio
        self.velocity = 0
        self.velocity_settings = velocity_settings

    def set_step_length(self, steps: int) -> None:
        self.steps = steps

    def set_velocity(self, velocity: int) -> None:
        self.velocity = velocity
        if velocity == 0:
            self.us_delay = 0
        elif velocity == 1:
            self.us_delay = self.velocity_settings['velocity_1']
        elif velocity == 2:
            self.us_delay = self.velocity_settings['velocity_2']
        elif velocity == 3:
            self.us_delay = self.velocity_settings['velocity_3']

    def move_to_position(self, target_pos: int) -> None:
        current_pos = self.pos
        if target_pos > current_pos:
            self.accelerate()
            self.move_right(target_pos - current_pos)
            self.decelerate()
        elif target_pos < current_pos:
            self.accelerate()
            self.move_left(current_pos - target_pos)
            self.decelerate()

    def accelerate(self) -> None:
        for v in range(1, self.velocity + 1):
            self.set_velocity(v)
            sleep(0.5)  # Adjust the sleep time as needed for smoother acceleration

    def decelerate(self) -> None:
        for v in range(self.velocity, 0, -1):
            self.set_velocity(v)
            sleep(0.5)  # Adjust the sleep time as needed for smoother deceleration

    def move_right(self, steps: int) -> None:
        GPIO.output(self.direction_pin, GPIO.HIGH)
        for i in range(steps):
            if self.pos >= self.max_steps:
                print("Reached maximum steps")
                continue
            delay = self.uS * self.us_delay
            GPIO.output(self.step_pin, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            sleep(delay)
            self.pos += 1
            self.socketio.emit('update_step_count', {'step_count': self.pos})
            print(f"Moving right: current position = {self.pos}")

    def move_left(self, steps: int) -> None:
        GPIO.output(self.direction_pin, GPIO.LOW)
        for i in range(steps):
            if self.pos <= 0:
                print("Reached minimum steps")
                continue
            delay = self.uS * self.us_delay
            GPIO.output(self.step_pin, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            sleep(delay)
            self.pos -= 1
            self.socketio.emit('update_step_count', {'step_count': self.pos})
            print(f"Moving left: current position = {self.pos}")

    def get_current_pos(self) -> int:
        return self.pos

    def set_current_pos(self, value: int) -> None:
        self.pos = value
        self.pos = value
