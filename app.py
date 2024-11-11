import sys
import psutil
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint, QSettings
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QBrush

class SystemStatsWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_settings()  # Load the saved position

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 400, 180)  # Increased width for the additional circle

        # Custom widget to draw CPU, memory, and network speed with liquid animation
        self.widget = LiquidStatsGraph(self)
        self.setCentralWidget(self.widget)

        # Close button
        self.close_button = QPushButton("X", self)
        self.close_button.setGeometry(370, 10, 20, 20)  # Adjusted position
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
        self.timer.start(50)  # Update every 50 ms

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
        self.save_settings()  # Save the position when the widget is closed
        event.accept()

    def save_settings(self):
        settings = QSettings("kd_pc-emo", "pc_emo")
        settings.setValue("position", self.pos())

    def load_settings(self):
        settings = QSettings("kd_pc-emo", "pc_emo")
        pos = settings.value("position", QPoint(100, 100))
        self.move(pos)

class LiquidStatsGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_usage = 0
        self.memory_usage = 0
        self.wave_offset = 0
        self.upload_speed = 0
        self.download_speed = 0
        self.previous_net_io = psutil.net_io_counters()

    def update_stats(self):
        # Get CPU and memory stats
        self.cpu_usage = psutil.cpu_percent()
        self.memory_usage = psutil.virtual_memory().percent

        # Get network speeds
        net_io = psutil.net_io_counters()
        self.upload_speed = (net_io.bytes_sent - self.previous_net_io.bytes_sent) / 1024  # KB/s
        self.download_speed = (net_io.bytes_recv - self.previous_net_io.bytes_recv) / 1024  # KB/s
        self.previous_net_io = net_io  # Update previous counters

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
        self.draw_liquid_circle(painter, 150, 80, self.memory_usage, "Mem.", QColor(255, 153, 0))

        # Draw Network speed circle with gauges
        self.draw_network_circle(painter, 240, 80, self.upload_speed, self.download_speed, "Net")

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

    def draw_network_circle(self, painter, x, y, upload_speed, download_speed, label):
        radius = 23
        painter.setPen(Qt.NoPen)

        # We no longer draw a circle background for the network speed

        # Adjust max_speed for better visibility
        max_speed = 10  # Adjust this value to display small speeds better

        # Calculate lengths for the upload and download bars
        upload_bar_length = int(min(upload_speed / max_speed * (radius * 2), radius * 2))
        download_bar_length = int(min(download_speed / max_speed * (radius * 2), radius * 2))

        # Upload bar (above the circle)
        painter.setBrush(QColor(0, 153, 255))  # Blue color for upload
        painter.drawRect(x - radius, y - radius - 15, upload_bar_length, 5)

        # Download bar (below the circle)
        painter.setBrush(QColor(255, 102, 0))  # Orange color for download
        painter.drawRect(x - radius, y + radius + 10, download_bar_length, 5)

        # Display upload and download speed values above and below the bars
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(x - radius, y - radius - 20, f"↑ {upload_speed:.1f} KB/s")  # Upload speed
        painter.drawText(x - radius, y + radius + 20, f"↓ {download_speed:.1f} KB/s")  # Download speed

        # Draw the label text below the entire network section
        painter.setFont(QFont("Arial", 12))
        painter.drawText(x - 20, y + 55, label)  # Label below the circle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemStatsWidget()
    sys.exit(app.exec_())
