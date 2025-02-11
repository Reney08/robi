import RPi.GPIO as GPIO
import threading
import time

from hx711 import HX711

class Scale:
    def __init__(self, clock_pin, data_pin, calibration_factor):
        self.hx711 = HX711(clock_pin, data_pin)
        self.calibration_factor = calibration_factor
        self.active = False
        self.weight = 0
        self.thread = None

    def activate(self):
        self.hx711.tare()
        self.active = True
        if self.thread is None:
            self.thread = threading.Thread(target=self._update_weight)
            self.thread.start()

    def deactivate(self):
        self.active = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def _update_weight(self):
        while self.active:
            weight = self.hx711.read_average(3) * self.calibration_factor
            if weight < 0:
                weight = 0
            self.weight = int(weight)
            time.sleep(1)

    def get_weight(self):
        if not self.active:
            return None
        return self.weight

    def calibrate(self):
        print("Place a known weight on the scale (e.g., 1000g).")
        input("Press Enter when the weight is placed.")
        raw_value = self.hx711.read_average()
        print(f"Raw value before calibration: {raw_value}")  # Debug
        known_weight = float(input("Enter the actual weight in grams: "))  # Input the weight
        self.calibration_factor = known_weight / raw_value
        print(f"Calibration factor: {self.calibration_factor}")

    def shutdown(self):
        self.deactivate()
        GPIO.cleanup()
