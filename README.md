# rehab_miniproject_rob5
Github for the Rehabilitation Robotics Rob5

# PyTongue Controller

## Installation

Clone the repository:

```bash
git clone https://github.com/Basken2901/rehab_miniproject_rob5.git
cd rehab_miniproject_rob5/PyTongue
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**Ubuntu:** If the Qt `xcb` platform plugin is missing, install:

```bash
sudo apt install libxcb-cursor0
```

## Running PyTongue

From the `PyTongue` directory, activate the virtual environment and launch the controller:

```bash
source .venv/bin/activate
python main.py
```

## Controls

- **Movement:** Drag the circular joystick to move forward, backward, left, or right.
- **Rotation:** Drag the horizontal joystick to rotate left or right.
- **Presets:** Click Previous or Next to change presets.

Releasing either joystick returns it to its neutral position (`STOP`).

The current commands are displayed in the GUI and printed to the terminal.