import os

# App Info
APP_NAME = "Desktop Kitty"
APP_VERSION = "1.0.0"

# Filesystem
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
CONFIG_FILE = os.path.join(BASE_DIR, "settings.json")

# Physics & World
GRAVITY = 0.5
TERMINAL_VELOCITY = 15.0
GROUND_OFFSET = 50  # Distance from bottom of screen to stop
MOVE_SPEED = 2      # Horizontal pixels per tick

# Timers
ANIMATION_INTERVAL_MS = 150 
PHYSICS_INTERVAL_MS = 16    # ~60 FPS
DECISION_INTERVAL_MS = 2000 # AI Brain tick

# Sprite Fallback Defaults
DEFAULT_SIZE = (128, 128)
DEFAULT_COLOR = "#8B4513" # SaddleBrown
