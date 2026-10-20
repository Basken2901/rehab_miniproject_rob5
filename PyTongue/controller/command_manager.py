from PySide6.QtCore import QObject, Signal


class CommandManager(QObject):

    # Signal emitted whenever the state changes
    state_changed = Signal(dict)

    def __init__(self):
        super().__init__()

        # Current controller states
        self.movement = "STOP"
        self.rotation = "STOP"
        self.preset = 0

        # Number of available presets
        self.max_presets = 5

    def set_movement(self, direction):

        valid_commands = [
            "FORWARD",
            "BACKWARD",
            "LEFT",
            "RIGHT",
            "STOP"
        ]

        if direction not in valid_commands:
            return

        if direction != self.movement:

            self.movement = direction
            self.update_state()

    def set_rotation(self, direction):

        valid_commands = [
            "ROTATE_LEFT",
            "ROTATE_RIGHT",
            "STOP"
        ]

        if direction not in valid_commands:
            return

        if direction != self.rotation:

            self.rotation = direction
            self.update_state()

    def set_preset(self, command):

        if command == "NEXT":

            self.preset = (
                self.preset + 1
            ) % self.max_presets

        elif command == "PREVIOUS":

            self.preset = (
                self.preset - 1
            ) % self.max_presets

        else:
            return

        self.update_state()

    def get_state(self):

        return {
            "movement": self.movement,
            "rotation": self.rotation,
            "preset": self.preset
        }

    def update_state(self):

        state = self.get_state()

        # Send updated state
        self.state_changed.emit(state)

        # Print for debugging
        print(
            f"Movement: {state['movement']} | "
            f"Rotation: {state['rotation']} | "
            f"Preset: {state['preset']}"
        )