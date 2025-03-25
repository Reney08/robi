import time
import neopixel

# Parameter für den LED-Streifen
TEST_PIN = 18  # GPIO-Pin, an den die LEDs angeschlossen sind
MAX_LEDS_GUESS = 300  # Schätze die maximale Anzahl der LEDs auf deinem Streifen
BRIGHTNESS = 0.5  # Helligkeit (Skala 0.0 bis 1.0)

# LED-Streifen initialisieren
pixels = neopixel.NeoPixel(
    TEST_PIN, MAX_LEDS_GUESS, brightness=BRIGHTNESS, auto_write=False
)


def find_led_count():
    """
    Testet schrittweise jede LED auf dem Streifen,
    um die Anzahl der LEDs herauszufinden.
    """
    print("Ermittle die Anzahl der LEDs. Zähle die LEDs, die nacheinander leuchten.")
    for i in range(MAX_LEDS_GUESS):
        pixels.fill((0, 0, 0))  # Schalte alle LEDs aus
        pixels[i] = (255, 0, 0)  # Aktiviere LED i (leuchtet rot)
        pixels.show()
        print(f"LED {i + 1} leuchtet – Zähle sie.")  # Zeigt die LED-Nummer an
        time.sleep(0.5)  # Kurze Pause, damit du die aktive LED erkennen kannst

        # Beende das Programm mit "Strg+C", wenn die letzte LED erreicht ist
    print("Maximale Anzahl der LEDs erreicht oder Testende. Anpassen, wenn nötig.")


try:
    find_led_count()
except KeyboardInterrupt:
    # Bei manueller Beendigung durch Strg+C: Schalte die LEDs aus
    print("\nTest unterbrochen. LEDs ausschalten...")
    pixels.fill((0, 0, 0))
    pixels.show()
