import json

class FileHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def readJson(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.filepath} not found. Creating default file.")
            return {}

    def writeJson(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
