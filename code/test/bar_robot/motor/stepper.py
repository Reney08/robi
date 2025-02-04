import RPi.GPIO as GPIO
import time
import json
from fileHandler import FileHandler
from logger import setup_logger

class StepperMotor:
    STEP = 17
    DIR = 27
    EN = 23
    schalterLinksPin = 16
    schalterRechtsPin = 24
    us_delay = 950
    uS = 0.000001

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

    def moveRelPos(self, relative_steps, aktPos):
        direction = GPIO.HIGH if relative_steps > 0 else GPIO.LOW
        absolute_steps = abs(relative_steps)
        GPIO.output(self.DIR, direction)

        for _ in range(absolute_steps):
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.uS * self.us_delay)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.uS * self.us_delay)
            aktPos += 1 if direction == GPIO.HIGH else -1
            if (aktPos < -1) or (aktPos > self.maxPos):
                print("Limit switch triggered! Stopping motor.")
                break
        self.aktuellePos = aktPos

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

    def initMoveMotor(self, direction, stop_condition):
        GPIO.output(self.DIR, direction)
        while not stop_condition():
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.uS * self.us_delay)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.uS * self.us_delay)
            self.aktuellePos += 1 if direction == GPIO.HIGH else -1

    def init(self):
        if self.initialized:
            return
        for step in self.initSequence:
            if step == "left":
                self.initMoveMotor(GPIO.LOW, self.getSchalterLinksStatus)
                self.nullPos = self.aktuellePos = 0
                time.sleep(1)
            elif step == "right":
                self.initMoveMotor(GPIO.HIGH, self.getSchalterRechtsStatus)
                self.maxPos = self.aktuellePos
                time.sleep(1)
            elif step == "left_again":
                self.move_to_position(20)
                self.aktuellePos = 0
                time.sleep(1)

        self.maxPos = abs(self.nullPos) + abs(self.maxPos)
        self.temp_disable_limit_switch_check = True
        self.moveRelPos(10, self.aktuellePos)
        self.temp_disable_limit_switch_check = False
        self.initialized = True

    def getSchalterRechtsStatus(self):
        return GPIO.input(self.schalterRechtsPin) == 1

    def getSchalterLinksStatus(self):
        return GPIO.input(self.schalterLinksPin) == 1
        
    def execute_sequence(self, sequence):
        for step in sequence:
            position_name = step["position"]
            wait_time = step["wait_time"]
            # print(position_name)
            # print(wait_time)
            # print(self.aktuellePos)
    
            if position_name in self.positions:
                print(self.positions)
                target_steps = self.positions[position_name]  # Lookup the position in positions.json
                # Move the motor only if needed
                if target_steps != self.aktuellePos:
                    self.move_to_position(target_steps)

            else: 
                print(f"Invalid position in sequence: {position_name}")
            
            if position_name == "finished":
                print("Sequence completed. Returning to home position...")
                time.sleep(10)
                self.move_to_position(self.nullPos)
                self.pwm.set_pwm(0, 0, self.inactive_pos)
                time.sleep(1)
                print("Returned to Null position.")
                print("Available Cocktails:")
                for cocktail in self.available_cocktails:
                    print(f"- {cocktail}")
                break
            time.sleep(1)
            
            # Move the servo regardless of motor movement
            print("Moving servo to active position...")
            self.pwm.set_pwm(0, 0, self.active_pos)
            time.sleep(5)  # Wait for 5 seconds
    
            # Move servo back
            print("Returning servo to inactive position...")
            self.pwm.set_pwm(0, 0, self.inactive_pos)
            time.sleep(1)  # Wait for servo movement
            
    def load_sequence(self, cocktail_name):
        sequence_file = f"./json/sequences/{cocktail_name}_sequence.json"
        try:
            with open(sequence_file, 'r') as f:
                sequence = json.load(f)
            return sequence
        except FileNotFoundError:
            print(f"Sequence file for {cocktail_name} not found.")
            return None
