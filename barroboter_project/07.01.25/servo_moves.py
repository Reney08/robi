
from gpio_setup import GPIOSetup
from movement import Movement
from config import ConfigManager

class ServoMoves:
    def __init__(self, step_pin: int, direction_pin: int, enable_pin: int, socketio, velocity_settings: dict, config_file: str):
        self.gpio_setup = GPIOSetup(step_pin, direction_pin, enable_pin)
        self.movement = Movement(step_pin, direction_pin, enable_pin, socketio, velocity_settings=velocity_settings)
        self.config_manager = ConfigManager(config_file=config_file)

    def set_step_length(self, steps: int) -> None:
        self.movement.set_step_length(steps)

    def go_right(self, steps: int) -> None:
        self.movement.move_right(steps)

    def go_left(self, steps: int) -> None:
        self.movement.move_left(steps)

    def get_current_pos(self) -> int:
        return self.movement.get_current_pos()

    def set_current_pos(self, value: int):
        self.movement.set_current_pos(value)

    def set_velocity(self, velocity: int) -> None:
        self.movement.set_velocity(velocity)

    def move_to_position(self, target_pos: int) -> None:
        self.movement.move_to_position(target_pos)

    def cleanup(self) -> None:
        self.gpio_setup.cleanup_gpio()
