import curses

from .cli import build_parser, create_app


def main() -> None:
    args = build_parser().parse_args()

    try:
        curses.wrapper(lambda stdscr: create_app(stdscr, args).run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
