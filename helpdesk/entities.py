"""Things in the office: the tech, desks, printers and the coffee machine."""
from .constants import COFFEE_FIRST


class Station:
    """A fixed object the player can stand next to and interact with.

    kind is "DESK", "PRINTER" or "COFFEE". Desks and printers carry an
    open ticket in `issue` ("CRASH", "PASSWORD" or "JAM"); the coffee
    machine uses `cup` instead.
    """

    def __init__(self, kind, x, y, w, h, shirt=None):
        self.kind = kind
        self.x, self.y, self.w, self.h = x, y, w, h
        self.shirt = shirt
        self.issue = None
        self.age = 0.0          # seconds the ticket has been open
        self.progress = 0       # button presses applied so far
        self.flash = 0.0        # "just fixed" sparkle timer
        self.cup = False
        self.cup_timer = COFFEE_FIRST

    def blocks(self, px, py, pw, ph):
        """True when a rect at (px, py) of size pw x ph overlaps this station."""
        return (px < self.x + self.w and px + pw > self.x
                and py < self.y + self.h and py + ph > self.y)

    def touches(self, px, py, pw, ph):
        """True when the rect, grown by one pixel on every side, overlaps."""
        return self.blocks(px - 1, py - 1, pw + 2, ph + 2)


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.facing = 1
        self.step = 0           # increments per pixel moved, animates the legs
        self.boost = 0.0        # seconds of coffee left
        self.last_fire = -10.0  # world time of the last press that counted
        self.working = 0.0      # seconds left to show the arms-up pose
