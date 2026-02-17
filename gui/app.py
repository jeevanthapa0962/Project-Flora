import sys
import math
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QPixmap

PRIMARY_COLOR = QColor("#00FFFF")
WARNING_COLOR = QColor("#FFA500")


# -------- GLASS PANEL BASE --------
class GlassPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def draw_glass_background(self, painter):
        rect = self.rect()

        # Glass base
        painter.setBrush(QBrush(QColor(255, 255, 255, 25)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect.adjusted(5, 5, -5, -5), 20, 20)

        # Gloss highlight
        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.drawRoundedRect(rect.adjusted(5, 5, -5, -rect.height() // 2), 20, 20)

        # Glow border
        pen = QPen(QColor(0, 255, 255, 60))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect.adjusted(5, 5, -5, -5), 20, 20)


# -------- HEXAGON PANEL --------
class HexagonPanel(GlassPanel):
    def __init__(self):
        super().__init__()
        self.opacity = 80
        self.increasing = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)

    def animate(self):
        if self.increasing:
            self.opacity += 5
            if self.opacity >= 200:
                self.increasing = False
        else:
            self.opacity -= 5
            if self.opacity <= 60:
                self.increasing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_glass_background(painter)

        size = 30
        rows, cols = 4, 3
        x_offset, y_offset = 20, 50

        for r in range(rows):
            for c in range(cols):
                color = QColor(PRIMARY_COLOR)
                color.setAlpha(self.opacity)
                painter.setPen(QPen(color, 2))

                x = x_offset + c * (size * 1.5)
                y = y_offset + r * (size * math.sqrt(3))
                if c % 2 == 1:
                    y += size * math.sqrt(3) / 2

                self.draw_hexagon(painter, x, y, size)

    def draw_hexagon(self, painter, x, y, size):
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.append(QPointF(px, py))
        painter.drawPolygon(QPolygonF(points))


# -------- TELEMETRY PANEL --------
class TelemetryPanel(GlassPanel):
    def __init__(self):
        super().__init__()
        self.bar_heights = [30, 50, 40, 60]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        t = time.time()
        self.bar_heights = [
            int(50 + 40 * math.sin(t * (i + 1)))
            for i in range(4)
        ]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_glass_background(painter)

        bar_width = 30
        gap = 10
        start_x = 20
        base_y = 200

        painter.setBrush(QBrush(PRIMARY_COLOR))
        painter.setPen(Qt.PenStyle.NoPen)

        for i, h in enumerate(self.bar_heights):
            x = start_x + i * (bar_width + gap)
            painter.drawRect(QRectF(x, base_y - h, bar_width, h))


# -------- CENTRAL REACTOR WITH ROBOT --------
class CentralReactor(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.wave_phase = 0
        self.is_paused = False
        self.robot = QPixmap("/Users/jeev_116/Downloads/flora1.png")

        # animation values
        self.float_phase = 0
        self.scale_phase = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_paused(self, paused):
        self.is_paused = paused
        self.update()

    def animate(self):
        if not self.is_paused:
            self.angle = (self.angle + 2) % 360
            self.wave_phase += 0.15

            # robot animation
            self.float_phase += 0.05
            self.scale_phase += 0.04

            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2

        main_color = WARNING_COLOR if self.is_paused else PRIMARY_COLOR

        # Glow ring
        glow_pen = QPen(QColor(main_color.red(), main_color.green(), main_color.blue(), 60))
        glow_pen.setWidth(14)
        painter.setPen(glow_pen)
        painter.drawEllipse(QPointF(cx, cy), 110, 110)

        # Main ring
        pen = QPen(main_color)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(cx, cy), 110, 110)

        # Waveform ring
        points = []
        radius = 80
        for i in range(0, 360, 6):
            angle_rad = math.radians(i)
            wave = math.sin(self.wave_phase + angle_rad * 4) * 6
            r = radius + wave
            x = cx + r * math.cos(angle_rad)
            y = cy + r * math.sin(angle_rad)
            points.append(QPointF(x, y))

        painter.drawPolyline(QPolygonF(points))

        # Glow behind robot
        painter.setBrush(QBrush(QColor(0, 255, 255, 40)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 70, 70)

        # ---- ROBOT ANIMATION ----
        if not self.robot.isNull():
            # floating motion
            float_offset = math.sin(self.float_phase) * 8

            # pulsing scale
            scale_offset = math.sin(self.scale_phase) * 8
            size = 140 + scale_offset

            scaled = self.robot.scaled(
                int(size), int(size),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            x = int(cx - scaled.width() / 2)
            y = int(cy - scaled.height() / 2 + float_offset)

            painter.drawPixmap(x, y, scaled)


# -------- MAIN WINDOW --------
class FloraGUI(QMainWindow):
    def __init__(self, pause_event):
        super().__init__()
        self.pause_event = pause_event
        self.is_paused = False

        self.setWindowTitle("FLORA HUD")
        self.resize(1000, 600)

        self.setStyleSheet("""
        QMainWindow {
            background-color: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #000000,
                stop:1 #050b14
            );
        }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        self.left_panel = HexagonPanel()
        layout.addWidget(self.left_panel)

        self.reactor = CentralReactor()
        layout.addWidget(self.reactor, stretch=2)

        self.right_panel = TelemetryPanel()
        layout.addWidget(self.right_panel)

    def mousePressEvent(self, event):
        self.toggle_pause()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.reactor.set_paused(self.is_paused)

        if self.is_paused:
            self.pause_event.set()
            print("FLORA: PAUSED")
        else:
            self.pause_event.clear()
            print("FLORA: RESUMED")


# -------- RUN FUNCTION --------
def run_gui(pause_event):
    app = QApplication(sys.argv)
    window = FloraGUI(pause_event)
    window.show()
    sys.exit(app.exec())