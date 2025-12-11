import os
import random
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QBrush
from PyQt6.QtCore import Qt
from .constants import SPRITES_DIR, DEFAULT_SIZE, DEFAULT_COLOR

class SpriteManager:
    """Handles loading sprites and generating fallbacks if missing."""

    def __init__(self):
        self.sprites = {
            "idle": [],
            "sit": [],
            "sleep": [],
            "drag": [],
            "jump": [],
            "walk": [],
        }
        self.load_sprites()

    def load_sprites(self):
        """Loads images from disk or creates placeholders."""
        from PIL import Image, ImageOps
        import numpy as np
        
        print(f"DEBUG: Looking for sprites in {SPRITES_DIR}")
        for state in self.sprites.keys():
            path = os.path.join(SPRITES_DIR, state)
            if os.path.exists(path):
                files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.gif'))])
                print(f"DEBUG: Found {len(files)} files for state '{state}' in {path}")
                for f in files:
                    full_path = os.path.join(path, f)
                    try:
                        pil_img = Image.open(full_path).convert("RGBA")
                        
                        # 1. Smart Background Removal (Flood Fill)
                        # Instead of removing ALL white pixels (which eats paws),
                        # we only remove white pixels connected to the background (corner).
                        
                        from PIL import ImageDraw
                        
                        # Ensure RGBA
                        pil_img = pil_img.convert("RGBA")
                        
                        # Flood fill from (0,0) with transparency
                        # Tolerance helps with collecting compression artifacts
                        # Note: Pillow's floodfill might not support tolerance well in all versions,
                        # but we can try targeting the color at (0,0).
                        
                        # Simplified approach:
                        # 1. Get background color from top-left pixel
                        bg_color = pil_img.getpixel((0, 0))
                        
                        # 2. Use ImageDraw to floodfill with transparent (0,0,0,0)
                        # Threshold handles slight off-whites
                        # Increased threshold to 60 to remove halos
                        thresh_val = 60
                        ImageDraw.floodfill(pil_img, (0, 0), (0, 0, 0, 0), thresh=thresh_val)
                        
                        # Also try other corners if needed, but (0,0) usually covers unconnected background
                        w, h = pil_img.size
                        ImageDraw.floodfill(pil_img, (w-1, 0), (0, 0, 0, 0), thresh=thresh_val)
                        ImageDraw.floodfill(pil_img, (0, h-1), (0, 0, 0, 0), thresh=thresh_val)
                        ImageDraw.floodfill(pil_img, (w-1, h-1), (0, 0, 0, 0), thresh=thresh_val)

                        # 2. Resize
                        scale_factor = 1.0
                        # walk: Reverted to 1.0 as per user request
                        if state in ["sleep", "drag"]:
                            scale_factor = 0.8
                            
                        if scale_factor != 1.0:
                            target_w = int(DEFAULT_SIZE[0] * scale_factor)
                            target_h = int(DEFAULT_SIZE[1] * scale_factor)
                            
                            # Resize the content
                            pil_img = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                            
                            # Paste into a transparent frame of DEFAULT_SIZE to maintain alignment
                            base_img = Image.new("RGBA", DEFAULT_SIZE, (0, 0, 0, 0))
                            
                            x_offset = (DEFAULT_SIZE[0] - target_w) // 2
                            # Align Center: (Frame Height - Image Height) // 2
                            y_offset = (DEFAULT_SIZE[1] - target_h) // 2
                            
                            base_img.paste(pil_img, (x_offset, y_offset))
                            pil_img = base_img
                        else:
                            pil_img = pil_img.resize(DEFAULT_SIZE, Image.Resampling.LANCZOS)
                        
                        # Convert to QPixmap
                        data = pil_img.tobytes("raw", "BGRA")
                        qim = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_ARGB32)
                        pixmap = QPixmap.fromImage(qim)
                        self.sprites[state].append(pixmap)
                            
                    except Exception as e:
                        print(f"ERROR: Processing {full_path}: {e}")

            else:
                 print(f"DEBUG: Path not found {path}")
            
            # If no sprites found, generate a fallback
            if not self.sprites[state]:
                self.sprites[state].append(self._generate_fallback(state))

    def _generate_fallback(self, state_name):
        """Generates a procedural placeholder texture."""
        img = QImage(DEFAULT_SIZE[0], DEFAULT_SIZE[1], QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color based on state
        color = QColor(DEFAULT_COLOR)
        if state_name == "sleep":
            color = color.darker(150)
        elif state_name == "drag":
            color = color.lighter(150)
            
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw a simple cat shape (ellipse body + circle head)
        painter.drawEllipse(20, 40, 80, 50) # Body
        painter.drawEllipse(80, 10, 40, 40) # Head
        
        # Eyes
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(90, 20, 8, 8)
        painter.drawEllipse(105, 20, 8, 8)
        
        # Text
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(30, 70, state_name.upper())

        painter.end()
        return QPixmap.fromImage(img)

    def get_frame(self, state, index):
        """Returns the specific frame for a state, looping if necessary."""
        frames = self.sprites.get(state, [])
        if not frames:
            return None
        return frames[index % len(frames)]

    def get_frame_count(self, state):
        return len(self.sprites.get(state, []))
