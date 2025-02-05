import RPi.GPIO as GPIO
import time
import json
from fileHandler import FileHandler
from logger import setup_logger
from motor.servo import ServoMotor

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
        self.available_cocktails_file = "./json/available_cocktails.json"
        self.aktuellePos = 0
        self.maxPos = 0
        self.nullPos = 0
        self.standartPos = 20  # Default value
        self.initialized = False  # Ensure this attribute is set before calling init
        self.servo = ServoMotor()
        self.load_available_cocktails()
        self.load_positions()
        # self.init()

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
        
    def get_status(self):
        return {
            'current_position': self.aktuellePos,
            'max_position': self.maxPos,
            'null_position': self.nullPos,
            'is_active': GPIO.input(self.EN) == GPIO.LOW
        }
        
    def getSchalterRechtsStatus(self):
        return GPIO.input(self.schalterRechtsPin) == 1

    def getSchalterLinksStatus(self):
        return GPIO.input(self.schalterLinksPin) == 1

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
        if self.aktuellePos == self.standartPos or self.aktuellePos == self.maxPos:
            self.servo.move_to_active()
            time.sleep(1)

    def initMoveMotor(self, direction, stop_condition):
        GPIO.output(self.DIR, direction)
        while not stop_condition():
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.uS * self.us_delay)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.uS * self.us_delay)
            self.aktuellePos += 1 if direction == GPIO.HIGH else -1

    def quick_init(self):
        # Move the servo to the inactive position to avoid collisions
        self.servo.move_to_inactive()
        time.sleep(1)
        # Move to the left until the left limit switch is triggered
        self.initMoveMotor(GPIO.LOW, self.getSchalterLinksStatus)
        time.sleep(1)
        # Move to standartPos
        self.move_to_position(self.standartPos)
        self.aktuellePos = 0
        time.sleep(1)

    def init(self):
        if self.initialized:
            return
        # Move the servo to the inactive position to avoid collisions
        self.servo.move_to_inactive()
        time.sleep(1)

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
                self.move_to_position(self.standartPos)
                self.aktuellePos = 0
                time.sleep(1)

        self.maxPos = abs(self.nullPos) + abs(self.maxPos)
        self.moveRelPos(10, self.aktuellePos)
        self.initialized = True

    def execute_sequence(self, sequence):
        for step in sequence:
            position_name = step["position"]
            wait_time = step["wait_time"]

            self.servo.move_to_inactive()
            time.sleep(1)
            
            if position_name in self.positions:
                target_steps = self.positions[position_name]  # Lookup the position in positions.json
                if target_steps != self.aktuellePos:
                    self.move_to_position(target_steps)
                
                time.sleep(1)
            
                self.servo.move_to_active()
                time.sleep(wait_time)  # Wait for the specified time
    
                self.servo.move_to_inactive()
                time.sleep(1)  # Wait for servo movement
            
            else: 
                print(f"Invalid position in sequence: {position_name}")
                
            if position_name == "finished":
                time.sleep(10)
                self.servo.move_to_inactive()
                self.move_to_position(self.standartPos)
                time.sleep(1)
                for cocktail in self.available_cocktails:
                    print(f"- {cocktail}")
                break
        
    def load_positions(self):
        try:
            self.nullPos = self.positions['nullPos']
            self.maxPos = self.positions['maxPos']
            self.standartPos = self.positions['standartPos']
        except KeyError as e:
            print(f"KeyError: {e} not found in positions.json. Using default values.")
            self.nullPos = 0
            self.maxPos = 0  # Set a default value or handle appropriately
            self.standartPos = 20
            
    def move_and_save_position(self, steps, position_name):
        target_position = self.aktuellePos + steps
        self.move_to_position(target_position)
        self.positions[position_name] = self.aktuellePos
        self.save_positions()
    
    def save_positions(self):
        with open('./json/positions.json', 'w') as f:
            json.dump(self.positions, f, indent=4)

    def edit_position(self, position_name, new_value):
        if position_name not in ['finished', 'nullPos', 'maxPos']:
            self.positions[position_name] = new_value
            self.save_positions()
            self.move_to_position(new_value)

    def delete_position(self, position_name):
        if position_name not in ['finished', 'nullPos', 'maxPos']:
            del self.positions[position_name]
            self.save_positions()


    def load_sequence(self, cocktail_name):
        sequence_file = f"./json/sequences/{cocktail_name}_sequence.json"
        try:
            with open(sequence_file, 'r') as f:
                sequence = json.load(f)
            return sequence
        except FileNotFoundError:
            print(f"Sequence file for {cocktail_name} not found.")
            return None

    def load_available_cocktails(self):
        try:
            with open(self.available_cocktails_file, 'r') as f:
                self.available_cocktails = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.available_cocktails_file} not found. Creating default file.")
            self.available_cocktails = []
            self.save_available_cocktails()

    def save_available_cocktails(self):
        with open(self.available_cocktails_file, 'w') as f:
            json.dump(self.available_cocktails, f, indent=4)

    def shutdown(self):
        self.logger.info("Shutting down stepper motor")
        GPIO.output(self.EN, GPIO.HIGH)  # Disable the stepper motor
        self.servo.move_to_inactive()  # Ensure the servo is in the inactive position
        self.logger.info("Stepper motor shutdown complete")
