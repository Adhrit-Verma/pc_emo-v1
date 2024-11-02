import sys
import psutil
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QBrush

class SystemStatsWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 180)  # Reduced width and height

        # Custom widget to draw CPU and memory usage with liquid animation
        self.widget = LiquidStatsGraph(self)
        self.setCentralWidget(self.widget)

        # Close button
        self.close_button = QPushButton("X", self)
        self.close_button.setGeometry(270, 10, 20, 20)  # Adjusted position
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
        self.timer.start(50)  # Update every 50 ms for smooth animation

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

class LiquidStatsGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_usage = 0
        self.memory_usage = 0
        self.wave_offset = 0

    def update_stats(self):
        # Get system stats using psutil
        self.cpu_usage = psutil.cpu_percent()
        self.memory_usage = psutil.virtual_memory().percent

        # Update wave offset for animation
        self.wave_offset += 0.1
        if self.wave_offset > 2 * math.pi:
            self.wave_offset = 0

        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw CPU circle with liquid animation
        self.draw_liquid_circle(painter, 60, 80, self.cpu_usage, "C.P.U", QColor(0, 122, 255))

        # Draw Memory circle with liquid animation
        self.draw_liquid_circle(painter, 120, 80, self.memory_usage, "Mem.", QColor(255, 153, 0))

    def draw_liquid_circle(self, painter, x, y, usage, label, color):
        radius = 23  # Reduced radius for smaller circles
        painter.setPen(Qt.NoPen)

        # Draw background circle
        painter.setBrush(QColor(220, 220, 220))
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Calculate liquid level based on usage (inverted)
        level = usage / 100.0 * (radius * 2)

        # Clip the circle to ensure liquid stays inside
        clip_path = QPainterPath()
        clip_path.addEllipse(x - radius, y - radius, radius * 2, radius * 2)
        painter.setClipPath(clip_path)

        # Create a path for the liquid animation
        path = QPainterPath()
        path.moveTo(x - radius, y + radius)

        # Draw the liquid wave using a sinusoidal function
        wave_amplitude = 5  # Height of the wave
        wave_length = 30    # Length of the wave
        for i in range(x - radius, x + radius):
            wave_height = math.sin((i / wave_length) + self.wave_offset) * wave_amplitude
            y_pos = y + radius - level + wave_height
            path.lineTo(i, y_pos)

        path.lineTo(x + radius, y + radius)
        path.closeSubpath()

        # Draw the liquid
        painter.setBrush(QBrush(color))
        painter.drawPath(path)

        # Reset the clip to draw text
        painter.setClipping(False)

        # Center the percentage text inside the circle
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(Qt.black)
        painter.drawText(x - 9, y + 5, f"{int(usage)}%")

        # Draw the label text below the circle and in white
        painter.setFont(QFont("Arial", 12))
        painter.setPen(Qt.white)
        painter.drawText(x - 20, y + 55, label)  # Label below the circle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemStatsWidget()
    sys.exit(app.exec_())
