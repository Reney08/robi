from Adafruit_PCA9685 import PCA9685
import time
from fileHandler import FileHandler
from logger import setup_logger

class ServoMotor:
    # Define pulse width ranges (adjust as needed for your servos)
    pulse_min = 150  # Min pulse length out of 4096
    pulse_max = 600  # Max pulse length out of 4096

    mid_pos = (pulse_max + pulse_min) // 2
    range = pulse_max - pulse_min
    inactive_pos = mid_pos + (range // 9) + 50
    active_pos = mid_pos - (range // 9) + 65
    def __init__(self):
        self.logger = setup_logger()
        self.pwm = PCA9685(busnum=1)
        self.pwm.set_pwm_freq(60)
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()
        

    def move_to_active(self):
        self.logger.info("Moving servo to active position")
        self.pwm.set_pwm(0, 0, self.active_pos)
        time.sleep(1)

    def move_to_inactive(self):
        self.logger.info("Moving servo to inactive position")
        self.pwm.set_pwm(0, 0, self.inactive_pos)
        time.sleep(1)

    def get_status(self):
        return {
            'current_position': 'active' if self.pwm.get_pwm(0) == self.active_pos else 'inactive'
        }
