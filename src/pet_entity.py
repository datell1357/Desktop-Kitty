import sys
import random
from PyQt6.QtWidgets import QMainWindow, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRect
from PyQt6.QtGui import QPainter, QAction, QCursor

from .constants import *
from .sprite_manager import SpriteManager
from .state_machine import StateMachine
from .config import ConfigManager

class PetEntity(QMainWindow):
    """The main transparent window entity for the desktop pet."""
    
    def __init__(self):
        super().__init__()
        
        # Managers
        self.config = ConfigManager()
        self.sprites = SpriteManager()
        self.fsm = StateMachine(self)
        
        # Physics State
        self.velocity = QPointF(0, 0) # x, y velocity (Float for smooth gravity)
        self.is_dragging = False
        self.drag_position = QPoint()

        self.direction = 1 # 1 for Right, -1 for Left
        
        # Setup Window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Resize window to default sprite size
        w, h = DEFAULT_SIZE
        self.resize(w, h)
        
        # Load Position (Default: Bottom Right)
        screen_geo = QApplication.primaryScreen().availableGeometry()
        default_x = screen_geo.width() - w - 100
        default_y = screen_geo.height() - h - 50
        
        x = self.config.get("last_x", default_x)
        y = self.config.get("last_y", default_y)
        
        # Add random offset to prevent stacking when opening multiple instances
        x += random.randint(-50, 50)
        y += random.randint(-50, 50)
        
        # Keep within screen bounds (basic check)
        x = max(0, min(x, screen_geo.width() - w))
        y = max(0, min(y, screen_geo.height() - h))
        
        self.move(int(x), int(y))
        
        # Timers
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(ANIMATION_INTERVAL_MS)
        
        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.update_physics)
        self.physics_timer.start(PHYSICS_INTERVAL_MS)
        
        # Context Menu
        self.init_context_menu()

    def init_context_menu(self):
        self.context_menu = QMenu(self)
        
        self.action_jump = QAction("Jump!", self)
        self.action_jump.triggered.connect(self.trigger_user_jump)
        self.context_menu.addAction(self.action_jump)
        
        self.action_wait = QAction("Wait", self)
        self.action_wait.setCheckable(True)
        self.action_wait.setChecked(self.config.get("wait_mode", False))
        self.action_wait.triggered.connect(self.toggle_wait_mode)
        self.context_menu.addAction(self.action_wait)

        self.context_menu.addSeparator()
        
        self.action_sit = QAction("Sit Down", self)
        self.action_sit.triggered.connect(lambda: self.fsm.set_state("sit", force=True))
        self.context_menu.addAction(self.action_sit)

        self.action_sleep = QAction("Go to Sleep", self)
        self.action_sleep.triggered.connect(lambda: self.fsm.set_state("sleep", force=True))
        self.context_menu.addAction(self.action_sleep)
        
        self.action_follow = QAction("Follow Mouse", self)
        self.action_follow.setCheckable(True)
        self.action_follow.setChecked(self.config.get("follow_mode", False))
        self.action_follow.triggered.connect(self.toggle_follow_mode)
        self.context_menu.addAction(self.action_follow)
        
        self.context_menu.addSeparator()
        
        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.close_app)
        self.context_menu.addAction(action_exit)

    def trigger_user_jump(self):
        # User defined jump: Random direction
        self.direction = random.choice([-1, 1])
        self.fsm.set_state("jump", force=True)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Determine Sprite Key
        state = self.fsm.current_state
        sprite_key = state
        
        if state == "walk" or state == "follow":
            sprite_key = "walk"
        elif state == "run": # If we add run later
            sprite_key = "run_left" if self.direction == -1 else "run_right"
            
        # Get current frame
        frame = self.sprites.get_frame(sprite_key, self.fsm.frame_index)
        
        if frame:
            # Flip Logic
            need_flip = False
            
            if state in ["walk", "follow", "idle", "sit"]:
                 # Left-Facing Base: Flip if Right (1)
                 if self.direction == 1:
                     need_flip = True
            elif state in ["drag", "jump", "sleep"]:
                 # Right-Facing Base: Flip if Left (-1)
                 if self.direction == -1:
                     need_flip = True
            
            if need_flip:
                 from PyQt6.QtGui import QTransform
                 frame = frame.transformed(QTransform().scale(-1, 1))
                
            painter.drawPixmap(0, 0, frame)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.fsm.set_state("drag", force=True)
            self.fsm.locked = True
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu.exec(event.globalPosition().toPoint())
            event.accept()

    def is_valid_location(self, x, y):
        """Checks if the pet's window rect at (x, y) is fully within valid screen space."""
        # To prevent "head going into edge", we ensure ALL corners are in valid screens.
        # This allows straddling between monitors (e.g. Left corners in Monitor 1, Right in Monitor 2)
        # but prevents any part from being in the void.
        
        w, h = self.width(), self.height()
        points = [
            QPoint(int(x), int(y)),                  # Top-Left
            QPoint(int(x + w), int(y)),              # Top-Right
            QPoint(int(x), int(y + h)),              # Bottom-Left
            QPoint(int(x + w), int(y + h))           # Bottom-Right
        ]
        
        screens = QApplication.screens()
        
        for p in points:
            # Check if this point is in ANY screen
            point_valid = False
            for screen in screens:
                if screen.availableGeometry().contains(p):
                    point_valid = True
                    break
            
            if not point_valid:
                return False
                
        return True

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            
            # Helper: Determine drag direction
            dx = new_pos.x() - self.pos().x()
            if abs(dx) > 2: # Threshold to prevent jitter
                self.direction = 1 if dx > 0 else -1
            
            # Multi-monitor bounds check:
            # Only allow move if it stays somewhat within valid screen area.
            # However, for drag, strict checking feels bad if you briefly clip the edge.
            # But user asked to STOP at edge. 
            # So we check if the new position is valid. If not, we don't move (effectively clamping to valid area).
            
            if self.is_valid_location(new_pos.x(), new_pos.y()):
                self.move(new_pos)
            else:
                 # Optional: Try to clamp to nearest valid screen edge? 
                 # For now, just refusing to move into void is simple and effective.
                 pass
                 
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.fsm.locked = False
            # Only revert to Idle if we were dragging.
            # If a Double Click triggered a Jump/Sit/Sleep, do NOT overwrite it with Idle.
            if self.fsm.current_state == "drag":
                self.fsm.set_state("idle", force=True)
            self.save_position()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Random reaction
            reactions = ["sit", "jump", "sleep"]
            choice = random.choice(reactions)
            
            if choice == "jump":
                self.trigger_user_jump()
            else:
                self.fsm.set_state(choice, force=True)
            event.accept()

    def update_animation(self):
        self.fsm.step_animation()
        self.update() # Trigger repaint

    def update_physics(self):
        if self.is_dragging:
            return

        # FSM Logic Updates
        self.fsm.update(PHYSICS_INTERVAL_MS)
        
        # Apply Movement (No Gravity)
        current_pos = self.pos()
        
        if self.fsm.current_state == "walk":
            # Initialize random walk direction at start of state
            if self.fsm.state_timer <= PHYSICS_INTERVAL_MS * 2:
                import math
                import random
                angle = random.uniform(0, 2 * math.pi)
                speed = MOVE_SPEED
                self.velocity = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
                
                # Set visual facing based on X
                if self.velocity.x() != 0:
                    self.direction = 1 if self.velocity.x() > 0 else -1

            # Move
            current_pos = self.pos()
            new_x = current_pos.x() + self.velocity.x()
            new_y = current_pos.y() + self.velocity.y()
            
            if not self.is_valid_location(new_x, current_pos.y()):
                 self.velocity.setX(-self.velocity.x())
                 self.direction = 1 if self.velocity.x() > 0 else -1
                 new_x = current_pos.x() # Cancel move
                 
            if not self.is_valid_location(new_x, new_y):
                 self.velocity.setY(-self.velocity.y())
                 new_y = current_pos.y() # Cancel move

            self.move(int(new_x), int(new_y))
            
        elif self.fsm.current_state == "jump":
            # 45 Degree Jump Physics
            dt = PHYSICS_INTERVAL_MS / 1000.0
            
            # Initialize Jump Velocity (Front-Up 45 deg) & Capture Floor
            if self.fsm.state_timer <= PHYSICS_INTERVAL_MS * 2:
                # 45 deg = equal x and y components
                # Jump Power
                POWER = 400 # px/s ( Increased for 1.7x height)
                # X direction depends on facing
                vx = POWER * self.direction * 0.707 # cos(45)
                vy = -POWER * 0.707 # sin(45) - moving Up is negative Y
                self.velocity = QPointF(vx, vy)
                self.jump_start_y = float(self.pos().y())
            elif not hasattr(self, 'jump_start_y'):
                # Safety fallback if jump started mid-logic or somehow missed
                self.jump_start_y = float(self.pos().y())
            
            # Gravity
            GRAVITY = 800 # px/s^2
            self.velocity.setY(self.velocity.y() + GRAVITY * dt)
            
            # Move
            next_x = current_pos.x() + self.velocity.x() * dt
            next_y = current_pos.y() + self.velocity.y() * dt
            
            # Wall Bounce (Check if next X is valid)
            if not self.is_valid_location(next_x, current_pos.y()):
                self.velocity.setX(-self.velocity.x())
                next_x = current_pos.x() # Cancel X move
                self.direction *= -1

            # Landing Check (Floor = start_y)
            # We assume floor is always valid if start_y was valid? 
            # Simpler check: If falling and below start Y, land.
            if self.velocity.y() > 0 and next_y >= self.jump_start_y:
                 next_y = self.jump_start_y
                 self.velocity = QPointF(0, 0)
                 self.move(int(next_x), int(next_y))
                 self.fsm.set_state("idle")
            else:
                 self.move(int(next_x), int(next_y))
        
        elif self.fsm.current_state == "follow":
            import math
            target = QCursor.pos()
            # Calculate center of pet
            cx = current_pos.x() + self.width() // 2
            cy = current_pos.y() + self.height() // 2
            
            dx = target.x() - cx
            dy = target.y() - cy
            dist = math.hypot(dx, dy)
            
            # 1. Direction Facing (Visual Only)
            if abs(dx) > 5:
                self.direction = 1 if dx > 0 else -1
            
            # 2. Movement
            dist_threshold = 20 # Stop slightly before cursor
            
            if dist > dist_threshold:
                # Normalize and scale by speed
                speed = 2.5 # Slower follow speed
                vx = (dx / dist) * speed
                vy = (dy / dist) * speed
                
                # Move
                next_x = current_pos.x() + vx
                next_y = current_pos.y() + vy
                
                # Validity Check
                if self.is_valid_location(next_x, next_y):
                    self.move(int(next_x), int(next_y))
                else:
                    # Try to move as close as possible? 
                    # For now just stop at edge.
                    pass
            else:
                 # Arrived: Sit down
                 self.direction *= -1
                 self.fsm.set_state("sit")

        else:
            # Check for Persistent Follow Mode
            if self.config.get("follow_mode", False) and not self.is_dragging:
                 # If in Idle/Sit/Walk/Sleep, check distance
                 target = QCursor.pos()
                 cx = current_pos.x() + self.width() // 2
                 cy = current_pos.y() + self.height() // 2
                 
                 dx = target.x() - cx
                 dy = target.y() - cy
                 dist = (dx**2 + dy**2)**0.5
                 
                 # Trigger follow if mouse moves away (threshold)
                 if dist > 60: 
                     self.fsm.set_state("follow")

    def toggle_follow_mode(self):
        new_val = not self.config.get("follow_mode")
        self.config.set("follow_mode", new_val)
        self.action_follow.setChecked(new_val)
        if new_val:
            self.fsm.set_state("follow", force=True)

    def toggle_wait_mode(self):
        new_val = not self.config.get("wait_mode")
        self.config.set("wait_mode", new_val)
        self.action_wait.setChecked(new_val)
        
        if new_val:
            # When enabling Wait, force Sit immediately
            self.fsm.set_state("sit", force=True)

    def toggle_floating(self):
        new_val = not self.config.get("floating_mode")
        self.config.set("floating_mode", new_val)
        self.action_float.setChecked(new_val)

    def save_position(self):
        self.config.set("last_x", self.pos().x())
        self.config.set("last_y", self.pos().y())

    def close_app(self):
        self.save_position()
        QApplication.quit()
