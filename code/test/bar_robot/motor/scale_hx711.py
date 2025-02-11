import RPi.GPIO as GPIO

class HX711:
    def __init__(self, clock_pin, data_pin, gain=128):
        self.clock_pin = clock_pin
        self.data_pin = data_pin
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.data_pin, GPIO.IN)
        GPIO.output(self.clock_pin, False)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.25
        self.filtered = 0

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2

        self.read()
        self.filtered = self.read()

    def read(self):
        while GPIO.input(self.data_pin) == 1:
            pass

        data = 0
        for _ in range(24 + self.GAIN):
            GPIO.output(self.clock_pin, True)
            data = (data << 1) | GPIO.input(self.data_pin)
            GPIO.output(self.clock_pin, False)

        data >>= self.GAIN

        if data & 0x800000:
            data -= 0x1000000

        return data

    def read_average(self, times=3):
        sum = 0
        for _ in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.read_lowpass() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant=None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        GPIO.output(self.clock_pin, False)
        GPIO.output(self.clock_pin, True)

    def power_up(self):
        GPIO.output(self.clock_pin, False)
