from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout
)

from PySide6.QtCore import Signal


class PresetControls(QWidget):

    # Signal for sending commands
    command_selected = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 100)

        # Create layout
        layout = QHBoxLayout(self)

        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)

        # Create buttons
        self.previous_button = QPushButton("◀  Previous")
        self.next_button = QPushButton("Next  ▶")

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #242424;
                color: #D5DED6;
                border: 2px solid #9EAEA2;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }

            QPushButton:hover {
                background-color: #3A3A3A;
            }

            QPushButton:pressed {
                background-color: #80FF80;
                color: black;
            }
        """

        self.previous_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

        # Add buttons to layout
        layout.addWidget(self.previous_button)
        layout.addWidget(self.next_button)

        # Connect buttons
        self.previous_button.clicked.connect(
            lambda: self.command_selected.emit("PREVIOUS")
        )

        self.next_button.clicked.connect(
            lambda: self.command_selected.emit("NEXT")
        )