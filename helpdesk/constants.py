"""Layout, tuning, palette and block font for Help Desk Hero.

The game draws into a 40x27 "pixel" framebuffer. Each pixel is two terminal
columns wide and one row tall, which gives the wide, chunky pixels of a real
Atari 2600 (160 pixels across a 4:3 screen).
"""

# ---------------------------------------------------------------- screen
PW = 40                   # pixel columns
PH = 27                   # pixel rows
CELL_W = 2                # terminal columns per pixel
VIEW_COLS = PW * CELL_W   # 80
VIEW_ROWS = PH + 1        # plus one plain-text status line = 28
FPS = 30

# HUD occupies pixel rows 0-6. The office is rows 7-26 with walls on the edge.
HUD_SCORE_X = 1
HUD_LEVEL_X = 28
METER_ROW = 5
TICKET_ROW = 6
COFFEE_BAR_X0, COFFEE_BAR_X1 = 21, 38

WALL_TOP, WALL_BOT = 7, 26
WALL_L, WALL_R = 0, 39
INT_X0, INT_X1 = 1, 38    # walkable interior, inclusive
INT_Y0, INT_Y1 = 8, 25

PLAYER_W = PLAYER_H = 3
PLAYER_START = (18, 15)

# Stations. Desks are 6x3 (monitor, worker, desktop). Printers and the
# coffee machine are 3x3 and sit against the right-hand wall.
DESK_W, DESK_H = 6, 3
DESK_POSITIONS = [(x, y) for y in (11, 20) for x in (1, 12, 23)]
PRINTER_POSITIONS = [(36, 8), (36, 15)]
COFFEE_POSITION = (36, 23)

# ---------------------------------------------------------------- tuning
# Button presses needed to clear each ticket type (coffee doubles each press).
FIX_PRESSES = {"CRASH": 12, "JAM": 9, "PASSWORD": 6}
FIX_POINTS = {"CRASH": 300, "JAM": 200, "PASSWORD": 100}
TICKET_NAMES = {"CRASH": "BLUE SCREEN", "JAM": "PAPER JAM", "PASSWORD": "PASSWORD RESET"}
SPEED_BONUS_WINDOW = 15.0     # seconds: fix faster than this for bonus points
SPEED_BONUS_PER_SEC = 10
FIRE_INTERVAL = 0.11          # presses closer together than this don't count
DESK_CRASH_CHANCE = 0.6       # otherwise a desk ticket is a password reset

SPAWN_FIRST = 1.5
SPAWN_BASE = 4.5              # seconds between tickets at level 1
SPAWN_DECAY = 0.88            # multiplied in per level
SPAWN_MIN = 1.5
FIXES_PER_LEVEL = 6
MAX_OPEN_BASE = 3             # open tickets allowed at level 1, +1 every 2 levels
MAX_OPEN_CAP = 7

FRUST_BASE = 0.9              # meter points per second per open ticket
FRUST_AGE = 0.05              # extra per second a ticket has been waiting
FRUST_AGE_CAP = 40.0
FRUST_RELIEF = 4.0            # per second with nothing open
FRUST_FIX = 6.0               # knocked off the meter per fix
FRUST_MAX = 100.0

COFFEE_FIRST = 10.0           # first cup brews this long after the shift starts
COFFEE_REFILL = 15.0
BOOST_TIME = 8.0
BOOST_STEP = 2                # pixels per key press while caffeinated
BOOST_FIX = 2                 # fix progress per press while caffeinated

# ---------------------------------------------------------------- palette
# (name, xterm-256 colour, 8-colour fallback)
PALETTE = [
    ("BLACK", 16, 0),
    ("WHITE", 231, 7),
    ("WALL", 244, 7),
    ("WALL_WARN", 220, 3),
    ("WALL_DANGER", 196, 1),
    ("DESK", 130, 3),
    ("MON", 250, 7),
    ("SCREEN_OK", 34, 2),
    ("SCREEN_BAD", 21, 4),
    ("SCREEN_BAD2", 231, 7),
    ("SKIN", 216, 3),
    ("ANGRY", 196, 1),
    ("SHIRT_R", 160, 1),
    ("SHIRT_G", 28, 2),
    ("SHIRT_P", 93, 5),
    ("SHIRT_T", 37, 6),
    ("SHIRT_O", 208, 3),
    ("SHIRT_K", 198, 5),
    ("PRINTER", 245, 7),
    ("PAPER", 231, 7),
    ("JAM", 196, 1),
    ("JAM2", 220, 3),
    ("MACHINE", 88, 1),
    ("CUP", 230, 7),
    ("CUP2", 130, 3),
    ("HERO_SHIRT", 39, 6),
    ("HERO_PANTS", 24, 4),
    ("HERO_BOOST", 226, 3),
    ("SCORE", 208, 3),
    ("LEVEL", 51, 6),
    ("METER_BG", 236, 0),
    ("METER_G", 46, 2),
    ("METER_Y", 226, 3),
    ("METER_R", 196, 1),
    ("COFFEE_BAR", 130, 3),
    ("ALERT", 226, 3),
    ("ALERT2", 196, 1),
    ("PROGRESS", 46, 2),
    ("TICKET", 196, 1),
    ("RB0", 196, 1),
    ("RB1", 208, 3),
    ("RB2", 226, 3),
    ("RB3", 46, 2),
    ("RB4", 51, 6),
]


class C:
    """Colour indices into PALETTE, e.g. C.DESK."""


for _i, (_name, _full, _basic) in enumerate(PALETTE):
    setattr(C, _name, _i)

SHIRTS = [C.SHIRT_R, C.SHIRT_G, C.SHIRT_P, C.SHIRT_T, C.SHIRT_O, C.SHIRT_K]
RAINBOW = [C.RB0, C.RB1, C.RB2, C.RB3, C.RB4]

# ---------------------------------------------------------------- font
# 3x5 block font. Characters are 4 pixels apart when drawn.
FONT = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "###", "#..", "###"],
    "F": ["###", "#..", "###", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "J": ["..#", "..#", "..#", "#.#", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#"],
    "N": ["##.", "#.#", "#.#", "#.#", "#.#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "P": ["###", "#.#", "###", "#..", "#.."],
    "Q": ["###", "#.#", "#.#", "###", "..#"],
    "R": ["###", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#.#", "#.#", "###", "###", "#.#"],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", "..#", "..#"],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    "?": ["###", "..#", ".##", "...", ".#."],
    "!": [".#.", ".#.", ".#.", "...", ".#."],
    ":": ["...", ".#.", "...", ".#.", "..."],
    "-": ["...", "...", "###", "...", "..."],
    ".": ["...", "...", "...", "...", ".#."],
    "/": ["..#", "..#", ".#.", "#..", "#.."],
    " ": ["...", "...", "...", "...", "..."],
}
