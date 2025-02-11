import RPi.GPIO as GPIO
import spidev
import time

class Scale:
    DT_PIN = 5
    CLK_PIN = 6

    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DT_PIN, GPIO.IN)
        GPIO.setup(self.CLK_PIN, GPIO.OUT)
        self.zero_value = self.zero_scale()
        self.kalibrierungsfaktor = self.calibrate()

    def read_hx711(self):
        try:
            GPIO.output(self.CLK_PIN, False)
            time.sleep(0.1)  # Ensure the clock pin is low for a moment
            data = 0
            for _ in range(24):
                GPIO.output(self.CLK_PIN, True)
                time.sleep(0.0001)  # Increase delay
                GPIO.output(self.CLK_PIN, False)
                data = (data << 1) | GPIO.input(self.DT_PIN)
            
            GPIO.output(self.CLK_PIN, True)
            time.sleep(0.001)
            GPIO.output(self.CLK_PIN, False)

            # Convert to 2's complement
            if data & 0x800000:
                data = -(0x1000000 - data)

            return data

        except Exception as e:
            print(f"Fehler beim Lesen des HX711: {e}")
            return 0

    def calibrate(self):
        try:
            print("Lege ein bekanntes Gewicht auf die Waage (z.B. 1000g).")
            input("Drucke Enter, wenn das Gewicht platziert ist.")
            rohwert = self.read_hx711()
            print(f"Rohwert vor Kalibrierung: {rohwert}") #debug
            bekanntes_gewicht = float(input("Gib das tatsachliche Gewicht in Gramm ein: ")) #Eingabe des Gewichts
            kalibrierungsfaktor = bekanntes_gewicht / rohwert
            print(f"Kalibrierungsfaktor: {kalibrierungsfaktor}")
            return kalibrierungsfaktor
        except ValueError:
            print("Ungultige Eingabe. Bitte eine Zahl eingeben.")
            return None
        except Exception as e:
            print(f"Fehler bei Kalibrierung: {e}")
            return None

    def zero_scale(self):
        print("Zeroing the scale...")
        zero_values = []
        for _ in range(10):  # Read 10 times for averaging
            zero_values.append(self.read_hx711())
            time.sleep(0.1)
        zero_value = sum(zero_values) / len(zero_values)
        return zero_value

    def get_weight(self):
        rohwert = self.read_hx711()
        if rohwert != 0:
            gewicht = (rohwert - self.zero_value) * self.kalibrierungsfaktor
            return gewicht
        return 0

    def shutdown(self):
        GPIO.cleanup()
        self.spi.close()
