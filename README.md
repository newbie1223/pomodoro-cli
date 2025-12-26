# pomo-tui

A terminal-based Pomodoro timer with a real-time ASCII digital clock.  
Designed for developers who want to stay focused without leaving the terminal.

---

## ✨ Features

- Real-time ASCII digital clock display
- Pomodoro workflow (WORK / BREAK cycles)
- Color-coded phases  
  - 🔴 WORK (Red)  
  - 🔵 BREAK (Blue)
- Keyboard control
  - `p` : pause / resume
- Sound notification on phase change
- Fully terminal-based (no GUI)

---

## 🚀 Installation

```bash
pip install pomo-tui
```

## 🎯 Usage

```bash
pomo
```

```bash
pomo --work 25 --break 5 --cycles 4
```

| Option     | Description              | Default |
| ---------- | ------------------------ | ------- |
| `--work`   | Work duration (minutes)  | 25      |
| `--break`  | Break duration (minutes) | 5       |
| `--cycles` | Number of cycles         | 4       |

| Key        | Action         |
| ---------- | -------------- |
| `p`        | Pause / Resume |
| `Ctrl + C` | Quit           |

## 🛠️ Development Setup

git clone https://github.com/newbie1223/pomodoro-cli.git
cd pomodoro-cli

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
