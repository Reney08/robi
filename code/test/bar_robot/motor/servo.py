from Adafruit_PCA9685 import PCA9685
import time
from fileHandler import FileHandler
from logger import setup_logger

class ServoMotor:
    def __init__(self):
        self.logger = setup_logger()
        self.pwm = PCA9685(busnum=1)
        self.pwm.set_pwm_freq(60)
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()
        self.inactive_pos = 375
        self.active_pos = 325

    def move_to_position(self, position):
        if position == 'active':
            self.pwm.set_pwm(0, 0, self.active_pos)
        else:
            self.pwm.set_pwm(0, 0, self.inactive_pos)
        time.sleep(1)

    def get_status(self):
        return {
            'current_position': 'active' if self.pwm.get_pwm(0) == self.active_pos else 'inactive'
        }
