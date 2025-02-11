from Adafruit_PCA9685 import PCA9685
import time
from fileHandler import FileHandler
from logger import setup_logger

class ServoMotor:
    def __init__(self):
        # Initialize the ServoMotor with logger, PWM, and positions from JSON file
        self.logger = setup_logger()
        self.settingsFileHandler = FileHandler('./bar_robot/settings.json')
        self.settings = self.settingsFileHandler.readSettings()
        
        self.pulse_min = self.settings.get('pulse_min')
        self.pulse_max = self.settings.get('pulse_max')

        self.mid_pos = (self.pulse_max + self.pulse_min) // 2
        self.range = self.pulse_max - self.pulse_min
        self.inactive_pos = self.mid_pos + (self.range // 9) + 20
        self.active_pos = self.mid_pos - (self.range // 9) + 55
        self.waiting_pos = self.mid_pos + (self.range // 9) - 90

        self.current_position = 'inactive'
        
        self.pwm = PCA9685(busnum=1)
        self.pwm.set_pwm_freq(60)
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()

    def move_to_active(self):
        # Move the servo to the active position
        self.logger.info("Moving servo to active position")
        self.pwm.set_pwm(0, 0, self.active_pos)
        time.sleep(1)
        self.current_position = 'active'

    def move_to_inactive(self):
        # Move the servo to the inactive position
        self.logger.info("Moving servo to inactive position")
        self.pwm.set_pwm(0, 0, self.inactive_pos)
        time.sleep(1)
        self.current_position = 'inactive'

    def move_to_waiting(self):
        # Move the servo to the waiting position
        self.logger.info("Moving servo to waiting position")
        self.pwm.set_pwm(0, 0, self.waiting_pos)
        time.sleep(1)
        self.current_position = 'waiting'
        
    def get_status(self):
        # Return the current status of the servo motor
        return {
            'current_position': self.current_position
        }

    def shutdown(self):
        # Shutdown the servo motor and turn off the PWM signal
        self.logger.info("Shutting down servo motor")
        self.move_to_inactive()  # Ensure the servo is in the inactive position
        self.pwm.set_pwm(0, 0, 0)  # Turn off the PWM signal
        self.logger.info("Servo motor shutdown complete")
