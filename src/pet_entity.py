import sys
import random
from PyQt6.QtWidgets import QMainWindow, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRect
from PyQt6.QtGui import QPainter, QAction, QCursor

from .constants import *
from .sprite_manager import SpriteManager
from .state_machine import StateMachine
from .config import ConfigManager
from .pet_status import PetStatus
from .status_window import StatusWindow

class PetEntity(QMainWindow):
    """The main transparent window entity for the desktop pet."""
    
    def __init__(self):
        super().__init__()
        
        # Managers
        self.config = ConfigManager()
        self.sprites = SpriteManager()
        self.fsm = StateMachine(self)
        self.status = PetStatus()
        self.status_window = None
        
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
        
        self.action_feed = QAction("Feed (+40 Hunger)", self)
        self.action_feed.triggered.connect(self.start_feed_sequence)
        self.context_menu.addAction(self.action_feed)
        
        self.action_toilet = QAction("Go to Toilet", self)
        self.action_toilet.triggered.connect(self.start_toilet_sequence)
        self.action_toilet.setEnabled(False) # Default disabled
        self.context_menu.addAction(self.action_toilet)
        
        self.context_menu.addSeparator()
        
        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.close_app)
        self.context_menu.addAction(action_exit)
        
        # --- Debug Menu ---
        self.context_menu.addSeparator()
        debug_menu = self.context_menu.addMenu("Debug Tools")
        
        action_full_hunger = QAction("Full Hunger (100)", self)
        action_full_hunger.triggered.connect(lambda: self.status.debug_set_full_hunger() if self.status else None)
        debug_menu.addAction(action_full_hunger)
        
        action_hunger_30 = QAction("Set Hunger 30", self)
        action_hunger_30.triggered.connect(lambda: self.status.debug_set_hunger_30() if self.status else None)
        debug_menu.addAction(action_hunger_30)
        
        action_reset_cooldown = QAction("Reset Feed Cooldown", self)
        action_reset_cooldown.triggered.connect(lambda: self.status.debug_reset_feed_cooldown() if self.status else None)
        debug_menu.addAction(action_reset_cooldown)
        
        action_force_uncomfy = QAction("Force Uncomfortable", self)
        action_force_uncomfy.triggered.connect(self.debug_trigger_uncomfortable)
        debug_menu.addAction(action_force_uncomfy)

    def trigger_user_jump(self):
        # User defined jump: Random direction
        self.direction = random.choice([-1, 1])
        self.fsm.set_state("jump", force=True)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 1. Draw Pet
        state = self.fsm.current_state
        sprite_key = state
        
        if state == "walk" or state == "follow":
            sprite_key = "walk"
        elif state == "run":
            sprite_key = "walk"
            
        # Determine Frame Index logic
        frame_idx = self.fsm.frame_index
        
        # Mood-based static branch for idle/sit
        if state in ["idle", "sit"] and self.status:
            mood = self.status.get_mood()
            # Mood logic:
            # - Happy (Default): index 0
            # - Uncomfortable OR Bad: index 1 (bad.png) if available
            
            if mood == "행복":
                frame_idx = 0
            else:
                # Uncomfortable or Bad uses bad.png
                if self.sprites.get_frame_count(state) > 1:
                    frame_idx = 1
                else:
                    frame_idx = 0
        
        # Get current frame
        frame = self.sprites.get_frame(sprite_key, frame_idx)
        
        if frame:
            # Flip Logic
            need_flip = False
            
            if state in ["walk", "follow", "idle", "sit", "feed", "toilet"]:
                 if self.direction == 1:
                     need_flip = True
            elif state in ["drag", "jump", "sleep"]:
                 if self.direction == -1:
                     need_flip = True
            
            if need_flip:
                 from PyQt6.QtGui import QTransform
                 frame = frame.transformed(QTransform().scale(-1, 1))
                
            painter.drawPixmap(0, 0, frame)

    def mousePressEvent(self, event):
        # BLOCK INTERACTION if performing blocking actions
        if self.fsm.current_state in ["feed", "toilet"]:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.fsm.set_state("drag", force=True)
            self.fsm.locked = True
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # Update Actions
            if self.status:
                # Feed
                self.action_feed.setEnabled(self.status.can_feed())
                if not self.status.can_feed():
                    self.action_feed.setText("Feed (Cooldown...)")
                else:
                    self.action_feed.setText("Feed (+40 Hunger)")
                
                # Toilet
                self.action_toilet.setEnabled(self.status.is_uncomfortable)
                
            self.context_menu.exec(event.globalPosition().toPoint())
            event.accept()

    def is_valid_location(self, x, y):
        """Checks if the pet's window rect at (x, y) is fully within valid screen space."""
        w, h = self.width(), self.height()
        points = [
            QPoint(int(x), int(y)),
            QPoint(int(x + w), int(y)),
            QPoint(int(x), int(y + h)),
            QPoint(int(x + w), int(y + h))
        ]
        
        screens = QApplication.screens()
        
        for p in points:
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
            dx = new_pos.x() - self.pos().x()
            if abs(dx) > 2: 
                self.direction = 1 if dx > 0 else -1
            
            if self.is_valid_location(new_pos.x(), new_pos.y()):
                self.move(new_pos)
            else:
                 pass
                 
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.fsm.locked = False
            if self.fsm.current_state == "drag":
                self.fsm.set_state("idle", force=True)
            self.save_position()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.status_window is None:
                self.status_window = StatusWindow(self.status)
            
            pet_pos = self.pos()
            status_x = pet_pos.x() + self.width() + 10
            status_y = pet_pos.y() - 50
            
            self.status_window.move(status_x, status_y)
            self.status_window.show()
            self.status_window.raise_()
            self.status_window.activateWindow()
            
            event.accept()

    def update_animation(self):
        self.fsm.step_animation()
        self.update() # Trigger repaint
        
        # Check mood lazy update occasionally? 
        # Actually paintEvent calls get_mood indirectly via icon check? 
        # No, init checked it.
        # Let's explicitly trigger mood update for logic (e.g. uncomfortable transition)
        if self.status:
            self.status.update_mood_status()

    def update_physics(self):
        if self.is_dragging:
            return

        # FSM Logic Updates
        self.fsm.update(PHYSICS_INTERVAL_MS)
        
        # Apply Movement (No Gravity)
        current_pos = self.pos()
        
        if self.fsm.current_state == "walk":
            if self.fsm.state_timer <= PHYSICS_INTERVAL_MS * 2:
                import math
                import random
                angle = random.uniform(0, 2 * math.pi)
                speed = MOVE_SPEED
                self.velocity = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
                
                if self.velocity.x() != 0:
                    self.direction = 1 if self.velocity.x() > 0 else -1

            current_pos = self.pos()
            new_x = current_pos.x() + self.velocity.x()
            new_y = current_pos.y() + self.velocity.y()
            
            if not self.is_valid_location(new_x, current_pos.y()):
                 self.velocity.setX(-self.velocity.x())
                 self.direction = 1 if self.velocity.x() > 0 else -1
                 new_x = current_pos.x() 
                 
            if not self.is_valid_location(new_x, new_y):
                 self.velocity.setY(-self.velocity.y())
                 new_y = current_pos.y() 

            self.move(int(new_x), int(new_y))
            
        elif self.fsm.current_state == "jump":
            dt = PHYSICS_INTERVAL_MS / 1000.0
            
            if self.fsm.state_timer <= PHYSICS_INTERVAL_MS * 2:
                POWER = 400 
                vx = POWER * self.direction * 0.707 
                vy = -POWER * 0.707 
                self.velocity = QPointF(vx, vy)
                self.jump_start_y = float(self.pos().y())
            elif not hasattr(self, 'jump_start_y'):
                self.jump_start_y = float(self.pos().y())
            
            GRAVITY = 800 
            self.velocity.setY(self.velocity.y() + GRAVITY * dt)
            
            next_x = current_pos.x() + self.velocity.x() * dt
            next_y = current_pos.y() + self.velocity.y() * dt
            
            if not self.is_valid_location(next_x, current_pos.y()):
                self.velocity.setX(-self.velocity.x())
                next_x = current_pos.x() 
                self.direction *= -1

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
            cx = current_pos.x() + self.width() // 2
            cy = current_pos.y() + self.height() // 2
            
            dx = target.x() - cx
            dy = target.y() - cy
            dist = math.hypot(dx, dy)
            
            if abs(dx) > 5:
                self.direction = 1 if dx > 0 else -1
            
            dist_threshold = 20 
            
            if dist > dist_threshold:
                speed = 2.5 
                vx = (dx / dist) * speed
                vy = (dy / dist) * speed
                
                next_x = current_pos.x() + vx
                next_y = current_pos.y() + vy
                
                if self.is_valid_location(next_x, next_y):
                    self.move(int(next_x), int(next_y))
                else:
                    pass
            else:
                 self.direction *= -1
                 self.fsm.set_state("sit")

        else:
            if self.config.get("follow_mode", False) and not self.is_dragging:
                 target = QCursor.pos()
                 cx = current_pos.x() + self.width() // 2
                 cy = current_pos.y() + self.height() // 2
                 
                 dx = target.x() - cx
                 dy = target.y() - cy
                 dist = (dx**2 + dy**2)**0.5
                 
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
            self.fsm.set_state("sit", force=True)

    def toggle_floating(self):
        new_val = not self.config.get("floating_mode")
        self.config.set("floating_mode", new_val)
        self.action_float.setChecked(new_val)

    def save_position(self):
        self.config.set("last_x", self.pos().x())
        self.config.set("last_y", self.pos().y())

    def close_app(self):
        self.close()

    def closeEvent(self, event):
        self.save_position()
        
        if self.status_window:
            self.status_window.close()

        if self.status:
            try:
                self.status.save_data()
            except Exception as e:
                print(f"Error saving PetStatus: {e}")
        event.accept()

    def start_feed_sequence(self):
        if not self.status or not self.status.can_feed():
            return
            
        self.fsm.set_state("feed", force=True)
        QTimer.singleShot(5200, self.finish_feed)
        
    def finish_feed(self):
        if self.status:
            self.status.feed(40)
            self.status.record_feed()

    def start_toilet_sequence(self):
        if not self.status or not self.status.is_uncomfortable:
            return
        
        self.fsm.set_state("toilet", force=True)
        QTimer.singleShot(4500, self.finish_toilet)
        
    def finish_toilet(self):
        if self.status:
            self.status.poop()
            self.update() # Trigger repaint to remove icon

    def debug_trigger_uncomfortable(self):
        if self.status:
            self.status.debug_set_uncomfortable()
            self.update() # Repaint for icon
