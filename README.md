# pomo-tui

A terminal-based Pomodoro timer with a real-time ASCII digital clock.
Designed for developers who want to stay focused without leaving the terminal.

---

## ✨ Features

- Real-time ASCII digital clock display
- Pomodoro workflow with WORK / BREAK cycles
- tmux-friendly terminal behavior
  - stable key polling
  - resize-aware redraw
  - compact help text for small panes
- Color-coded phases
  - 🔴 WORK
  - 🔵 BREAK
  - 🟡 PAUSED
- Keyboard control
  - `p`: pause / resume
  - `N`: skip to next phase
  - `R`: reset the whole session
  - `Ctrl + C`: quit
- Terminal bell notification on phase change
- Safe fallback rendering on small terminal windows
- Fully terminal-based with no GUI dependency

---

## 🚀 Installation

### pip

```bash
pip install pomo-tui
```

### pipx

```bash
pipx install pomo-tui
```

---

## 🎯 Usage

Start with the default Pomodoro flow:

```bash
pomo
```

Run a custom session:

```bash
pomo --work 25 --break 5 --cycles 4
```

Run continuously until interrupted:

```bash
pomo --cycles 0
```

| Option     | Description                                 | Default |
| ---------- | ------------------------------------------- | ------- |
| `--work`   | Work duration in minutes                    | `25`    |
| `--break`  | Break duration in minutes                   | `5`     |
| `--cycles` | Number of work/break cycles, `0` = infinite | `0`     |

### Keyboard controls

| Key        | Action                     |
| ---------- | -------------------------- |
| `p`        | Pause / Resume             |
| `N`        | Move immediately to next phase |
| `R`        | Reset the whole session    |
| `Ctrl + C` | Quit                       |

### Notes

- `--work` and `--break` must be positive integers
- `--cycles` must be a non-negative integer
- Very small terminals automatically fall back to compact text rendering
- In tmux, use the keys directly in the running app pane
- The status area shows the current cycle and adapts to pane resizing

---

## 🛠️ Development Setup

```bash
git clone https://github.com/newbie1223/pomodoro-cli.git
cd pomodoro-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[test]
pytest
```

If your environment does not support extras installation yet, use:

```bash
pip install -e .
pip install pytest
pytest
```

### Project structure

```text
pomodoro_cli/
├── __init__.py
├── __main__.py
├── app.py
├── cli.py
├── config.py
└── models.py
tests/
└── test_app.py
```

- `app.py`: application lifecycle and curses UI flow
- `cli.py`: argument parsing and app construction
- `config.py`: constants and ASCII digit definitions
- `models.py`: enums and session state models

---

## 📦 Package Information

- Package name: `pomo-tui`
- CLI command: `pomo`
- Version: `1.3.0`
- Python requirement: `>=3.9`
