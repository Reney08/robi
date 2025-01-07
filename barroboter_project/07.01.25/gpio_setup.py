import RPi.GPIO as GPIO
class GPIOSetup:
    def __init__(self, step_pin: int, direction_pin: int, enable_pin: int):
        self.step_pin: int = step_pin
        self.direction_pin: int = direction_pin
        self.enable_pin: int = enable_pin
        self.setup_gpio()

    def setup_gpio(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.output(self.enable_pin, GPIO.LOW)

    def cleanup_gpio(self) -> None:
        GPIO.cleanup()
