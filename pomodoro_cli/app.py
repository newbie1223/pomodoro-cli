import argparse
import curses
import time
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
        self.phase_end_time = 0.0

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

        self.phase_end_time = time.time() + duration
        self.paused = False
        self.pause_started_at = 0.0

        while True:
            self._handle_input()

            remaining = max(0, int(self.phase_end_time - time.time()))
            self._draw(phase, remaining)

            if remaining == 0:
                return

            time.sleep(FPS_PAUSED if self.paused else FPS_ACTIVE)

    # ---------- input ----------

    def _handle_input(self) -> None:
        key = self.stdscr.getch()
        if key == ord("p"):
            self._toggle_pause()

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.pause_started_at = time.time()
            return

        pause_duration = time.time() - self.pause_started_at
        self.phase_end_time += pause_duration

    # ---------- drawing ----------

    def _draw(self, phase: Phase, remaining: int) -> None:
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        time_str = self._format_time(remaining)
        color = self._current_color(phase)

        time_width = len(time_str) * DIGIT_WIDTH + (len(time_str) - 1) * DIGIT_GAP
        time_y = max(0, h // 2 - DIGIT_HEIGHT)
        time_x = max(0, w // 2 - time_width // 2)

        if h >= DIGIT_HEIGHT + 3 and w >= time_width:
            self._draw_time(
                time_str,
                y=time_y,
                x=time_x,
                color=color,
            )
        else:
            self._safe_addstr(
                max(0, h // 2),
                max(0, w // 2 - len(time_str) // 2),
                time_str,
                color,
            )

        status = "PAUSED" if self.paused else self._phase_label(phase)
        self._draw_status(status, min(h - 3, time_y + DIGIT_HEIGHT + 1), w, color)
        self._safe_addstr(h - 2, 2, "p: pause/resume | Ctrl+C: quit")
        self.stdscr.refresh()

    def _draw_time(self, time_str: str, y: int, x: int, color: int) -> None:
        self.stdscr.attron(curses.color_pair(color))
        for row in range(DIGIT_HEIGHT):
            col = x
            for ch in time_str:
                for c in DIGITS[ch][row]:
                    self._safe_addch(y + row, col, c)
                    col += 1
                col += DIGIT_GAP
        self.stdscr.attroff(curses.color_pair(color))

    def _draw_status(self, text: str, y: int, width: int, color: int) -> None:
        x = max(0, width // 2 - len(text) // 2)
        self._safe_addstr(y, x, text, color)

    # ---------- helpers ----------

    def _safe_addch(self, y: int, x: int, ch: str) -> None:
        if y < 0 or x < 0:
            return

        height, width = self.stdscr.getmaxyx()
        if y >= height or x >= width:
            return

        try:
            self.stdscr.addch(y, x, ch)
        except curses.error:
            pass

    def _safe_addstr(self, y: int, x: int, text: str, color: int | None = None) -> None:
        if y < 0 or x < 0 or not text:
            return

        height, width = self.stdscr.getmaxyx()
        if y >= height or x >= width:
            return

        clipped_text = text[: max(0, width - x)]
        if not clipped_text:
            return

        try:
            if color is not None:
                self.stdscr.attron(curses.color_pair(color))
            self.stdscr.addstr(y, x, clipped_text)
        except curses.error:
            pass
        finally:
            if color is not None:
                self.stdscr.attroff(curses.color_pair(color))

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

def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or a positive integer")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Pomodoro Timer")
    parser.add_argument("--work", type=positive_int, default=25)
    parser.add_argument("--break", dest="break_", type=positive_int, default=5)
    parser.add_argument(
        "--cycles",
        type=non_negative_int,
        default=0,
        help="Number of work/break cycles to run. Use 0 for infinite.",
    )
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