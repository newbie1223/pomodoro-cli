from unittest.mock import patch

from pomodoro_cli.app import PomodoroApp
from pomodoro_cli.cli import non_negative_int, positive_int
from pomodoro_cli.models import Phase, PhaseAction


class DummyScreen:
    def __init__(self, height: int = 24, width: int = 80):
        self.height = height
        self.width = width
        self.calls: list[tuple] = []

    def getmaxyx(self) -> tuple[int, int]:
        return self.height, self.width

    def addch(self, y: int, x: int, ch: str) -> None:
        self.calls.append(("addch", y, x, ch))

    def addstr(self, y: int, x: int, text: str) -> None:
        self.calls.append(("addstr", y, x, text))

    def attron(self, value: int) -> None:
        self.calls.append(("attron", value))

    def attroff(self, value: int) -> None:
        self.calls.append(("attroff", value))

    def clear(self) -> None:
        self.calls.append(("clear",))

    def refresh(self) -> None:
        self.calls.append(("refresh",))

    def nodelay(self, enabled: bool) -> None:
        self.calls.append(("nodelay", enabled))

    def timeout(self, value: int) -> None:
        self.calls.append(("timeout", value))

    def getch(self) -> int:
        return -1


def test_positive_int_accepts_positive_values() -> None:
    assert positive_int("25") == 25


def test_positive_int_rejects_zero() -> None:
    try:
        positive_int("0")
    except Exception:
        return

    assert False, "positive_int should reject zero"


def test_positive_int_rejects_negative_values() -> None:
    try:
        positive_int("-1")
    except Exception:
        return

    assert False, "positive_int should reject negative values"


def test_non_negative_int_accepts_zero() -> None:
    assert non_negative_int("0") == 0


def test_non_negative_int_rejects_negative_values() -> None:
    try:
        non_negative_int("-1")
    except Exception:
        return

    assert False, "non_negative_int should reject negative values"


def test_toggle_pause_extends_phase_end_time() -> None:
    app = PomodoroApp(DummyScreen(), work_min=25, break_min=5, cycles=1)
    app.phase_end_time = 100.0

    with patch("pomodoro_cli.app.time.time", side_effect=[10.0, 16.5]):
        app._toggle_pause()
        assert app.paused is True
        app._toggle_pause()

    assert app.paused is False
    assert app.phase_end_time == 106.5


def test_help_text_includes_bell_off_marker() -> None:
    app = PomodoroApp(DummyScreen(), work_min=25, break_min=5, cycles=1, bell_enabled=False)

    assert "bell off" in app._help_text()


def test_current_color_returns_paused_color_when_paused() -> None:
    app = PomodoroApp(DummyScreen(), work_min=25, break_min=5, cycles=1)
    app.paused = True

    assert app._current_color(Phase.WORK) == 3


def test_current_color_returns_phase_color_when_active() -> None:
    app = PomodoroApp(DummyScreen(), work_min=25, break_min=5, cycles=1)

    assert app._current_color(Phase.WORK) == 1
    assert app._current_color(Phase.BREAK) == 2


def test_safe_addstr_clips_text_to_screen_width() -> None:
    screen = DummyScreen(width=5)
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    app._safe_addstr(0, 2, "abcdef")

    assert ("addstr", 0, 2, "abc") in screen.calls


def test_safe_addstr_ignores_out_of_bounds_coordinates() -> None:
    screen = DummyScreen(height=3, width=3)
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    app._safe_addstr(5, 0, "abc")
    app._safe_addstr(0, 5, "abc")
    app._safe_addstr(-1, 0, "abc")

    assert not any(call[0] == "addstr" for call in screen.calls)


def test_safe_addch_ignores_out_of_bounds_coordinates() -> None:
    screen = DummyScreen(height=3, width=3)
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    app._safe_addch(10, 1, "x")
    app._safe_addch(1, 10, "x")
    app._safe_addch(-1, 1, "x")

    assert not any(call[0] == "addch" for call in screen.calls)


def test_draw_uses_plain_text_fallback_on_small_screen() -> None:
    screen = DummyScreen(height=6, width=10)
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    with patch("pomodoro_cli.app.curses.color_pair", return_value=1):
        app._draw(Phase.WORK, 90)

    assert ("addstr", 3, 3, "01:30") in screen.calls


def test_handle_input_can_advance_to_next_phase() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)
    screen.getch = lambda: ord("N")

    assert app._handle_input() == PhaseAction.NEXT


def test_handle_input_can_reset_session() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=3)
    app.paused = True
    app.phase_end_time = 999.0
    screen.getch = lambda: ord("R")

    assert app._handle_input() == PhaseAction.RESET_SESSION
    assert app.paused is False
    assert app.phase_end_time == 0.0


def test_help_text_mentions_tmux_when_enabled() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)
    app.is_tmux = True

    assert "tmux" in app._help_text()


def test_run_phase_exits_when_timer_reaches_zero() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    with (
        patch.object(app, "_notify_phase_change"),
        patch.object(app, "_handle_input", side_effect=[PhaseAction.CONTINUE, PhaseAction.CONTINUE]),
        patch.object(app, "_draw") as draw_mock,
        patch("pomodoro_cli.app.time.time", side_effect=[100.0, 100.0, 101.0]),
        patch("pomodoro_cli.app.time.sleep"),
    ):
        result = app._run_phase(Phase.WORK, 1)

    assert result == PhaseAction.CONTINUE
    draw_mock.assert_any_call(Phase.WORK, 1)
    draw_mock.assert_any_call(Phase.WORK, 0)


def test_run_phase_returns_next_action() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=1)

    with (
        patch.object(app, "_notify_phase_change"),
        patch.object(app, "_handle_input", return_value=PhaseAction.NEXT),
        patch.object(app, "_draw"),
    ):
        result = app._run_phase(Phase.WORK, 10)

    assert result == PhaseAction.NEXT


def test_show_completion_message_renders_summary() -> None:
    screen = DummyScreen()
    app = PomodoroApp(screen, work_min=25, break_min=5, cycles=2)
    app.current_cycle = 2

    app._show_completion_message()

    assert any(call[0] == "addstr" and "Session complete!" in call[3] for call in screen.calls)

