import argparse

from .app import PomodoroApp


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI Pomodoro Timer")
    parser.add_argument("--work", type=positive_int, default=25)
    parser.add_argument("--break", dest="break_", type=positive_int, default=5)
    parser.add_argument(
        "--cycles",
        type=non_negative_int,
        default=0,
        help="Number of work/break cycles to run. Use 0 for infinite.",
    )
    parser.add_argument(
        "--no-bell",
        action="store_true",
        help="Disable terminal bell notification on phase change.",
    )
    return parser


def create_app(stdscr, args: argparse.Namespace) -> PomodoroApp:
    return PomodoroApp(
        stdscr,
        args.work,
        args.break_,
        args.cycles,
        bell_enabled=not args.no_bell,
    )
