import time
import neopixel
import board

class TestAddressableRGBLEDs:
    def __init__(self, pin, num_leds=30, brightness=0.5):
        """
        Initialisiert den RGB-LED-Streifen für Tests.

        :param pin: GPIO-Pin zum Steuern des LED-Streifens.
        :param num_leds: Anzahl der LEDs auf dem Streifen.
        :param brightness: Helligkeit der LEDs (zwischen 0.0 und 1.0).
        """
        self.num_leds = num_leds
        self.brightness = brightness

        # NeoPixel-Objekt initialisieren
        self.pixels = neopixel.NeoPixel(
            pin,
            num_leds,
            auto_write=False,
            brightness=brightness,
            pixel_order=neopixel.GRB
        )

    def _color_wheel(self, pos):
        """
        Erstellt eine Farbe basierend auf einem Regenbogenrad.
        :param pos: Position im Farbkreis (0–255).
        :return: (R, G, B) Farbe als Tupel.
        """
        if pos < 85:
            return int(pos * 3), int(255 - (pos * 3)), 0
        elif pos < 170:
            pos -= 85
            return int(255 - (pos * 3)), 0, int(pos * 3)
        else:
            pos -= 170
            return 0, int(pos * 3), int(255 - (pos * 3))

    def display_rainbow(self, speed=0.05):
        """
        Zeigt einen Regenbogeneffekt auf dem LED-Streifen an.

        :param speed: Geschwindigkeit der Animation (in Sekunden pro Frame).
        """
        print("Starting rainbow animation. Press Ctrl+C to stop.")
        try:
            while True:
                for j in range(255):  # Regenbogenfarben durchlaufen
                    for i in range(self.num_leds):
                        pixel_index = (i * 256 // self.num_leds) + j
                        self.pixels[i] = self._color_wheel(pixel_index & 255)
                    self.pixels.show()
                    time.sleep(speed)
        except KeyboardInterrupt:
            print("\nAnimation stopped.")
            self.clear()

    def clear(self):
        """
        Schaltet alle LEDs aus.
        """
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        print("LEDs cleared.")

    def test_single_led(self, led_index, test_color=(255, 0, 0), wait=0.5):
        """
        Testet eine einzelne LED am gegebenen Index.

        :param led_index: Index der LED (0–n).
        :param test_color: Farbe der LED, z.B. (255, 0, 0) für Rot.
        :param wait: Wartezeit in Sekunden.
        """
        if led_index >= self.num_leds:
            print(f"Error: LED index {led_index} is out of range (max index: {self.num_leds - 1}).")
            return

        print(f"Testing LED {led_index} with color {test_color}.")
        self.clear()
        self.pixels[led_index] = test_color
        self.pixels.show()
        time.sleep(wait)
        self.clear()

    def run_color_loop(self):
        """
        Lässt den Benutzer eine Farbe auswählen und wendet sie dynamisch auf die LEDs an.
        Die Schleife läuft, bis der Benutzer `Ctrl + C` drückt.
        """
        print("Drücke Strg+C, um das Programm zu beenden.")
        print("Gib die neue Farbe als RGB-Werte (z. B. '255 0 0' für Rot) ein.")

        try:
            while True:
                user_input = input("Neue Farbe (RGB-Werte): ")
                try:
                    r, g, b = map(int, user_input.split())
                    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                        self.set_color(r, g, b)
                        print(f"Neue Farbe auf R:{r}, G:{g}, B:{b} gesetzt.")
                    else:
                        print("RGB-Werte müssen zwischen 0 und 255 liegen.")
                except ValueError:
                    print("Ungültige Eingabe. Bitte gib drei Zahlen ein, getrennt durch Leerzeichen.")
        except KeyboardInterrupt:
            print("\nProgramm beendet. LEDs werden ausgeschaltet.")
            self.clear()

    def set_color(self, r, g, b):
        """
        Setzt alle LEDs auf eine bestimmte Farbe.

        :param r: Rot-Wert (0-255)
        :param g: Grün-Wert (0-255)
        :param b: Blau-Wert (0-255)
        """
        # Konvertiere Werte auf die Helligkeitsskala, falls nötig
        scaled_color = (int(r * self.brightness), int(g * self.brightness), int(b * self.brightness))

        # Wende die Farbe auf alle LEDs an
        for i in range(self.num_leds):
            self.pixels[i] = scaled_color  # Setze alle LEDs auf dieselbe Farbe


# Hauptfunktion für einfache Tests
if __name__ == "__main__":
    # Konfiguriere den GPIO-Pin und die Anzahl der LEDs
    TEST_PIN = board.D18  # GPIO 18
    TEST_NUM_LEDS = 600  # Anzahl der LEDs auf deinem Streifen
    TEST_BRIGHTNESS = 0.5  # Helligkeit (zwischen 0.0 und 1.0)

    # LED-Testobjekt initialisieren
    leds = TestAddressableRGBLEDs(TEST_PIN, TEST_NUM_LEDS, TEST_BRIGHTNESS)

    print("Testprogramm gestartet.")
    print("Optionen:")
    print("1. Display Rainbow (Ctrl+C to stop)")
    print("2. Test a Single LED")
    print("3. Clear all LEDs")
    print("4. Test all LEDs")
    print("0. Exit")

    while True:
        try:
            choice = int(input("Bitte wähle eine Option: "))
            if choice == 1:
                leds.display_rainbow()
            elif choice == 2:
                index = int(input(f"Welche LED möchtest du testen? (0–{TEST_NUM_LEDS - 1}): "))
                color = input("Gib eine Farbe als (R,G,B) ein (z.B. 255,0,0 für Rot): ")
                try:
                    r, g, b = map(int, color.split(","))
                    leds.test_single_led(index, (r, g, b))
                except ValueError:
                    print("Ungültiges Farbschema. Bitte erneut versuchen!")
            elif choice == 3:
                leds.clear()
            elif choice == 4:
                for i in range(TEST_NUM_LEDS):
                    leds.test_single_led(i)
                    time.sleep(0.5)
            elif choice == 5:
                leds.run_color_loop()
            elif choice == 0:
                print("Beenden des Testprogramms.")
                leds.clear()
                break
            else:
                print("Ungültige Eingabe. Bitte erneut versuchen!")
        except ValueError:
            print("Bitte gib eine gültige Nummer ein.")
