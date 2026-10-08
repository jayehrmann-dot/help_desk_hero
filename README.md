# Help Desk Hero

You are the only IT tech in an office where everything breaks at once.
Monitors blue-screen, printers jam, and somebody has forgotten their password
again. Run between the desks and clear tickets before the frustration meter
fills. Atari 2600 looks, single-screen action, running inside your terminal.

<p align="center">
<img width="593" height="475" alt="help_desk_hero" src="https://github.com/user-attachments/assets/2e6458f2-f754-4a38-be0a-a1d70a9ae618" />
</p>

```bash
./play.sh
```

or `python3 -m helpdesk` from this folder. Add `--sound` for a terminal bell on
fixes, coffee and game over. Needs Python 3 (ships with macOS) and a terminal
at least 80 columns by 28 rows. A 256-colour terminal gives the full palette;
8-colour terminals still work. Each key press moves one pixel, so holding a key
leans on your OS key-repeat rate: a faster repeat setting makes you faster.

## The game

The screen is a 40x27 "pixel" picture, each pixel two terminal columns wide,
like the wide pixels of a real 2600. The top is the HUD: a six-digit score,
your level, the frustration meter and a row of red blocks for open tickets.
Below it is the office: six desks with workers, two printers against the right
wall and the coffee machine in the corner.

- **Tickets.** Every few seconds a new ticket opens somewhere. A yellow block
  blinks above whoever needs you. Three kinds:

  | Ticket | Where | Looks like | Presses | Points |
  | --- | --- | --- | --- | --- |
  | Blue screen | a desk | monitor flashing blue and white | 12 | 300 |
  | Paper jam | a printer | red paper flashing in the tray | 9 | 200 |
  | Password reset | a desk | worker's face flashing red | 6 | 100 |

  Stand next to the desk or printer and mash SPACE. The marker above it turns
  into a green progress bar. Fix a ticket within fifteen seconds of it opening
  for a speed bonus of ten points per second to spare.
- **Frustration.** Every open ticket feeds the meter, and the longer it waits
  the faster it feeds. After eight seconds the worker starts turning red; after
  twenty the marker turns red too. Each fix knocks the meter down a little, and
  with nothing open it drains on its own. The office walls go yellow at half
  and flash red near the top. When the meter fills, the shift is over.
- **Coffee.** The machine in the bottom-right corner brews a cup ten seconds
  into the shift and every fifteen seconds after you take one. A blinking cup
  appears in the machine and in the HUD. Walk up and press SPACE: for eight
  seconds you move two pixels per press and every fix press counts double. The
  brown bar at the top right is your caffeine.
- **Levels.** Every six fixes is a level. Tickets come faster and more can be
  open at once. There is no winning, only a higher score.

The high score is saved to `highscore.json` in this folder.

## Controls

| Key | Action |
| --- | --- |
| Arrows / WASD / HJKL | Move |
| Space / F / Z / X / Enter | Fix the ticket you are next to, or grab coffee |
| P | Pause |
| Q / Esc | Quit (asks first during a shift) |

The status line under the screen tells you what the station next to you
needs, so you never have to guess which key does what.

## Layout

```
helpdesk/
  constants.py   screen layout, desk positions, tuning, palette, block font
  entities.py    Station (desk / printer / coffee machine) and Player
  world.py       rules: movement, tickets, frustration, coffee, scoring (no curses)
  render.py      paints the pixel framebuffer and blits it to curses
  engine.py      game loop, key map, high score file
  __main__.py    entry point
highscore.json   created after your first game
```

Everything you would want to tune is at the top of `constants.py`: `FIX_PRESSES`
and `FIX_POINTS` per ticket type, the `SPAWN_*` pacing, the `FRUST_*` meter
rates and the coffee timings. `world.py` has no curses dependency, so you can
drive it from a script to test balance changes without playing.
