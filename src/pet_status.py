import json
import os
import time
import random
from PyQt6.QtCore import QTimer, QObject
from . import resource_utils

class PetStatus(QObject):
    def __init__(self, data_file=None):
        super().__init__()
        
        # Use persistent data path
        if data_file is None:
            data_dir = resource_utils.get_data_path()
            self.data_file = os.path.join(data_dir, "pet_data.json")
        else:
            self.data_file = data_file
            
        print(f"DEBUG: Data file path: {self.data_file}")
        
        # Default Values
        self.birth_time = time.time()
        self.hunger = 100 # Max 100, 0 is starving
        self.mood = "Unknown" 
        self.last_fed_time = 0 # Timestamp of last feed
        self.digest_finish_time = 0 # Timestamp when uncomfortable starts (0 = none)
        self.is_uncomfortable = False
        self.is_bored = False
        self.start_bored_timer()
        
        self.load_data()
        
        # Hunger Decay Timer (1 minute interval)
        self.hunger_timer = QTimer(self)
        self.hunger_timer.timeout.connect(self.decay_hunger)
        self.hunger_timer.start(60 * 1000) # 60 seconds

    def start_bored_timer(self):
        # Check for boredom every 30 minutes
        self.bored_check_timer = QTimer(self)
        self.bored_check_timer.timeout.connect(self.update_bored_status)
        self.bored_check_timer.start(30 * 60 * 1000) # 30 minutes

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.birth_time = data.get("birth_time", time.time())
                    self.hunger = data.get("hunger", 100)
                    self.last_fed_time = data.get("last_fed_time", 0)
                    self.digest_finish_time = data.get("digest_finish_time", 0)
                    self.is_uncomfortable = data.get("is_uncomfortable", False)
                    self.is_bored = data.get("is_bored", False)
                    print(f"DEBUG: Loaded data - Hunger: {self.hunger}, Uncomfortable: {self.is_uncomfortable}, Bored: {self.is_bored}")
            except Exception as e:
                print(f"Error loading data: {e}")
                # Keep defaults
        else:
            # First time run
            print("DEBUG: No data file found, creating new one.")
            self.birth_time = time.time()
            self.save_data()

    def save_data(self):
        data = {
            "birth_time": self.birth_time,
            "hunger": self.hunger,
            "last_fed_time": self.last_fed_time,
            "digest_finish_time": self.digest_finish_time,
            "is_uncomfortable": self.is_uncomfortable,
            "is_bored": self.is_bored
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            # Print only occasionally or for debug
            # print(f"DEBUG: Saved data")
        except Exception as e:
            print(f"Error saving data: {e}")

    def decay_hunger(self):
        if self.hunger > 0:
            self.hunger -= 1
        # Auto-save every decay
        self.save_data()

    def get_hunger(self):
        return self.hunger

    def get_birth_time_str(self):
        uptime = time.time() - self.birth_time
        
        days = int(uptime // (24 * 3600))
        uptime %= (24 * 3600)
        hours = int(uptime // 3600)
        uptime %= 3600
        minutes = int(uptime // 60)
        
        if days > 0:
            return f"{days}일 {hours}시간 {minutes}분"
        elif hours > 0:
            return f"{hours}시간 {minutes}분"
        else:
            return f"{minutes}분"

    def update_mood_status(self):
        """Checks digestion and updates uncomfortable status lazy-style."""
        # If we have a pending digestion
        if self.digest_finish_time > 0 and not self.is_uncomfortable:
            if time.time() >= self.digest_finish_time:
                self.is_uncomfortable = True
                self.digest_finish_time = 0
                self.save_data()
                print("DEBUG: Digestion finished -> Pet is now Uncomfortable")

    def update_bored_status(self):
        """Checks for boredom (50% chance every 30 mins)."""
        if not self.is_bored:
             if random.random() < 0.5:
                 self.is_bored = True
                 self.save_data()
                 print("DEBUG: Pet is now Bored")

    def get_mood(self):
        # Update logic whenever mood is queried
        self.update_mood_status()
        
        if self.is_uncomfortable:
            return "불편"
        elif self.is_bored:
            return "심심함"
        elif self.hunger <= 30: # Only if really starving
            return "나쁨"
        else:
            return "행복"

    def feed(self, amount=10):
        self.hunger = min(100, self.hunger + amount)
        
        # Set digestion timer (3 to 10 minutes)
        # 3*60 = 180, 10*60 = 600
        delay = random.randint(180, 600)
        self.digest_finish_time = time.time() + delay
        # self.is_uncomfortable = False # Removed: Feed does not cure discomfort
        self.save_data()
        print(f"DEBUG: Fed pet. Digestion in {delay} seconds.")
        
    def can_feed(self):
        # 5 minutes cooldown
        return (time.time() - self.last_fed_time) >= (5 * 60)
        
    def record_feed(self):
        self.last_fed_time = time.time()
        self.save_data()
        
    def poop(self):
        """Relieves discomfort."""
        self.is_uncomfortable = False
        self.digest_finish_time = 0
        self.save_data()
        print("DEBUG: Poop success -> Pet is Happy")

    def play_success(self):
        """Relieves boredom."""
        self.is_bored = False
        self.save_data()
        print("DEBUG: Play success -> Pet is no longer Bored")

    def debug_set_full_hunger(self):
        self.hunger = 100
        self.save_data()
        print("DEBUG: Force full hunger")
        
    def debug_set_hunger_30(self):
        self.hunger = 30
        self.save_data()
        print("DEBUG: Force hunger 30")

    def debug_reset_feed_cooldown(self):
        self.last_fed_time = 0
        self.save_data()
        print("DEBUG: Reset Feed Cooldown")

    # --- Debug Helpers ---
    def debug_set_uncomfortable(self):
        self.is_uncomfortable = True
        self.digest_finish_time = 0 # Clear timer if any
        self.save_data()
        print("DEBUG: Handled Force Uncomfortable")

    def debug_set_bored(self):
        self.is_bored = True
        self.save_data()
        print("DEBUG: Handled Force Bored")

    def debug_set_happy(self):
        """Force happy state: Not bored, not uncomfortable. Hunger to 50 if low."""
        self.is_bored = False
        self.is_uncomfortable = False
        if self.hunger <= 30:
            self.hunger = 50
        self.save_data()
        print("DEBUG: Handled Force Happy")
