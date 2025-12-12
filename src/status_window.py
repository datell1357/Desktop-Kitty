from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor, QCursor

class StatusWindow(QWidget):
    def __init__(self, pet_status, parent=None):
        super().__init__(parent)
        self.pet_status = pet_status
        
        # Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(220, 200)

        # Drag variables
        self.drag_pos = None

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Styled Container (Round corners, border)
        self.container = QFrame(self)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QFrame#Container {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #E0E0E0;
            }
        """)
        layout.addWidget(self.container)

        # Container Layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # --- Title Bar ---
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(35) # Title bar height
        self.title_bar.setObjectName("TitleBar")
        # Top-left, Top-right radius should match container radius minus border width roughly?
        # Actually CSS border-radius on child clips weirdly sometimes.
        # Let's try styling TitleBar.
        self.title_bar.setStyleSheet("""
            QWidget#TitleBar {
                background-color: #E0F7FA;
                border-top-left-radius: 13px;
                border-top-right-radius: 13px;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0) # Left, Top, Right, Bottom

        self.lbl_title = QLabel("고양이 상태")
        self.lbl_title.setStyleSheet("font-weight: bold; color: #555;")
        title_layout.addWidget(self.lbl_title)

        title_layout.addStretch()

        # Close Button
        self.btn_close = QPushButton("X")
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FF8A80;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                border: none;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        title_layout.addWidget(self.btn_close)
        
        container_layout.addWidget(self.title_bar)
        
        # --- Content Area ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 15)
        
        # Info
        self.lbl_birth = QLabel("생후: -")
        self.lbl_birth.setStyleSheet("font-family: 'Malgun Gothic'; color: #333;")
        content_layout.addWidget(self.lbl_birth)
        
        self.lbl_mood = QLabel("기분: -")
        self.lbl_mood.setStyleSheet("font-family: 'Malgun Gothic'; color: #333;")
        content_layout.addWidget(self.lbl_mood)
        
        content_layout.addSpacing(10)
        
        # Hunger
        h_layout = QHBoxLayout()
        h_label = QLabel("배고픔")
        h_label.setStyleSheet("font-family: 'Malgun Gothic'; color: #333;")
        h_layout.addWidget(h_label)
        
        h_layout.addStretch()
        self.lbl_hunger_val = QLabel("(100/100)")
        self.lbl_hunger_val.setStyleSheet("color: #888; font-size: 11px;")
        h_layout.addWidget(self.lbl_hunger_val)
        content_layout.addLayout(h_layout)

        self.bar_hunger = QProgressBar()
        self.bar_hunger.setFixedHeight(12)
        self.bar_hunger.setTextVisible(False)
        content_layout.addWidget(self.bar_hunger)
        
        content_layout.addStretch()
        
        container_layout.addWidget(content_widget)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
        
        self.update_ui()

    def update_ui(self):
        # Update Labels
        self.lbl_birth.setText(f"생후: {self.pet_status.get_birth_time_str()}")
        self.lbl_mood.setText(f"기분: {self.pet_status.get_mood()}")
        
        hunger = self.pet_status.get_hunger()
        self.bar_hunger.setValue(hunger)
        self.lbl_hunger_val.setText(f"({hunger}/100)")
        
        if hunger > 70: 
            color = "#90EE90"
        elif hunger > 30: 
            color = "#FFD700"
        else: 
            color = "#FF6B6B"
        
        self.bar_hunger.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #CCC;
                border-radius: 6px;
                background-color: #F0F0F0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    # Drag Logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicked inside Container -> TitleBar area
            # Map global pos to local container coordinates
            local_pos = self.container.mapFromGlobal(event.globalPosition().toPoint())
            
            # Allow drag if clicked in top 35 pixels (TitleBar height)
            # Use 'mapFromGlobal' to be sure, or just simple checking since title_bar is at top
            if local_pos.y() <= 35:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
