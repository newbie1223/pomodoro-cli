import curses
import os
import time

from .config import (
    COLOR_BREAK,
    COLOR_PAUSED,
    COLOR_WORK,
    DIGITS,
    DIGIT_GAP,
    DIGIT_HEIGHT,
    DIGIT_WIDTH,
    FPS_ACTIVE,
    FPS_PAUSED,
    INPUT_POLL_TIMEOUT_MS,
)
from .models import Phase, PhaseAction, SessionStats


class PomodoroApp:
    def __init__(
        self,
        stdscr,
        work_min: int,
        break_min: int,
        cycles: int,
        bell_enabled: bool = True,
    ):
        self.stdscr = stdscr
        self.work_sec = work_min * 60
        self.break_sec = break_min * 60
        self.cycles = cycles
        self.bell_enabled = bell_enabled

        self.paused = False
        self.pause_started_at = 0.0
        self.phase_end_time = 0.0
        self.current_cycle = 0
        self.is_tmux = "TMUX" in os.environ

    # ---------- lifecycle ----------

    def run(self) -> None:
        self._init_curses()

        while True:
            self.current_cycle = 0
            self._run_session()

            if not self._wait_after_completion():
                return

    def _run_session(self) -> None:
        while self.cycles == 0 or self.current_cycle < self.cycles:
            work_action = self._run_phase(Phase.WORK, self.work_sec)
            if work_action == PhaseAction.RESET_SESSION:
                return

            break_action = self._run_phase(Phase.BREAK, self.break_sec)
            if break_action == PhaseAction.RESET_SESSION:
                return

            self.current_cycle += 1

        self._show_completion_message()

    def _wait_after_completion(self) -> bool:
        while True:
            action = self._handle_input()
            if action == PhaseAction.RESET_SESSION:
                self._reset_session()
                return True

    def _init_curses(self) -> None:
        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.timeout(INPUT_POLL_TIMEOUT_MS)
        curses.set_escdelay(25)

        if hasattr(curses, "start_color"):
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(COLOR_WORK, curses.COLOR_RED, -1)
            curses.init_pair(COLOR_BREAK, curses.COLOR_BLUE, -1)
            curses.init_pair(COLOR_PAUSED, curses.COLOR_YELLOW, -1)

    # ---------- phase control ----------

    def _run_phase(self, phase: Phase, duration: int) -> PhaseAction:
        self._notify_phase_change()
        self._start_phase(duration)

        while True:
            action = self._handle_input()
            if action != PhaseAction.CONTINUE:
                return action

            remaining = self._remaining_time()
            self._draw(phase, remaining)

            if remaining == 0:
                return PhaseAction.CONTINUE

            time.sleep(FPS_PAUSED if self.paused else FPS_ACTIVE)

    def _start_phase(self, duration: int) -> None:
        self.phase_end_time = time.time() + duration
        self.paused = False
        self.pause_started_at = 0.0

    def _remaining_time(self) -> int:
        return max(0, int(self.phase_end_time - time.time()))

    # ---------- input ----------

    def _handle_input(self) -> PhaseAction:
        while True:
            key = self.stdscr.getch()
            if key == -1:
                return PhaseAction.CONTINUE
            if key == curses.KEY_RESIZE:
                curses.update_lines_cols()
                continue
            if key == ord("p"):
                self._toggle_pause()
                continue
            if key == ord("N"):
                return PhaseAction.NEXT
            if key == ord("R"):
                self._reset_session()
                return PhaseAction.RESET_SESSION

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.pause_started_at = time.time()
            return

        pause_duration = time.time() - self.pause_started_at
        self.phase_end_time += pause_duration

    def _reset_session(self) -> None:
        self.paused = False
        self.pause_started_at = 0.0
        self.phase_end_time = 0.0

    # ---------- drawing ----------

    def _draw(self, phase: Phase, remaining: int) -> None:
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        time_str = self._format_time(remaining)
        color = self._current_color(phase)
        time_y = self._draw_timer(height, width, time_str, color)

        status = "PAUSED" if self.paused else self._phase_label(phase)
        status_y = min(height - 3, time_y + DIGIT_HEIGHT + 1)
        self._draw_status(status, status_y, width, color)

        self._draw_session_summary(width)
        self._safe_addstr(height - 2, 2, self._help_text())
        self.stdscr.refresh()

    def _draw_timer(self, height: int, width: int, time_str: str, color: int) -> int:
        time_width = len(time_str) * DIGIT_WIDTH + (len(time_str) - 1) * DIGIT_GAP
        time_y = max(0, height // 2 - DIGIT_HEIGHT)
        time_x = max(0, width // 2 - time_width // 2)

        if height >= DIGIT_HEIGHT + 3 and width >= time_width:
            self._draw_time(time_str, y=time_y, x=time_x, color=color)
        else:
            self._safe_addstr(
                max(0, height // 2),
                max(0, width // 2 - len(time_str) // 2),
                time_str,
                color,
            )

        return time_y

    def _draw_session_summary(self, width: int) -> None:
        stats = self._session_stats()
        left = f"cycle {stats.current_cycle_label}"
        center = f"done {stats.progress_percent}"
        right = f"remaining {stats.remaining_cycles_label}"

        self._safe_addstr(1, 2, left)
        self._safe_addstr(1, max(2, width // 2 - len(center) // 2), center)
        self._safe_addstr(1, max(2, width - len(right) - 2), right)

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

    def _show_completion_message(self) -> None:
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        stats = self._session_stats()
        lines = [
            "Session complete!",
            f"Completed cycles: {stats.completed_cycles}",
            "Press R to restart or Ctrl+C to quit.",
        ]

        start_y = max(0, height // 2 - len(lines) // 2)
        for index, line in enumerate(lines):
            x = max(0, width // 2 - len(line) // 2)
            self._safe_addstr(start_y + index, x, line)

        self.stdscr.refresh()

    # ---------- helpers ----------

    def _session_stats(self) -> SessionStats:
        return SessionStats(
            completed_cycles=self.current_cycle,
            total_cycles=self.cycles,
        )

    def _help_text(self) -> str:
        base = "p pause | N next | R reset | Ctrl+C quit"
        if not self.bell_enabled:
            base += " | bell off"
        if self.is_tmux:
            base += " | tmux: send keys directly"
        return base

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

    def _notify_phase_change(self) -> None:
        if self.bell_enabled:
            print("\a", end="", flush=True)
