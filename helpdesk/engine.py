"""The curses game loop: keyboard, timing, sound cues and the high score file."""
import curses
import json
import os
import time

from .constants import FPS
from .render import Renderer, compose, status_text
from .world import World

HISCORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "highscore.json")

KEYS = {
    curses.KEY_UP: "UP", ord("w"): "UP", ord("W"): "UP", ord("k"): "UP",
    curses.KEY_DOWN: "DOWN", ord("s"): "DOWN", ord("S"): "DOWN", ord("j"): "DOWN",
    curses.KEY_LEFT: "LEFT", ord("a"): "LEFT", ord("A"): "LEFT", ord("h"): "LEFT",
    curses.KEY_RIGHT: "RIGHT", ord("d"): "RIGHT", ord("D"): "RIGHT", ord("l"): "RIGHT",
    ord(" "): "FIRE", ord("f"): "FIRE", ord("F"): "FIRE", ord("z"): "FIRE", ord("x"): "FIRE",
    10: "FIRE", 13: "FIRE", curses.KEY_ENTER: "FIRE",
    ord("p"): "PAUSE", ord("P"): "PAUSE",
    ord("q"): "QUIT", ord("Q"): "QUIT", 27: "QUIT",
    ord("y"): "YES", ord("Y"): "YES", ord("n"): "NO", ord("N"): "NO",
}

ARROWS = {ord("A"): curses.KEY_UP, ord("B"): curses.KEY_DOWN,
          ord("C"): curses.KEY_RIGHT, ord("D"): curses.KEY_LEFT}

BEEPS = {"fix", "coffee", "over"}


def load_hiscore():
    try:
        with open(HISCORE_PATH) as f:
            return int(json.load(f).get("high", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def save_hiscore(value):
    try:
        with open(HISCORE_PATH, "w") as f:
            json.dump({"high": int(value)}, f)
    except OSError:
        pass


class Game:
    def __init__(self, stdscr, sound=False):
        self.scr = stdscr
        self.sound = sound
        self.renderer = Renderer(stdscr)
        self.world = World(load_hiscore())

    def decode_escape(self):
        """Turn a raw ESC [ A style arrow sequence that curses did not translate
        into the matching KEY_* code. A lone ESC comes back unchanged."""
        k2 = self.scr.getch()
        if k2 in (ord("["), ord("O")):
            k3 = self.scr.getch()
            arrow = ARROWS.get(k3)
            if arrow is not None:
                return arrow
            if k3 != -1:
                curses.ungetch(k3)
            return 0
        if k2 != -1:
            curses.ungetch(k2)
        return 27

    def run(self):
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.scr.nodelay(True)
        self.scr.keypad(True)
        world = self.world
        last = time.monotonic()
        while True:
            now = time.monotonic()
            dt = min(now - last, 0.1)
            last = now

            while True:
                k = self.scr.getch()
                if k == -1:
                    break
                if k == curses.KEY_RESIZE:
                    self.renderer.last_size = None
                    continue
                if k == 27:
                    k = self.decode_escape()
                name = KEYS.get(k, "OTHER")
                if world.key(name) == "QUIT":
                    return world.hiscore

            world.update(dt)
            if "over" in world.events:
                save_hiscore(world.hiscore)
            if self.sound and any(e in BEEPS for e in world.events):
                curses.beep()
            world.events.clear()

            self.renderer.blit(compose(world), status_text(world))
            spent = time.monotonic() - now
            time.sleep(max(0.0, 1.0 / FPS - spent))
