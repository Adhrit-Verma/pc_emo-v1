import sys
import psutil
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
        self.emoji_renderer = EmojiRenderer()
        self.previous_net_io = psutil.net_io_counters()

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Render the emoji face based on the expression
        self.emoji_renderer.render(painter, 50, 50, 100, 100, self.expression)

        # Display internet speeds
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(130, 180, f"↑ {self.upload_speed:.1f} KB/s")
        painter.drawText(130, 190, f"↓ {self.download_speed:.1f} KB/s")

class EmojiRenderer:
    def render(self, painter, x, y, width, height, expression):
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
        painter.drawEllipse(x, y, width, height)

        # Draw eyes and mouth based on expression
        painter.setBrush(QColor(0, 0, 0))
        if expression == "happy":
            painter.drawEllipse(x + 25, y + 30, 10, 10)  # Left eye
            painter.drawEllipse(x + 65, y + 30, 10, 10)  # Right eye
            painter.setPen(QPen(Qt.black, 2))
            painter.drawArc(x + 25, y + 50, 50, 20, 0, -180 * 16)  # Smile
        elif expression == "cpu_worried" or expression == "ram_tired":
            # Worried eyes with a focused, fatigued expression
            painter.drawEllipse(x + 25, y + 30, 10, 10)  # Left eye
            painter.drawEllipse(x + 65, y + 30, 10, 10)  # Right eye
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawArc(x + 25, y + 60, 50, 20, 180 * 16, -180 * 16)  # Frown
        elif expression == "cpu_struggling":
            # Struggling eyes with an exhausted look
            painter.drawEllipse(x + 20, y + 30, 15, 15)  # Left eye
            painter.drawEllipse(x + 65, y + 30, 15, 15)  # Right eye
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(x + 25, y + 35, 5, 5)  # Rolling pupil left
            painter.drawEllipse(x + 70, y + 35, 5, 5)  # Rolling pupil right
            painter.setPen(QPen(Qt.black, 2))
            painter.drawArc(x + 25, y + 65, 50, 20, 180 * 16, -180 * 16)  # Deeper frown
        elif expression == "ram_exhausted":
            # Dizzy or tired face for memory overload
            painter.drawEllipse(x + 25, y + 30, 10, 10)  # Left eye
            painter.drawEllipse(x + 65, y + 30, 10, 10)  # Right eye
            painter.setPen(QPen(Qt.black, 2))
            painter.drawArc(x + 25, y + 60, 50, 20, 180 * 16, -180 * 16)  # Tired frown

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemStatsWidget()
    sys.exit(app.exec_())
