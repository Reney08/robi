import json

class FileHandler:
    def __init__(self, filepath):
        # Initialize the FileHandler with the given file path
        self.filepath = filepath

    def readJson(self):
        try:
            # Attempt to open the file and load its contents as JSON
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If the file is not found, print a warning and return an empty dictionary
            print(f"Warning: {self.filepath} not found. Creating default file.")
            return {}

    def writeJson(self, data):
        # Write the given data to the file in JSON format with indentation for readability
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def readSettings(self):
        settings = {}
        try:
            # Attempt to open the settings file and read its contents
            with open(self.filepath, 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    settings[key] = self._convert_value(value)
        except FileNotFoundError:
            # If the file is not found, print a warning and return an empty dictionary
            print(f"Warning: {self.filepath} not found. Creating default settings.")
        return settings

    def _convert_value(self, value):
        # Convert the value to the appropriate type (int, float, or str)
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def create_default_settings(self):
        default_settings = """
            STEP=17
            DIR=27
            EN=23
            schalterLinksPin=16
            schalterRechtsPin=24
            us_delay=950
            uS=0.000001
            pulse_min=150
            pulse_max=600
            GAIN=0
            OFFSET=0
            SCALE=1
            time_constant=0.25
            filtered=0
            clock_pin=6
            data_pin=5
            calibration_factor=-0.0009405187713438978
            """
        with open(self.filepath, 'w') as f:
            f.write(default_settings)
