# ServoMotor Inheriting from PCADevice
class ServoMotor(PCADevice):
    def __init__(self, address, channel):
        """
        Servo motor controlled via PCA9685.
        :param address: I2C address of PCA board
        :param channel: Channel number (0-15)
        """
        super().__init__(address, channel)

        # Initialize logging and settings
        self.logger = setup_logger()
        self.settingsFileHandler = FileHandler('./json/settings.json')
        self.settings = self.settingsFileHandler.readJson()

        # Load movement limits from settings file
        self.pulse_min = self.settings.get('pulse_min', 150)
        self.pulse_max = self.settings.get('pulse_max', 600)

        # Compute positions
        self.mid_pos = (self.pulse_max + self.pulse_min) // 2
        self.range = self.pulse_max - self.pulse_min
        self.inactive_pos = self.mid_pos + (self.range // 9) + 20
        self.active_pos = self.mid_pos - (self.range // 9) + 55
        self.waiting_pos = self.mid_pos + (self.range // 9) - 90

        self.current_position = 'inactive'
        self.positionsFileHandler = FileHandler('./json/positions.json')
        self.positions = self.positionsFileHandler.readJson()

    def activate(self):
        """Move servo to the active position."""
        self.logger.info(f"Moving servo on address {hex(self.pca.address)} channel {self.channel} to active position")
        self.pca.set_pwm(self.channel, 0, self.active_pos)
        time.sleep(1)
        self.current_position = 'active'

    def deactivate(self):
        """Move servo to the inactive position."""
        self.logger.info(f"Moving servo on address {hex(self.pca.address)} channel {self.channel} to inactive position")
        self.pca.set_pwm(self.channel, 0, self.inactive_pos)
        time.sleep(1)
        self.current_position = 'inactive'

    def move_to_waiting(self):
        """Move the servo to a waiting position."""
        self.logger.info(f"Moving servo on address {hex(self.pca.address)} channel {self.channel} to waiting position")
        self.pca.set_pwm(self.channel, 0, self.waiting_pos)
        time.sleep(1)
        self.current_position = 'waiting'

    def get_status(self):
        """Return the current position of the servo."""
        return {'current_position': self.current_position}

    def shutdown(self):
        """Shutdown the servo by moving it to inactive and turning off the PWM signal."""
        self.logger.info(f"Shutting down servo on address {hex(self.pca.address)} channel {self.channel}")
        self.deactivate()  # Ensure the servo is in the inactive position
        self.pca.set_pwm(self.channel, 0, 0)  # Turn off the PWM signal
        self.logger.info(f"Servo on address {hex(self.pca.address)} channel {self.channel} shutdown complete")
