from motor.pcadevice import PCADevice
from motor.servo import ServoMotor
from motor.pump import Pump
import RPi.GPIO as GPIO
import time
from fileHandler import FileHandler
from logger import setup_logger

class StepperMotor:
    
    def __init__(self):
        # Initialize the StepperMotor with logger, GPIO configuration, and file handlers
        self.logger = setup_logger()
        self.settingsFileHandler = FileHandler('./json/settings.json')
        self.settings = self.settingsFileHandler.readJson()
        
        self.STEP = self.settings.get('STEP')
        self.DIR = self.settings.get('DIR')
        self.EN = self.settings.get('EN')
        self.schalterLinksPin = self.settings.get('schalterLinksPin')
        self.schalterRechtsPin = self.settings.get('schalterRechtsPin')
        self.us_delay = self.settings.get('us_delay')
        self.uS = self.settings.get('uS')

        print(f"STEP: {self.STEP}, DIR: {self.DIR}, EN: {self.EN}, schalterLinksPin: {self.schalterLinksPin}, schalterRechtsPin: {self.schalterRechtsPin}, us_delay: {self.us_delay}, uS: {self.uS}")
        
        self.GPIOConfig()
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()
        self.initFileHandler = FileHandler('./json/stepper_init.json')
        self.initSequence = self.initFileHandler.readJson()
        self.aktuellePos = 0
        self.maxPos = 0
        self.nullPos = 0
        self.standartPos = 20  # Default value
        self.initialized = False  # Ensure this attribute is set before calling init
        self.servo = ServoMotor(address=0x41, channel=0)
        self.pump = Pump(address=0x40, channel=0)
        self.load_positions()
        # self.init()

    def GPIOConfig(self):
        # Configure GPIO settings
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
        # Return the current status of the stepper motor
        return {
            'current_position': self.aktuellePos,
            'max_position': self.maxPos,
            'null_position': self.nullPos,
            'is_active': GPIO.input(self.EN) == GPIO.LOW
        }
        
    def getSchalterRechtsStatus(self):
        # Check the status of the right limit switch
        return GPIO.input(self.schalterRechtsPin) == 1

    def getSchalterLinksStatus(self):
        # Check the status of the left limit switch
        return GPIO.input(self.schalterLinksPin) == 1

    def moveRelPos(self, relative_steps, aktPos):
        # Move the stepper motor by a relative number of steps
        time.sleep(1)
        self.servo.deactivate()
        
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
        # Move the stepper motor to an absolute position
        self.servo.deactivate()
        
        relative_steps = target_steps - self.aktuellePos
        self.moveRelPos(relative_steps, self.aktuellePos)
        self.aktuellePos = target_steps
        if self.aktuellePos == self.standartPos or self.aktuellePos == self.maxPos:
            time.sleep(1)
            self.servo.move_to_waiting()

    def initMoveMotor(self, direction, stop_condition):
        # Move the motor in a specified direction until a stop condition is met
        GPIO.output(self.DIR, direction)
        while not stop_condition():
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.uS * self.us_delay)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.uS * self.us_delay)
            self.aktuellePos += 1 if direction == GPIO.HIGH else -1

    def quick_init(self):
        # Quickly initialize the stepper motor
        if self.initialized:
            return
        self.servo.deactivate()
        time.sleep(1)
        self.initMoveMotor(GPIO.LOW, self.getSchalterLinksStatus)
        time.sleep(1)
        self.move_to_position(self.standartPos)
        self.aktuellePos = 0
        time.sleep(1)
        self.initialized = True

    def init(self):
        # Fully initialize the stepper motor
        if self.initialized:
            return
        self.servo.deactivate()
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
        # Execute a sequence of movements
        for step in sequence:
            position_name = step["position"]
            wait_time = step["wait_time"]
    
            self.servo.deactivate()
            self.pump.deactivate()
            time.sleep(1)

            if position_name == "finished":
                self.servo.move_to_waiting()
                time.sleep(10)
                self.servo.deactivate()
                self.pump.deactivate()
                self.move_to_position(self.standartPos)
                time.sleep(1)
                break
            
            if position_name in self.positions:
                target_steps = self.positions[position_name]
                if target_steps != self.aktuellePos:
                    self.move_to_position(target_steps)
                
                time.sleep(1)
            
                self.servo.activate()
                self.pump.activate()
                time.sleep(wait_time)
    
                self.servo.deactivate()
                self.pump.deactivate()
                time.sleep(1)
            
            else: 
                print(f"Invalid position in sequence: {position_name}")
            
    def load_positions(self):
        # Load positions from the JSON file
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
        # Move to a position and save it
        target_position = self.aktuellePos + steps
        self.move_to_position(target_position)
        self.positions[position_name] = self.aktuellePos
        self.save_positions()
    
    def move_and_save_position(self, steps, position_name):
        # Move to a position and save it
        target_position = self.aktuellePos + steps
        self.move_to_position(target_position)
        self.positions[position_name] = self.aktuellePos
        self.save_positions()

    def save_positions(self):
        # Save positions to the JSON file
        self.positionsFileHandler.writeJson(self.positions)

    def edit_position(self, position_name, new_value):
        # Edit an existing position
        if position_name not in ['finished', 'nullPos', 'maxPos']:
            self.positions[position_name] = new_value
            self.save_positions()
            self.move_to_position(new_value)

    def delete_position(self, position_name):
        # Delete a position
        if position_name not in ['finished', 'nullPos', 'maxPos']:
            del self.positions[position_name]
            self.save_positions()

    def shutdown(self):
        # Ensure the motor is disabled
        print("shutdown stepper")
        GPIO.output(self.EN, GPIO.LOW)
        time.sleep(1)  # Wait for a moment to ensure the motor is disabled
        
        print("shutdown stepperGPIO")
        # Clean up GPIO resources
        GPIO.cleanup()
        self.logger.info("GPIO cleaned up and motor shutdown")
