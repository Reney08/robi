import time
from rpi_ws281x import PixelStrip, ws

# Beispiel LED Konfiguration.
LED_COUNT = 16
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0
LED_STRIP = ws.WS2811_STRIP_GRB

# LED Strip initialisieren.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()

# Beispiel Funktion.
def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Main funktion.
if __name__ == '__main__':
    try:
        colorWipe(strip, (255, 0, 0))  # Rot.
        colorWipe(strip, (0, 255, 0))  # Grün.
        colorWipe(strip, (0, 0, 255))  # Blau.

    except KeyboardInterrupt:
        colorWipe(strip, (0, 0, 0), 10)  # LEDs ausschalten.
