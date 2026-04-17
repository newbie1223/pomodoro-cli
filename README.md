# pomo-tui

A terminal-based Pomodoro timer with a real-time ASCII digital clock.
Designed for developers who want to stay focused without leaving the terminal.

---

## ✨ Features

- Real-time ASCII digital clock display
- Pomodoro workflow with WORK / BREAK cycles
- Color-coded phases
  - 🔴 WORK
  - 🔵 BREAK
  - 🟡 PAUSED
- Keyboard control
  - `p`: pause / resume
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

| Key        | Action         |
| ---------- | -------------- |
| `p`        | Pause / Resume |
| `Ctrl + C` | Quit           |

### Notes

- `--work` and `--break` must be positive integers
- `--cycles` must be a non-negative integer
- Very small terminals automatically fall back to compact text rendering

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

---

## 📦 Package Information

- Package name: `pomo-tui`
- CLI command: `pomo`
- Python requirement: `>=3.9`
