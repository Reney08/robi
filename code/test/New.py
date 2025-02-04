import RPi.GPIO as GPIO
from Adafruit_PCA9685 import PCA9685
import time
import json
import os

from logger import setup_logger
from fileHandler import FileHandler

class StetterInit:
    # Initialize the PCA9685
    pwm = PCA9685(busnum=1)  # Use bus 1 (check your I2C bus if unsure)
    pwm.set_pwm_freq(60)  # Set frequency to 60 Hz

    # Define pulse width ranges (adjust as needed for your servos)
    pulse_min = 150  # Min pulse length out of 4096
    pulse_max = 600  # Max pulse length out of 4096

    nullPos = 0
    maxPos = 0
    aktuellePos = 0

    # Pin configuration
    STEP = 17
    DIR = 27
    EN = 23
    schalterLinksPin = 16
    schalterRechtsPin = 24

    # Timing and delay
    us_delay = 950
    uS = 0.000001  # 0.00001 normal

    mid_pos = (pulse_max + pulse_min) // 2
    range = pulse_max - pulse_min
    inactive_pos = mid_pos + (range // 9) + 50
    active_pos = mid_pos - (range // 9) + 65

    temp_disable_limit_switch_check = False

    def __init__(self):
        self.logger = setup_logger()
        self.logger.debug("Logger initialized")
        self.GPIOConfig()
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()
        self.initFileHandler = FileHandler('./json/stepper_init.json')
        self.initSequence = self.initFileHandler.readJson()
        self.available_cocktails_file = "./json/available_cocktails.json"
        self.load_available_cocktails()

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

    def getSchalterRechtsStatus(self) -> bool:
        if self.temp_disable_limit_switch_check:
            return False
        return GPIO.input(self.schalterRechtsPin) == 1

    def getSchalterLinksStatus(self) -> bool:
        if self.temp_disable_limit_switch_check:
            return False
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

    def initMoveMotor(self, direction, stop_condition):
        GPIO.output(self.DIR, direction)
        while not stop_condition():
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.uS * self.us_delay)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.uS * self.us_delay)
            self.aktuellePos += 1 if direction == GPIO.HIGH else -1

    def init(self):
        self.pwm.set_pwm(0, 0, self.inactive_pos)
        print("Moved servo down")

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

        print(f"aktuellePos: {self.aktuellePos}, maxPos: {self.maxPos}")

    def execute_sequence(self, sequence):
        for step in sequence:
            position_name = step["position"]
            wait_time = step["wait_time"]
            print(position_name)
            print(wait_time)
            print(self.aktuellePos)
    
            if position_name in self.positions:
                print(self.positions)
                target_steps = self.positions[position_name]  # Lookup the position in positions.json
                # Move the motor only if needed
                if target_steps != self.aktuellePos:
                    self.move_to_position(target_steps)
                
                time.sleep(1)
            
                # Move the servo regardless of motor movement
                print("Moving servo to active position...")
                self.pwm.set_pwm(0, 0, self.active_pos)
                time.sleep(5)  # Wait for 5 seconds
    
                # Move servo back
                print("Returning servo to inactive position...")
                self.pwm.set_pwm(0, 0, self.inactive_pos)
                time.sleep(1)  # Wait for servo movement
            
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
    
    def select_cocktail(self):
        print("Available Cocktails:")
        for i, cocktail in enumerate(self.available_cocktails):
            print(f"{i + 1}. {cocktail}")

        choice = int(input("Select a cocktail by number: ")) - 1
        if 0 <= choice < len(self.available_cocktails):
            selected_cocktail = self.available_cocktails[choice]
            print(f"You selected: {selected_cocktail}")
            return selected_cocktail
        else:
            print("Invalid selection.")
            return None

    def load_sequence(self, cocktail_name):
        sequence_file = f"./json/sequences/{cocktail_name}_sequence.json"
        try:
            with open(sequence_file, 'r') as f:
                sequence = json.load(f)
            return sequence
        except FileNotFoundError:
            print(f"Sequence file for {cocktail_name} not found.")
            return None
            
            
if __name__ == "__main__":
    try:
        stepper = StetterInit()
        stepper.init()
        while True:
            selected_cocktail = stepper.select_cocktail()
            if selected_cocktail:
                sequence = stepper.load_sequence(selected_cocktail)
                if sequence:
                    stepper.execute_sequence(sequence)
            continue_choice = input("Do you want to select another cocktail? (yes/no): ").strip().lower()
            if continue_choice != 'yes':
                print("Exiting program.")
                break
    except Exception as e:
        print(e)
