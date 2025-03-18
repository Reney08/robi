from motor.pcadevice import PCADevice
from logger import setup_logger
import time

class Pump(PCADevice):
    def __init__(self, address, channel):
        super().__init__(address, channel)

        # Initialize logging and settings
        self.logger = setup_logger()
        
        # Load movement limits from settings file
        self.pulse_min = 150
        self.pulse_max = 100000000  # Example valid range

        # Compute positions
        self.mid_pos = (self.pulse_max + self.pulse_min) // 2       
        self.range = self.pulse_max - self.pulse_min
        self.inactive_pos = 0
        self.active_pos = self.mid_pos - (self.range // 9)
        self.reverse_pos = (self.mid_pos - (self.range // 9)) * -1 

        self.current_position = 'inactive'

    def get_status(self):
        """Return the current position and PWM settings of the pump."""
        return {
            'current_position': self.current_position,
            'active_position': self.active_pos,
            'inactive_position': self.inactive_pos
        }

    def activate(self):
        """Move servo to the active position."""
        self.pca.set_pwm(self.channel, 0, self.active_pos)
        time.sleep(1)
        self.current_position = 'active'

    def deactivate(self):
        """Move servo to the inactive position."""
        self.pca.set_pwm(self.channel, 0, self.inactive_pos)
        time.sleep(1)
        self.current_position = 'inactive_pos'

    def reversed():
        """Move servo to the inactive position."""
        self.pca.set_pwm(self.channel, 0, self.reverse_pos)
        time.sleep(1)
        self.current_position = 'reverse_pos'

    def shutdown(self):
        """Shutdown the pump by moving it to inactive and turning off the PWM signal."""
        print("Shutting down pump...")
    
        # Move the pump to its inactive position
        self.deactivate()
    
        # Ensure PWM is completely turned off
        time.sleep(0.5)  # Short delay to let it deactivate
        self.pca.set_pwm(self.channel, 0, 0)  # Stop sending PWM signal
    
        print("Pump shut down successfully.")
