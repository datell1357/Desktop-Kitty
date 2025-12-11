# Desktop Kitty

A lightweight, cute desktop pet application for Windows.

## Requirements
- Windows 10 or 11
- Python 3.8+

## setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running
Run the following command in the terminal:
```bash
python main.py
```

## Features
- **Drag & Drop**: Click and hold to move the cat.
- **Interactions**: Double-click to trigger reactions.
- **Context Menu**: Right-click for options.
    - **Floating Mode**: Toggle gravity.
    - **Follow Mouse**: The cat will chase your cursor.
    - **Sleep**: Force the cat to sleep.
- **Custom Sprites**: Add your own PNG/GIF files to `assets/sprites/{state}/`.
    - Supported states: `idle`, `walk`, `sit`, `sleep`, `follow`, `drag`.

## Development
- `src/pet_entity.py`: Main logic and rendering.
- `src/state_machine.py`: AI Behavior.
- `src/sprite_manager.py`: Graphics handling.
