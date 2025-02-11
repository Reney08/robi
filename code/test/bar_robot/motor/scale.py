import RPi.GPIO as GPIO
import threading
import time

from .scale_hx711 import HX711
from fileHandler import FileHandler

class Scale:
    def __init__(self):
        # Initialize the Scale with settings from the settings file
        self.settingsFileHandler = FileHandler('./json/settings.json')
        self.settings = self.settingsFileHandler.readJson()
        
        self.clock_pin = self.settings.get('clock_pin')
        self.data_pin = self.settings.get('data_pin')
        self.calibration_factor = self.settings.get('calibration_factor')
        
        self.hx711 = HX711(self.clock_pin, self.data_pin)
        self.hx711.set_scale(self.calibration_factor)
        self.active = False
        self.weight = 0
        self.thread = None
        self.thread_stop_event = threading.Event()

    def activate(self):
        # Tare the scale and start the weight update thread
        self.hx711.tare()
        self.active = True
        self.thread_stop_event.clear()
        if self.thread is None:
            self.thread = threading.Thread(target=self._update_weight)
            self.thread.start()

    def deactivate(self):
        # Stop the weight update thread and deactivate the scale
        self.active = False
        self.thread_stop_event.set()
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def _update_weight(self):
        # Continuously update the weight while the scale is active
        while not self.thread_stop_event.is_set():
            weight = self.hx711.read_average(3) * self.calibration_factor
            if weight < 0:
                weight = 0
            self.weight = int(weight)
            time.sleep(1)

    def get_weight(self):
        # Return the current weight if the scale is active
        if not self.active:
            return None
        return self.weight

    def calibrate(self):
        # Calibrate the scale using a known weight
        print("Place a known weight on the scale (e.g., 1000g).")
        input("Press Enter when the weight is placed.")
        raw_value = self.hx711.read_average()
        print(f"Raw value before calibration: {raw_value}")  # Debug
        known_weight = float(input("Enter the actual weight in grams: "))  # Input the weight
        self.calibration_factor = known_weight / raw_value
        print(f"Calibration factor: {self.calibration_factor}")

    def shutdown(self):
        # Deactivate the scale and clean up GPIO resources
        self.deactivate()
        GPIO.cleanup()
