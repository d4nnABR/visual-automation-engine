# Visual Automation Engine 🤖

A modular Python-based visual automation engine that executes screen actions using coordinate mapping, image recognition, and robust error-handling logic.

---

## Features

- 🖱️ Click, type, hotkeys, and key sequences via coordinate mapping
- 🖼️ Image detection with `CLICK_WHEN_IMAGE` and `WAIT_FOR_IMAGE`
- 🔁 Error recovery with `ON_FAIL_GOTO`, `LABEL`, `GOTO`, and `RETRY`
- 📅 Automatic date clicking with `CLICK_NEXT_DATE`
- 🟡 Random yellow box detection with `CLICK_RANDOM_YELLOW`
- 📂 Dynamic base directory — configurable from the menu
- 🧩 Clean modular architecture across 7 modules

---

## Project Structure

```
visual-automation-engine/
├── main.py              # Entry point and menu
├── core.py              # Main orchestration class
├── acciones.py          # Action execution logic
├── vision.py            # Image/color detection
├── logger.py            # Logging and error screenshots
├── utils.py             # Helper functions
├── config.py            # Configuration and valid actions
├── automation_images/   # Reference images (add your own)
│   └── debug/           # Auto-generated logs and screenshots
└── example_automation.txt  # Example instruction file
```

---

## Requirements

```bash
pip install pyautogui keyboard pillow
```

---

## Usage

```bash
python main.py
```

### Menu Options
1. **Record new automation** — capture coordinates interactively
2. **Append to existing file** — add steps to an existing `.txt`
3. **Run automation** — execute a `.txt` instruction file
4. **Validate file** — check a `.txt` for errors before running
5. **Show stored images** — list reference images available
6. **Set base directory** — configure where `.txt` files and images are stored

---

## Instruction File Format

Each line follows this format:
```
ACTION,X,Y,DELAY,PAYLOAD
```

| Action | Description |
|---|---|
| `CLICK` | Click at coordinates |
| `TYPE` | Click and type text |
| `TYPE_RAW` | Type without clicking |
| `PRESS` | Press a single key |
| `HOTKEY` | Execute a key combination |
| `KEYEVENTS` | Replay a recorded key sequence |
| `CLICK_WHEN_IMAGE` | Click when image appears on screen |
| `WAIT_FOR_IMAGE` | Wait until image is detected |
| `CLICK_NEXT_DATE` | Click next available date in a calendar |
| `CLICK_RANDOM_YELLOW` | Click a random yellow box in a region |
| `LABEL` | Define a named jump point |
| `GOTO` | Jump to a label |
| `RETRY` | Set retry count for next action |
| `ON_FAIL_GOTO` | Jump to label if next action fails |

See `example_automation.txt` for a complete working example.

---

## Notes

- `automation_images/` — place your reference `.png` images here
- `debug/` — auto-generated logs and error screenshots (not versioned)
- `config_usuario.json` — stores your local base directory (not versioned)

---

## Author

[d4nnABR](https://github.com/d4nnABR)
