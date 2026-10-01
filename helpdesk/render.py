"""Drawing. `compose()` paints the world into a 40x27 pixel framebuffer of
palette indices; `Renderer` blits that framebuffer to curses as two-column
blocks and writes the plain-text status line under it."""
import curses
import math

from .constants import (
    PW, PH, CELL_W, VIEW_COLS, VIEW_ROWS, PALETTE, FONT, C, RAINBOW,
    HUD_SCORE_X, HUD_LEVEL_X, METER_ROW, TICKET_ROW, COFFEE_BAR_X0, COFFEE_BAR_X1,
    WALL_TOP, WALL_BOT, WALL_L, WALL_R, FIX_PRESSES, FRUST_MAX, BOOST_TIME,
)


# ------------------------------------------------------------------ primitives
def px(fb, x, y, c):
    if 0 <= x < PW and 0 <= y < PH:
        fb[y][x] = c


def rect(fb, x, y, w, h, c):
    for yy in range(max(0, y), min(PH, y + h)):
        row = fb[yy]
        for xx in range(max(0, x), min(PW, x + w)):
            row[xx] = c


def text(fb, x, y, s, color):
    """Draw block-font text. `color` is one index or a list of five, one per row."""
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT[" "])
        for r, line in enumerate(glyph):
            c = color[r % len(color)] if isinstance(color, list) else color
            for i, bit in enumerate(line):
                if bit == "#":
                    px(fb, x + i, y + r, c)
        x += 4


def text_width(s):
    return len(s) * 4 - 1


