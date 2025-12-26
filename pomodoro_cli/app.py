import curses
import time
import argparse
from enum import Enum, auto


# ======================
# Configuration
# ======================

FPS_ACTIVE = 1.0
FPS_PAUSED = 0.1

DIGIT_HEIGHT = 5
DIGIT_WIDTH = 8
DIGIT_GAP = 1


class Phase(Enum):
    WORK = auto()
    BREAK = auto()


COLOR_WORK = 1
COLOR_BREAK = 2
COLOR_PAUSED = 3


DIGITS = {
    "0": [
        " ██████ ",
        "██    ██",
        "██    ██",
        "██    ██",
        " ██████ ",
    ],
    "1": [
        "   ██   ",
        " ████   ",
        "   ██   ",
        "   ██   ",
        " ██████ ",
    ],
    "2": [
        " ██████ ",
        "      ██",
        " ██████ ",
        "██      ",
        " ██████ ",
    ],
    "3": [
        " ██████ ",
        "      ██",
        " ██████ ",
        "      ██",
        " ██████ ",
    ],
    "4": [
        "██    ██",
        "██    ██",
        " ██████ ",
        "      ██",
        "      ██",
    ],
    "5": [
        " ██████ ",
        "██      ",
        " ██████ ",
        "      ██",
        " ██████ ",
    ],
    "6": [
        " ██████ ",
        "██      ",
        " ██████ ",
        "██    ██",
        " ██████ ",
    ],
    "7": [
        " ██████ ",
        "      ██",
        "      ██",
        "      ██",
        "      ██",
    ],
    "8": [
        " ██████ ",
        "██    ██",
        " ██████ ",
        "██    ██",
        " ██████ ",
    ],
    "9": [
        " ██████ ",
        "██    ██",
        " ██████ ",
        "      ██",
        " ██████ ",
    ],
    ":": [
        "        ",
        "   ██   ",
        "        ",
        "   ██   ",
        "        ",
    ],
}


# ======================
# Pomodoro Application
# ======================

class PomodoroApp:
    def __init__(self, stdscr, work_min: int, break_min: int, cycles: int):
        self.stdscr = stdscr
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.cycles = cycles

        self.paused = False
        self.pause_started_at = 0.0

    # ---------- lifecycle ----------

    def run(self) -> None:
        self._init_curses()

        cycle = 0
        while self.cycles == 0 or cycle < self.cycles:
            self._run_phase(Phase.WORK, self.work_sec)
            self._run_phase(Phase.BREAK, self.break_sec)
            cycle += 1

    def _init_curses(self) -> None:
        curses.curs_set(0)
        self.stdscr.nodelay(True)

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_WORK, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_BREAK, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_PAUSED, curses.COLOR_YELLOW, -1)

    # ---------- phase control ----------

    def _run_phase(self, phase: Phase, duration: int) -> None:
        self._beep()

        end_time = time.time() + duration
        self.paused = False

        while True:
            self._handle_input(end_time)

            remaining = int(end_time - time.time())
            if remaining < 0:
                return

            self._draw(phase, remaining)

            time.sleep(FPS_PAUSED if self.paused else FPS_ACTIVE)

    # ---------- input ----------

    def _handle_input(self, end_time: float) -> None:
        key = self.stdscr.getch()
        if key == ord("p"):
            self._toggle_pause(end_time)

    def _toggle_pause(self, end_time: float) -> None:
        self.paused = not self.paused
        if self.paused:
            self.pause_started_at = time.time()
        else:
            pause_duration = time.time() - self.pause_started_at
            end_time += pause_duration

    # ---------- drawing ----------

    def _draw(self, phase: Phase, remaining: int) -> None:
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        time_str = self._format_time(remaining)
        color = self._current_color(phase)

        self._draw_time(
            time_str,
            y=h // 2 - DIGIT_HEIGHT,
            x=w // 2 - (len(time_str) * (DIGIT_WIDTH + DIGIT_GAP)) // 2,
            color=color,
        )

        status = "PAUSED" if self.paused else self._phase_label(phase)
        self._draw_status(status, h // 2 + 3, w, color)

        self.stdscr.addstr(h - 2, 2, "p: pause/resume | Ctrl+C: quit")
        self.stdscr.refresh()

    def _draw_time(self, time_str: str, y: int, x: int, color: int) -> None:
        self.stdscr.attron(curses.color_pair(color))
        for row in range(DIGIT_HEIGHT):
            col = x
            for ch in time_str:
                for c in DIGITS[ch][row]:
                    self.stdscr.addch(y + row, col, c)
                    col += 1
                col += DIGIT_GAP
        self.stdscr.attroff(curses.color_pair(color))

    def _draw_status(self, text: str, y: int, width: int, color: int) -> None:
        self.stdscr.attron(curses.color_pair(color))
        self.stdscr.addstr(y, width // 2 - len(text) // 2, text)
        self.stdscr.attroff(curses.color_pair(color))

    # ---------- helpers ----------

    @staticmethod
    def _format_time(sec: int) -> str:
        m, s = divmod(sec, 60)
        return f"{m:02}:{s:02}"

    @staticmethod
    def _phase_label(phase: Phase) -> str:
        return "WORK TIME" if phase == Phase.WORK else "BREAK TIME"

    def _current_color(self, phase: Phase) -> int:
        if self.paused:
            return COLOR_PAUSED
        return COLOR_WORK if phase == Phase.WORK else COLOR_BREAK

    @staticmethod
    def _beep() -> None:
        print("\a", end="", flush=True)


# ======================
# Entry Point
# ======================

def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Pomodoro Timer")
    parser.add_argument("--work", type=int, default=25)
    parser.add_argument("--break", dest="break_", type=int, default=5)
    parser.add_argument("--cycles", type=int, default=0)
    args = parser.parse_args()

    try:
        curses.wrapper(
            lambda stdscr: PomodoroApp(
                stdscr,
                args.work,
                args.break_,
                args.cycles,
            ).run()
        )
    except KeyboardInterrupt:
        pass