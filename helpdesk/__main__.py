"""Entry point: python3 -m helpdesk [--sound]"""
import curses
import locale
import os
import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "-h" in argv or "--help" in argv:
        print("usage: python3 -m helpdesk [--sound]\n\n  --sound   ring the terminal bell on fixes, coffee and game over")
        return 0
    sound = "--sound" in argv or "-s" in argv

    locale.setlocale(locale.LC_ALL, "")
    os.environ.setdefault("ESCDELAY", "25")
    if not os.environ.get("TERM"):
        os.environ["TERM"] = "xterm-256color"
    from .engine import Game

    def run(stdscr):
        return Game(stdscr, sound=sound).run()

    try:
        high = curses.wrapper(run)
    except KeyboardInterrupt:
        high = None
    if high:
        print("Shift's over. High score: %d. Have you tried turning it off and on again?" % high)
    else:
        print("Shift's over. Have you tried turning it off and on again?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
