from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF, QFont


class RotationPad(QWidget):

    direction_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 260)

        # Joystick configuration
        self.joystick_x = 0
        self.joystick_radius = 55
        self.max_distance = 130
        self.deadzone = 25

        self.direction = "STOP"
        self.dragging = False

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2

        # Background
        painter.setBrush(QColor("#242424"))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRoundedRect(
            10, 10, 480, 240, 30, 30
        )

        # Draw outer direction indicators
        self.draw_indicator(
            painter, center_x - 175, center_y,
            "ROTATE_LEFT", "Rotate L"
        )

        self.draw_indicator(
            painter, center_x + 175, center_y,
            "ROTATE_RIGHT", "Rotate R"
        )

        # Joystick position
        joystick_center = QPointF(
            center_x + self.joystick_x,
            center_y
        )

        # Joystick circle
        painter.setBrush(QColor("#9EAEA2"))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            joystick_center,
            self.joystick_radius,
            self.joystick_radius
        )

        # Inner ring
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#D5DED6"), 3))

        painter.drawEllipse(
            joystick_center,
            35,
            35
        )

        # Inner arrows
        self.draw_inner_arrows(
            painter,
            joystick_center.x(),
            joystick_center.y()
        )

    def draw_indicator(self, painter, x, y, direction, label):

        if self.direction == direction:
            color = QColor("#80FF80")
        else:
            color = QColor("#A0A0A0")

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        size = 18

        if direction == "ROTATE_LEFT":
            points = [
                QPointF(x - size, y),
                QPointF(x + size, y - size),
                QPointF(x + size, y + size)
            ]
        else:
            points = [
                QPointF(x + size, y),
                QPointF(x - size, y - size),
                QPointF(x - size, y + size)
            ]

        painter.drawPolygon(QPolygonF(points))

        painter.setPen(color)
        painter.setFont(QFont("Arial", 11))

        painter.drawText(
            int(x - 50),
            int(y + 25),
            100,
            25,
            Qt.AlignmentFlag.AlignCenter,
            label
        )

    def draw_inner_arrows(self, painter, x, y):

        painter.setBrush(QColor("#D5DED6"))
        painter.setPen(Qt.PenStyle.NoPen)

        size = 10
        offset = 20

        left = [
            QPointF(x - offset - size, y),
            QPointF(x - offset + size, y - size),
            QPointF(x - offset + size, y + size)
        ]

        right = [
            QPointF(x + offset + size, y),
            QPointF(x + offset - size, y - size),
            QPointF(x + offset - size, y + size)
        ]

        painter.drawPolygon(QPolygonF(left))
        painter.drawPolygon(QPolygonF(right))

    def mousePressEvent(self, event):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        center_x = self.width() / 2 + self.joystick_x
        center_y = self.height() / 2

        dx = event.position().x() - center_x
        dy = event.position().y() - center_y

        if dx * dx + dy * dy <= self.joystick_radius ** 2:
            self.dragging = True

    def mouseMoveEvent(self, event):

        if not self.dragging:
            return

        center_x = self.width() / 2

        dx = event.position().x() - center_x

        # Restrict horizontal movement
        dx = max(
            -self.max_distance,
            min(self.max_distance, dx)
        )

        self.joystick_x = dx

        if abs(dx) < self.deadzone:
            direction = "STOP"
        elif dx < 0:
            direction = "ROTATE_LEFT"
        else:
            direction = "ROTATE_RIGHT"

        if direction != self.direction:
            self.direction = direction
            self.direction_changed.emit(direction)

        self.update()

    def mouseReleaseEvent(self, event):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        if not self.dragging:
            return

        self.dragging = False
        self.joystick_x = 0

        self.direction = "STOP"
        self.direction_changed.emit("STOP")

        self.update()