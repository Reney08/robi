import json

class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> dict:
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_config(self) -> None:
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str):
        return self.config.get(key)

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()
