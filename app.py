import sys
import psutil
import math
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint, QSettings
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

class SystemStatsWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 200)

        # Custom widget to draw emoji face
        self.widget = EmojiFace(self)
        self.setCentralWidget(self.widget)

        # Close button
        self.close_button = QPushButton("X", self)
        self.close_button.setGeometry(170, 10, 20, 20)
        self.close_button.setStyleSheet(
            "background-color: rgba(255, 0, 0, 150);"
            "color: white;"
            "border: none;"
            "font-size: 12px;"
            "border-radius: 10px;"
        )
        self.close_button.clicked.connect(self.close)

        # Timer to update stats and animate
        self.timer = QTimer()
        self.timer.timeout.connect(self.widget.update_stats)
        self.timer.start(1000)  # Update every 1000 ms

        # Variables for dragging
        self.old_pos = None
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.old_pos)
            event.accept()

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def save_settings(self):
        settings = QSettings("kd_pc-emo", "pc_emo")
        settings.setValue("position", self.pos())

    def load_settings(self):
        settings = QSettings("kd_pc-emo", "pc_emo")
        pos = settings.value("position", QPoint(100, 100))
        self.move(pos)

class EmojiFace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_usage = 0
        self.memory_usage = 0
        self.upload_speed = 0
        self.download_speed = 0
        self.expression = "happy"
        self.blinking = False
        self.scale_factor = 1.0  # Scale for breathing animation
        self.emoji_renderer = EmojiRenderer()
        self.previous_net_io = psutil.net_io_counters()

        # Timer for blinking
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink)
        self.blink_timer.start(5000)  # Blink every 5 seconds

        # Timer for breathing animation
        self.breath_timer = QTimer()
        self.breath_timer.timeout.connect(self.breathe)
        self.breath_timer.start(50)  # Smooth breathing effect at 50 ms intervals

    def update_stats(self):
        # Update CPU and memory usage
        self.cpu_usage = psutil.cpu_percent()
        self.memory_usage = psutil.virtual_memory().percent

        # Update internet speeds
        net_io = psutil.net_io_counters()
        self.upload_speed = (net_io.bytes_sent - self.previous_net_io.bytes_sent) / 1024  # KB/s
        self.download_speed = (net_io.bytes_recv - self.previous_net_io.bytes_recv) / 1024  # KB/s
        self.previous_net_io = net_io

        # Determine expression based on CPU and memory usage thresholds
        if self.cpu_usage > 90:
            self.expression = "cpu_struggling"
        elif self.cpu_usage > 70:
            self.expression = "cpu_worried"
        elif self.memory_usage > 90:
            self.expression = "ram_exhausted"
        elif self.memory_usage > 70:
            self.expression = "ram_tired"
        else:
            self.expression = "happy"

        self.update()  # Trigger a paint event
        self.repaint()  # Force repaint immediately

    def blink(self):
        self.blinking = True
        QTimer.singleShot(200, lambda: setattr(self, 'blinking', False))  # Close eyes for 200 ms
        self.update()

    def breathe(self):
        # Breathing animation with smooth scaling effect
        self.scale_factor = 1.0 + 0.02 * math.sin(time.time() * 4.0)  # Adjust frequency and amplitude
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Render the emoji face with blinking and breathing effects
        self.emoji_renderer.render(painter, 50, 50, 100, 100, self.expression, self.blinking, self.scale_factor)

        # Display internet speeds
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(130, 180, f"↑ {self.upload_speed:.1f} KB/s")
        painter.drawText(130, 190, f"↓ {self.download_speed:.1f} KB/s")

class EmojiRenderer:
    def render(self, painter, x, y, width, height, expression, blinking, scale_factor):
        # Adjust face size for breathing effect
        scaled_width = int(width * scale_factor)
        scaled_height = int(height * scale_factor)
        face_x = x + (width - scaled_width) // 2
        face_y = y + (height - scaled_height) // 2

        # Set face color based on expression
        face_color = QColor(0, 255, 0)  # Default to green for "happy"
        if expression == "cpu_worried":
            face_color = QColor(255, 165, 0)  # Orange
        elif expression == "cpu_struggling":
            face_color = QColor(255, 0, 0)  # Red
        elif expression == "ram_tired":
            face_color = QColor(255, 255, 0)  # Yellow
        elif expression == "ram_exhausted":
            face_color = QColor(255, 0, 0)  # Red

        # Draw face circle
        painter.setBrush(face_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(face_x, face_y, scaled_width, scaled_height)

        # Draw the mouth based on the expression (independent of blinking)
        painter.setPen(QPen(Qt.black, 2))
        if expression == "happy":
            painter.drawArc(face_x + 25, face_y + 50, 50, 20, 0, -180 * 16)  # Smile
        elif expression == "cpu_worried" or expression == "ram_tired":
            painter.drawArc(face_x + 25, face_y + 60, 50, 20, 180 * 16, -180 * 16)  # Frown
        elif expression == "cpu_struggling" or expression == "ram_exhausted":
            painter.drawArc(face_x + 25, face_y + 65, 50, 20, 180 * 16, -180 * 16)  # Deeper frown

        # Draw eyes based on blinking state
        painter.setBrush(QColor(0, 0, 0))
        if blinking:
            # Draw closed eyes as short horizontal lines for blinking
            painter.drawLine(face_x + 25, face_y + 35, face_x + 35, face_y + 35)  # Left eye closed
            painter.drawLine(face_x + 65, face_y + 35, face_x + 75, face_y + 35)  # Right eye closed
        else:
            # Draw normal eyes based on expression (not affected by blinking)
            if expression == "cpu_struggling":
                painter.drawEllipse(face_x + 20, face_y + 30, 15, 15)  # Left eye
                painter.drawEllipse(face_x + 65, face_y + 30, 15, 15)  # Right eye
                painter.setBrush(QColor(255, 255, 255))
                painter.drawEllipse(face_x + 25, face_y + 35, 5, 5)  # Left pupil
                painter.drawEllipse(face_x + 70, face_y + 35, 5, 5)  # Right pupil
            else:
                # Regular eyes for other expressions
                painter.drawEllipse(face_x + 25, face_y + 30, 10, 10)  # Left eye
                painter.drawEllipse(face_x + 65, face_y + 30, 10, 10)  # Right eye

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemStatsWidget()
    sys.exit(app.exec_())
