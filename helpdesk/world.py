"""Game rules: movement, tickets, the frustration meter, coffee and scoring.

This module has no curses dependency so the game can be driven headlessly.
Input arrives as abstract key names: UP DOWN LEFT RIGHT FIRE PAUSE QUIT YES NO.
"""
import random

from .constants import (
    INT_X0, INT_X1, INT_Y0, INT_Y1, PLAYER_W, PLAYER_H, PLAYER_START,
    DESK_W, DESK_H, DESK_POSITIONS, PRINTER_POSITIONS, COFFEE_POSITION, SHIRTS,
    FIX_PRESSES, FIX_POINTS, SPEED_BONUS_WINDOW, SPEED_BONUS_PER_SEC, FIRE_INTERVAL,
    DESK_CRASH_CHANCE, SPAWN_FIRST, SPAWN_BASE, SPAWN_DECAY, SPAWN_MIN,
    FIXES_PER_LEVEL, MAX_OPEN_BASE, MAX_OPEN_CAP, FRUST_BASE, FRUST_AGE,
    FRUST_AGE_CAP, FRUST_RELIEF, FRUST_FIX, FRUST_MAX, COFFEE_REFILL,
    BOOST_TIME, BOOST_STEP, BOOST_FIX,
)
from .entities import Player, Station

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


