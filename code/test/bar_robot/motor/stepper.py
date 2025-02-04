import RPi.GPIO as GPIO
import time
import json
from fileHandler import FileHandler
from logger import setup_logger

class StepperMotor:
    def __init__(self):
        self.logger = setup_logger()
        self.GPIOConfig()
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()
        self.initFileHandler = FileHandler('./json/stepper_init.json')
        self.initSequence = self.initFileHandler.readJson()
        self.aktuellePos = 0
        self.maxPos = 0
        self.nullPos = 0
        self.init()

    def GPIOConfig(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.STEP, GPIO.OUT)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.EN, GPIO.OUT)
        GPIO.setup(self.schalterLinksPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.schalterRechtsPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(self.EN, GPIO.LOW)
        self.logger.info("Setup GPIO")

    def move_to_position(self, target_steps):
        relative_steps = target_steps - self.aktuellePos
        self.moveRelPos(relative_steps, self.aktuellePos)
        self.aktuellePos = target_steps

    def get_status(self):
        return {
            'current_position': self.aktuellePos,
            'max_position': self.maxPos,
            'is_active': GPIO.input(self.EN) == GPIO.LOW
        }
