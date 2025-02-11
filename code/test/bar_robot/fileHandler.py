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