class World:
    def __init__(self, hiscore=0, rng=None):
        self.rng = rng or random.Random()
        self.hiscore = hiscore
        self.state = "TITLE"      # TITLE, PLAYING, OVER
        self.t = 0.0              # world clock, drives blinking
        self.events = []          # sound cues for the frontend: fix, coffee, ticket, over
        self.paused = False
        self.asking_quit = False
        self.over_timer = 0.0
        self.reset()

    # ------------------------------------------------------------ setup
    def reset(self):
        self.score = 0
        self.fixes = 0
        self.frust = 0.0
        self.spawn_timer = SPAWN_FIRST
        self.player = Player(*PLAYER_START)
        self.stations = []
        for i, (x, y) in enumerate(DESK_POSITIONS):
            self.stations.append(Station("DESK", x, y, DESK_W, DESK_H, SHIRTS[i % len(SHIRTS)]))
        for x, y in PRINTER_POSITIONS:
            self.stations.append(Station("PRINTER", x, y, 3, 3))
        self.coffee = Station("COFFEE", COFFEE_POSITION[0], COFFEE_POSITION[1], 3, 3)
        self.stations.append(self.coffee)
        self.paused = False
        self.asking_quit = False
        self.over_timer = 0.0

    def start(self):
        self.reset()
        self.state = "PLAYING"

    # ------------------------------------------------------------ derived
    @property
    def level(self):
        return 1 + self.fixes // FIXES_PER_LEVEL

    @property
    def spawn_interval(self):
        return max(SPAWN_MIN, SPAWN_BASE * SPAWN_DECAY ** (self.level - 1))

    @property
    def max_open(self):
        return min(MAX_OPEN_BASE + (self.level - 1) // 2, MAX_OPEN_CAP)

    @property
    def open_tickets(self):
        return [s for s in self.stations if s.issue]

    def target(self):
        """The station with a ticket the player is standing next to, if any."""
        p = self.player
        for s in self.stations:
            if s.issue and s.touches(p.x, p.y, PLAYER_W, PLAYER_H):
                return s
        return None

    def coffee_in_reach(self):
        p = self.player
        return self.coffee.cup and self.coffee.touches(p.x, p.y, PLAYER_W, PLAYER_H)

    # ------------------------------------------------------------ input
    def key(self, name):
        """Handle one key press. Returns "QUIT" when the player confirms quitting.

        Unmapped keys arrive as "OTHER"; they only matter as a way to answer
        the quit prompt with "no".
        """
        if self.asking_quit:
            self.asking_quit = False
            if name in ("YES", "QUIT"):
                return "QUIT"
            return None
        if name == "QUIT":
            if self.state == "PLAYING":
                self.asking_quit = True
                return None
            return "QUIT"
        if self.state == "TITLE":
            if name == "FIRE":
                self.start()
        elif self.state == "OVER":
            if name == "FIRE" and self.over_timer > 1.0:
                self.state = "TITLE"
        elif self.state == "PLAYING":
            if name == "PAUSE":
                self.paused = not self.paused
            elif self.paused:
                return None
            elif name in DIRS:
                self.move(*DIRS[name])
            elif name == "FIRE":
                self.fire()
        return None

    def free(self, x, y):
        if x < INT_X0 or x + PLAYER_W - 1 > INT_X1:
            return False
        if y < INT_Y0 or y + PLAYER_H - 1 > INT_Y1:
            return False
        return not any(s.blocks(x, y, PLAYER_W, PLAYER_H) for s in self.stations)

    def move(self, dx, dy):
        p = self.player
        steps = BOOST_STEP if p.boost > 0 else 1
        for _ in range(steps):
            nx, ny = p.x + dx, p.y + dy
            if not self.free(nx, ny):
                break
            p.x, p.y = nx, ny
            p.step += 1
        if dx:
            p.facing = dx

    def fire(self):
        p = self.player
        if self.t - p.last_fire < FIRE_INTERVAL:
            return
        p.last_fire = self.t
        if self.coffee_in_reach():
            self.coffee.cup = False
            self.coffee.cup_timer = COFFEE_REFILL
            p.boost = BOOST_TIME
            self.events.append("coffee")
            return
        s = self.target()
        if s is None:
            return
        s.progress += BOOST_FIX if p.boost > 0 else 1
        p.working = 0.2
        if s.progress >= FIX_PRESSES[s.issue]:
            self.complete(s)

    def complete(self, s):
        bonus = int(max(0.0, SPEED_BONUS_WINDOW - s.age)) * SPEED_BONUS_PER_SEC
        self.score = min(self.score + FIX_POINTS[s.issue] + bonus, 999999)
        self.fixes += 1
        self.frust = max(0.0, self.frust - FRUST_FIX)
        s.issue = None
        s.progress = 0
        s.age = 0.0
        s.flash = 0.8
        self.events.append("fix")

    # ------------------------------------------------------------ simulation
    def update(self, dt):
        self.t += dt
        if self.state == "OVER":
            self.over_timer += dt
            return
        if self.state != "PLAYING" or self.paused or self.asking_quit:
            return

        p = self.player
        p.boost = max(0.0, p.boost - dt)
        p.working = max(0.0, p.working - dt)

        c = self.coffee
        if not c.cup:
            c.cup_timer -= dt
            if c.cup_timer <= 0:
                c.cup = True
                self.events.append("ding")

        rate = 0.0
        for s in self.stations:
            s.flash = max(0.0, s.flash - dt)
            if s.issue:
                s.age += dt
                rate += FRUST_BASE + FRUST_AGE * min(s.age, FRUST_AGE_CAP)
        if rate == 0.0:
            self.frust = max(0.0, self.frust - FRUST_RELIEF * dt)
        else:
            self.frust += rate * dt

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            if len(self.open_tickets) < self.max_open:
                self.spawn()

        if self.frust >= FRUST_MAX:
            self.frust = FRUST_MAX
            self.state = "OVER"
            self.over_timer = 0.0
            self.hiscore = max(self.hiscore, self.score)
            self.events.append("over")

    def spawn(self):
        candidates = [s for s in self.stations if s.kind != "COFFEE" and not s.issue]
        if not candidates:
            return
        s = self.rng.choice(candidates)
        if s.kind == "DESK":
            s.issue = "CRASH" if self.rng.random() < DESK_CRASH_CHANCE else "PASSWORD"
        else:
            s.issue = "JAM"
        s.age = 0.0
        s.progress = 0
        self.events.append("ticket")