def centered(fb, y, s, color):
    text(fb, (PW - text_width(s)) // 2, y, s, color)


def blink(t, hz):
    return int(t * hz * 2) % 2 == 0


# ------------------------------------------------------------------ scenes
def compose(world):
    fb = [[C.BLACK] * PW for _ in range(PH)]
    if world.state == "TITLE":
        draw_title(fb, world)
        return fb
    draw_hud(fb, world)
    draw_field(fb, world)
    if world.state == "OVER":
        draw_over(fb, world)
    elif world.asking_quit:
        overlay(fb, world, "QUIT? Y/N", C.WHITE)
    elif world.paused:
        overlay(fb, world, "PAUSED", C.WHITE)
    return fb


def draw_title(fb, world):
    t = world.t
    shift = int(t * 6)
    rainbow = [RAINBOW[(i + shift) % len(RAINBOW)] for i in range(5)]
    rainbow2 = [RAINBOW[(i + shift + 2) % len(RAINBOW)] for i in range(5)]
    text(fb, 2, 2, "HELP DESK", rainbow)
    centered(fb, 8, "HERO", rainbow2)
    draw_player_sprite(fb, 4, 9, boost=False, working=blink(t, 1), step=int(t * 4), t=t)
    # a coffee cup beside the title
    px(fb, 33, 10, C.CUP if blink(t, 2) else C.CUP2)
    rect(fb, 32, 11, 3, 1, C.MACHINE)
    centered(fb, 15, "HI %06d" % world.hiscore, C.SCORE)
    if blink(t, 1):
        centered(fb, 21, "PUSH SPACE", C.WHITE)


def draw_hud(fb, world):
    t = world.t
    text(fb, HUD_SCORE_X, 0, "%06d" % world.score, C.SCORE)
    text(fb, HUD_LEVEL_X, 0, "L%02d" % min(world.level, 99), C.LEVEL)

    # frustration meter
    for x in range(PW):
        fb[METER_ROW][x] = C.METER_BG
    fill = int(round(world.frust / FRUST_MAX * PW))
    if world.frust < 50:
        col = C.METER_G
    elif world.frust < 80:
        col = C.METER_Y
    else:
        col = C.METER_R if blink(t, 3) else C.WHITE
    for x in range(min(PW, fill)):
        fb[METER_ROW][x] = col

    # open tickets, one red block each
    for i, s in enumerate(world.open_tickets[:9]):
        c = C.TICKET if (s.age < 20 or blink(t, 4)) else C.BLACK
        px(fb, 1 + 2 * i, TICKET_ROW, c)

    # coffee bar
    width = COFFEE_BAR_X1 - COFFEE_BAR_X0 + 1
    p = world.player
    if p.boost > 0:
        n = int(math.ceil(p.boost / BOOST_TIME * width))
        rect(fb, COFFEE_BAR_X1 - n + 1, TICKET_ROW, n, 1, C.COFFEE_BAR)
    elif world.coffee.cup:
        px(fb, COFFEE_BAR_X1, TICKET_ROW, C.CUP if blink(t, 2) else C.CUP2)


def wall_color(world):
    if world.frust < 50:
        return C.WALL
    if world.frust < 80:
        return C.WALL_WARN
    return C.WALL_DANGER if blink(world.t, 2) else C.WALL_WARN


def draw_field(fb, world):
    t = world.t
    wc = wall_color(world)
    rect(fb, 0, WALL_TOP, PW, 1, wc)
    rect(fb, 0, WALL_BOT, PW, 1, wc)
    rect(fb, WALL_L, WALL_TOP, 1, WALL_BOT - WALL_TOP + 1, wc)
    rect(fb, WALL_R, WALL_TOP, 1, WALL_BOT - WALL_TOP + 1, wc)

    for s in world.stations:
        if s.kind == "DESK":
            draw_desk(fb, s, t)
        elif s.kind == "PRINTER":
            draw_printer(fb, s, t)
        else:
            draw_coffee(fb, s, t)
    for s in world.stations:
        if s.issue:
            draw_alert(fb, s, t)

    p = world.player
    draw_player_sprite(fb, p.x, p.y, p.boost > 0, p.working > 0, p.step, t)


def draw_desk(fb, s, t):
    x, y = s.x, s.y
    rect(fb, x, y + 2, s.w, 1, C.DESK)
    screen = C.SCREEN_OK
    if s.issue == "CRASH":
        screen = C.SCREEN_BAD if blink(t, 4) else C.SCREEN_BAD2
    elif s.flash > 0 and blink(t, 8):
        screen = C.WHITE
    rect(fb, x + 1, y, 2, 1, screen)
    rect(fb, x + 1, y + 1, 2, 1, C.MON)
    head = C.SKIN
    if s.issue and s.age > 8 and blink(t, 3):
        head = C.ANGRY
    elif s.issue == "PASSWORD" and blink(t, 2):
        head = C.ANGRY
    px(fb, x + 4, y, head)
    rect(fb, x + 4, y + 1, 2, 1, s.shirt)


def draw_printer(fb, s, t):
    x, y = s.x, s.y
    rect(fb, x, y + 1, 3, 2, C.PRINTER)
    if s.issue:
        paper = C.JAM if blink(t, 4) else C.JAM2
        px(fb, x + 1, y, paper)
        px(fb, x + 1, y + 1, C.JAM)
        px(fb, x + 1, y + 2, C.BLACK)
    else:
        px(fb, x + 1, y, C.WHITE if (s.flash > 0 and blink(t, 8)) else C.PAPER)
        px(fb, x + 1, y + 1, C.PAPER)


def draw_coffee(fb, s, t):
    x, y = s.x, s.y
    rect(fb, x, y, 3, 3, C.MACHINE)
    if s.cup:
        px(fb, x + 1, y + 1, C.CUP if blink(t, 2) else C.CUP2)
    else:
        px(fb, x + 1, y + 1, C.BLACK)


def draw_alert(fb, s, t):
    """Attention marker above a ticket; turns into a progress bar once work starts."""
    ax = s.x + 4 if s.kind == "DESK" else s.x + 1
    ay = s.y - 1
    if s.progress > 0:
        need = FIX_PRESSES[s.issue]
        n = min(3, 1 + (s.progress * 3) // need)
        rect(fb, ax - 1, ay, n, 1, C.PROGRESS)
    else:
        hz = 2 if s.age < 10 else 5
        if blink(t, hz):
            px(fb, ax, ay, C.ALERT if s.age < 20 else C.ALERT2)


def draw_player_sprite(fb, x, y, boost, working, step, t):
    shirt = C.HERO_SHIRT
    if boost:
        shirt = C.HERO_BOOST if blink(t, 6) else C.WHITE
    px(fb, x + 1, y, C.SKIN)
    rect(fb, x, y + 1, 3, 1, shirt)
    if working:
        px(fb, x, y, C.SKIN)
        px(fb, x + 2, y, C.SKIN)
    if step % 2 == 0:
        px(fb, x, y + 2, C.HERO_PANTS)
        px(fb, x + 2, y + 2, C.HERO_PANTS)
    else:
        px(fb, x + 1, y + 2, C.HERO_PANTS)


def overlay(fb, world, msg, color):
    rect(fb, 0, 13, PW, 7, C.BLACK)
    centered(fb, 14, msg, color)


def draw_over(fb, world):
    t = world.t
    rect(fb, 0, 10, PW, 7, C.BLACK)
    centered(fb, 11, "GAME OVER", C.METER_R if blink(t, 2) else C.WHITE)
    rect(fb, 0, 18, PW, 7, C.BLACK)
    if world.over_timer > 1.0 and blink(t, 1):
        centered(fb, 19, "PUSH SPACE", C.WHITE)


# ------------------------------------------------------------------ status line
def status_text(world):
    if world.state == "TITLE":
        return "SPACE  START        Q  QUIT"
    if world.state == "OVER":
        return "SHIFT OVER: %d TICKETS CLOSED      SPACE  CONTINUE" % world.fixes
    if world.asking_quit:
        return "QUIT THE SHIFT?   Y  YES      ANY OTHER KEY  KEEP WORKING"
    if world.paused:
        return "PAUSED      P  RESUME"
    base = "ARROWS/WASD MOVE   SPACE FIX   P PAUSE   Q QUIT"
    if world.coffee_in_reach():
        return base + "    >> SPACE: GRAB COFFEE"
    s = world.target()
    if s is not None:
        from .constants import TICKET_NAMES
        return base + "    >> MASH SPACE: " + TICKET_NAMES[s.issue]
    return base


# ------------------------------------------------------------------ curses blit
class Renderer:
    def __init__(self, stdscr):
        self.scr = stdscr
        self.colors_ok = curses.has_colors()
        self.attrs = []
        if self.colors_ok:
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass
            self.attrs = self._build_pairs()
        self.last_size = None

    def _build_pairs(self):
        many = curses.COLORS >= 256
        pair_for_color = {}
        attrs = []
        for _name, full, basic in PALETTE:
            col = full if many else basic
            if col not in pair_for_color:
                n = len(pair_for_color) + 1
                if n < curses.COLOR_PAIRS:
                    try:
                        curses.init_pair(n, col, col)
                        pair_for_color[col] = n
                    except curses.error:
                        pair_for_color[col] = 0
                else:
                    pair_for_color[col] = 0
            attrs.append(curses.color_pair(pair_for_color[col]))
        return attrs

    def put(self, y, x, s, attr=0):
        try:
            self.scr.addstr(y, x, s, attr)
        except curses.error:
            pass

    def blit(self, fb, status):
        rows, cols = self.scr.getmaxyx()
        if (rows, cols) != self.last_size:
            self.scr.erase()
            self.last_size = (rows, cols)
        if rows < VIEW_ROWS or cols < VIEW_COLS:
            msg = "HELP DESK HERO needs %dx%d, terminal is %dx%d" % (VIEW_COLS, VIEW_ROWS, cols, rows)
            self.put(max(0, rows // 2), max(0, (cols - len(msg)) // 2), msg[: max(0, cols - 1)])
            self.scr.refresh()
            return
        oy = (rows - VIEW_ROWS) // 2
        ox = (cols - VIEW_COLS) // 2
        for y, row in enumerate(fb):
            x = 0
            while x < PW:
                c = row[x]
                x2 = x + 1
                while x2 < PW and row[x2] == c:
                    x2 += 1
                n = x2 - x
                if self.colors_ok:
                    self.put(oy + y, ox + x * CELL_W, " " * (n * CELL_W), self.attrs[c])
                else:
                    glyph = "  " if c == C.BLACK else "█" * CELL_W
                    self.put(oy + y, ox + x * CELL_W, glyph * n)
                x = x2
        line = status[:VIEW_COLS].center(VIEW_COLS)
        self.put(oy + PH, ox, line, curses.A_DIM)
        self.scr.refresh()
