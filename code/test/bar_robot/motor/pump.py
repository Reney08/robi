from motor.pcadevice import PCADevice
import time

class Pump(PCADevice):
    def __init__(self, address, channel):
        super().__init__(address, channel)

          # Load movement limits from settings file
        self.pulse_min = 150
        self.pulse_max = 6000

        # Compute positions
        self.mid_pos = (self.pulse_max + self.pulse_min) // 2
        self.range = self.pulse_max - self.pulse_min
        self.inactive_pos = 0
        self.active_pos = self.mid_pos - (self.range // 9) 
        #self.inactive_pos = 150
        #self.active_pos = 600

        self.current_position = 'inactive'

    def activate(self):
        """Move servo to the active position."""
        self.pca.set_pwm(self.channel, 0, self.active_pos)
        time.sleep(1)
        self.current_position = 'active'

    def deactivate(self):
        """Move servo to the inactive position."""
        self.pca.set_pwm(self.channel, 0, self.inactive_pos)
        time.sleep(1)
        self.current_position = 'inactive'

    def get_status(self):
        """Return the current position of the servo."""
        return {'current_position': self.current_position}

    def shutdown(self):
        """Shutdown the servo by moving it to inactive and turning off the PWM signal."""
        self.deactivate()  # Ensure the servo is in the inactive position
        self.pca.set_pwm(self.channel, 0, 0)  # Turn off the PWM signal
