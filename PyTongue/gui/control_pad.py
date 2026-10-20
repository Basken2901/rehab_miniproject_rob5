import math

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF, QFont


class ControlPad(QWidget):

    # Signal for communicating joystick commands
    direction_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 500)

        # Joystick position relative to center
        self.joystick_x = 0
        self.joystick_y = 0

        # Joystick configuration
        self.joystick_radius = 75
        self.max_distance = 150
        self.deadzone = 25

        # Current direction
        self.direction = "STOP"

        # Mouse state
        self.dragging = False

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2

        # Background circle
        painter.setBrush(QColor("#242424"))
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(
            QPointF(center_x, center_y),
            245,
            245
        )

        # Outer directional indicators
        self.draw_direction_indicator(
            painter, center_x, center_y - 190,
            "FORWARD", "Forward"
        )

        self.draw_direction_indicator(
            painter, center_x, center_y + 190,
            "BACKWARD", "Back"
        )

        self.draw_direction_indicator(
            painter, center_x - 190, center_y,
            "LEFT", "Left"
        )

        self.draw_direction_indicator(
            painter, center_x + 190, center_y,
            "RIGHT", "Right"
        )

        # Joystick position
        joystick_center = QPointF(
            center_x + self.joystick_x,
            center_y + self.joystick_y
        )

        # Outer joystick circle
        painter.setBrush(QColor("#9EAEA2"))

        painter.drawEllipse(
            joystick_center,
            self.joystick_radius,
            self.joystick_radius
        )

        # Inner joystick ring
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("#D5DED6"), 4))

        painter.drawEllipse(
            joystick_center,
            50,
            50
        )

        # Draw arrows inside joystick
        self.draw_inner_arrows(
            painter,
            joystick_center.x(),
            joystick_center.y()
        )

    def draw_inner_arrows(self, painter, center_x, center_y):

        arrow_color = QColor("#D5DED6")
        painter.setBrush(arrow_color)
        painter.setPen(Qt.PenStyle.NoPen)
    
        size = 10
        offset = 32
    
        arrows = {
            "up": [
                QPointF(center_x, center_y - offset - size),
                QPointF(center_x - size, center_y - offset + size),
                QPointF(center_x + size, center_y - offset + size)
            ],
    
            "down": [
                QPointF(center_x, center_y + offset + size),
                QPointF(center_x - size, center_y + offset - size),
                QPointF(center_x + size, center_y + offset - size)
            ],
    
            "left": [
                QPointF(center_x - offset - size, center_y),
                QPointF(center_x - offset + size, center_y - size),
                QPointF(center_x - offset + size, center_y + size)
            ],
    
            "right": [
                QPointF(center_x + offset + size, center_y),
                QPointF(center_x + offset - size, center_y - size),
                QPointF(center_x + offset - size, center_y + size)
            ]
        }

        for points in arrows.values():
            painter.drawPolygon(QPolygonF(points))

    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        center_x = self.width() / 2 + self.joystick_x
        center_y = self.height() / 2 + self.joystick_y

        dx = event.position().x() - center_x
        dy = event.position().y() - center_y

        # Only allow dragging from inside joystick
        if math.hypot(dx, dy) <= self.joystick_radius:

            self.dragging = True

    def mouseMoveEvent(self, event):

        if not self.dragging:
            return

        center_x = self.width() / 2
        center_y = self.height() / 2

        dx = event.position().x() - center_x
        dy = event.position().y() - center_y

        distance = math.hypot(dx, dy)

        # Limit joystick movement
        if distance > self.max_distance:

            scale = self.max_distance / distance

            dx *= scale
            dy *= scale

        self.joystick_x = dx
        self.joystick_y = dy

        # Determine direction
        if math.hypot(dx, dy) < self.deadzone:

            direction = "STOP"

        elif abs(dx) > abs(dy):

            direction = "RIGHT" if dx > 0 else "LEFT"

        else:

            direction = "BACKWARD" if dy > 0 else "FORWARD"

        # Only emit when direction changes
        if direction != self.direction:

            self.direction = direction
            self.direction_changed.emit(direction)

        self.update()

    def mouseReleaseEvent(self, event):

        if event.button() != Qt.LeftButton or not self.dragging:
            return

        self.dragging = False

        # Return joystick to center
        self.joystick_x = 0
        self.joystick_y = 0

        self.direction = "STOP"
        self.direction_changed.emit("STOP")

        self.update()

    def draw_direction_indicator(self, painter, x, y, direction, label):

    # Highlight the active direction
        if self.direction == direction:
            color = QColor("#80FF80")
        else:
            color = QColor("#A0A0A0")

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        size = 22

        if direction == "FORWARD":
            points = [
                QPointF(x, y - size),
                QPointF(x - size, y + size),
                QPointF(x + size, y + size)
            ]

        elif direction == "BACKWARD":
            points = [
                QPointF(x, y + size),
                QPointF(x - size, y - size),
                QPointF(x + size, y - size)
            ]

        elif direction == "LEFT":
            points = [
                QPointF(x - size, y),
                QPointF(x + size, y - size),
                QPointF(x + size, y + size)
            ]

        else:  # RIGHT
            points = [
                QPointF(x + size, y),
                QPointF(x - size, y - size),
                QPointF(x - size, y + size)
            ]

        painter.drawPolygon(QPolygonF(points))

        # Draw label
        painter.setPen(color)
        painter.setFont(QFont("Arial", 12))

        painter.drawText(
            int(x - 50),
            int(y + 35),
            100,
            25,
            Qt.AlignCenter,
            label
        )