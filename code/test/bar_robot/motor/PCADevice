from abc import ABC, abstractmethod
from Adafruit_PCA9685 import PCA9685
from fileHandler import FileHandler
from logger import setup_logger

import time

# Abstract Parent Class for PCA Devices
class PCADevice(ABC):
    def __init__(self, address, channel):
        """
        Base class for PCA9685 devices.
        :param address: I2C address of the PCA board (e.g., 0x40, 0x41)
        :param channel: Channel number on the PCA (0-15)
        """
        self.pca = PCA9685(address=address, busnum=1)  # Initialize PCA9685 at given address
        self.pca.set_pwm_freq(60)  # Set frequency
        self.channel = channel

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass
