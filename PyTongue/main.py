import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from PySide6.QtCore import Qt

from gui.control_pad import ControlPad
from gui.rotation_pad import RotationPad
from gui.preset_controls import PresetControls

from controller.command_manager import CommandManager


class PyTongueGUI(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyTongue")
        self.setFixedSize(540, 1000)

        # Create Command Manager
        self.command_manager = CommandManager()

        # Main container
        central_widget = QWidget()
        central_widget.setStyleSheet(
            "background-color: black;"
        )

        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create controllers
        self.control_pad = ControlPad()
        self.rotation_pad = RotationPad()
        self.preset_controls = PresetControls()

        # Add controllers to layout
        layout.addWidget(
            self.control_pad,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.rotation_pad,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.preset_controls,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Status display
        self.status_label = QLabel()

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setStyleSheet("""
            QLabel {
                color: #D5DED6;
                background-color: #242424;
                border: 1px solid #9EAEA2;
                border-radius: 10px;
                font-size: 14px;
                padding: 10px;
            }
        """)

        layout.addWidget(self.status_label)

        # Connect GUI inputs to Command Manager
        self.control_pad.direction_changed.connect(
            self.command_manager.set_movement
        )

        self.rotation_pad.direction_changed.connect(
            self.command_manager.set_rotation
        )

        self.preset_controls.command_selected.connect(
            self.command_manager.set_preset
        )

        # Connect Command Manager to status display
        self.command_manager.state_changed.connect(
            self.update_status
        )

        # Display initial state
        self.update_status(
            self.command_manager.get_state()
        )

    def update_status(self, state):

        self.status_label.setText(
            f"Movement: {state['movement']}    |    "
            f"Rotation: {state['rotation']}    |    "
            f"Preset: {state['preset']}"
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = PyTongueGUI()
    window.show()

    sys.exit(app.exec())