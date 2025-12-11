import json
import os
from .constants import CONFIG_FILE

class ConfigManager:
    """Manages application settings persistence."""
    
    def __init__(self):
        self.settings = {
            "floating_mode": False,
            "sound_enabled": True,
            "last_x": 100,
            "last_y": 100,
            "always_on_top": True
        }
        self.load()

    def load(self):
        """Load settings from JSON file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save(self):
        """Save current settings to JSON file."""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
