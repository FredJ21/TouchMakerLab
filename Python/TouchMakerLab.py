#!/usr/bin/env python3
''' 
-------------------------------------------------------------------------------

                        TOUCH MAKER LAB  -  Gpio Test

Touch Maker Lab est une carte d’extension pour Raspberry PI, 
pensée par des makers pour des makers, conçue pour faciliter la connexion et 
la programmation des entrées/sorties. 
Elle permet d’interagir avec le système grâce à ses 6 pads tactiles et de 
relier de 6 à 12 GPIO en quelques secondes grâce à ses 6 connecteurs jack.
Fini la prise de tête avec le câblage — 
concentrez-vous sur le code, que ce soit sur Scratch ou en Python. 

by SLmediation & F-ROBOTICS.FR                                        mai 2026             

-------------------------------------------------------------------------------

Copyright © 2026 [SLmediation & F-ROBOTICS.FR]. Tous droits réservés.

Le matériel, le logiciel et la documentation constituant ce projet sont la propriété
exclusive de [SLmediation & F-ROBOTICS.FR] et sont protégés par le droit de la propriété intellectuelle.
Toute reproduction, fabrication ou distribution, partielle ou totale, est strictement
interdite sans autorisation écrite préalable.
Contacts : 
👉 https://www.instagram.com/slmediation
👉 https://www.instagram.com/fredrobotic

-------------------------------------------------------------------------------
'''

import curses
import time
from collections import deque
from datetime import datetime

# ── Import RPi.GPIO ────────────────────────────────────────────────────────
try:
    import RPi.GPIO as GPIO
    ON_PI = True
except ImportError:
    ON_PI = False

GPIOS = [16, 17, 18, 19, 20, 21]

# ═══════════════════════════════════════════════════════════════════════════
# COORDONNÉES
# R(n) = ligne curses absolue  |  C(n) = colonne curses absolue
# ═══════════════════════════════════════════════════════════════════════════

BOARD_COL = 2   # col du '║' gauche
BOARD_ROW = 2   # row du '╔'

def R(row): return BOARD_ROW + row
def C(col): return BOARD_COL + 1 + col   # +1 : dépasse le '║'

# ── Jacks ── col interne du '┌', ordre GPIO 16..21
JACK_COLS = [5, 16, 27, 38, 49, 60]

# ── Pads ── (row, col interne) du '╭', ordre GPIO 16..21
PAD_ORIGINS = [
    (12,  4),   # GPIO16 – gauche
    ( 9, 16),   # GPIO17 – milieu haut
    (16, 18),   # GPIO18 – milieu bas
    (12, 30),   # GPIO19 – centre
    ( 9, 46),   # GPIO20 – droite haut
    (16, 48),   # GPIO21 – droite bas
]
PAD_INNER_H = 3

# ── Connecteur 40 broches ── pin1=haut droite, pin40=bas gauche
_GPIO40_COLS = list(range(13, 52, 2))   # 20 cols : 13..51

def _pin_pos(pin):
    col_idx = 20 - (pin + 1) // 2
    row_i   = (pin - 1) % 2
    return row_i, _GPIO40_COLS[col_idx]

_GPIO_TO_PIN = {16: 36, 17: 11, 18: 12, 19: 35, 20: 38, 21: 40}
GPIO_PIN_POS = {gpio: _pin_pos(pin) for gpio, pin in _GPIO_TO_PIN.items()}

# ── Labels GPIO latéral ──
GPIO_LABEL_COL = 60
GPIO_LABELS = {
    10: ("[15]TX  ", "uart"),  11: ("[14]RX  ", "uart"),
    12: ("[11]CLK ", "spi"),   13: ("[10]MOSI", "spi"),
    14: ("[ 9]MISO", "spi"),   15: ("[ 8]CE0 ", "spi"),
    16: ("[ 7]CE1 ", "spi"),   17: ("[ 3]SDA ", "i2c"),
    18: ("[ 2]SCL ", "i2c"),   19: ("[5V]PWR ", "pwr"),
    20: ("[GN]GND ", "gnd"),
}

# ── Zone log ── 5 lignes sous la carte (rows 29..33)
LOG_ROW_START = 29
LOG_LINES     = 5

# ═══════════════════════════════════════════════════════════════════════════
# COULEURS
# ═══════════════════════════════════════════════════════════════════════════
CP_BORDER  = 1; CP_DEFAULT = 2; CP_ON    = 3; CP_GRAY  = 4
CP_UART    = 5; CP_SPI     = 6; CP_I2C   = 7
CP_PIN_OFF = 8; CP_PIN_ON  = 9; CP_TITLE = 10
CP_LOG_LOW = 11; CP_LOG_HIGH = 12   # couleurs des entrées de log

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(CP_BORDER,   curses.COLOR_MAGENTA, -1)
    curses.init_pair(CP_DEFAULT,  curses.COLOR_WHITE,   -1)
    curses.init_pair(CP_ON,       curses.COLOR_GREEN,   -1)
    curses.init_pair(CP_GRAY,     curses.COLOR_BLACK,   -1)
    curses.init_pair(CP_UART,     curses.COLOR_CYAN,    -1)
    curses.init_pair(CP_SPI,      curses.COLOR_YELLOW,  -1)
    curses.init_pair(CP_I2C,      curses.COLOR_GREEN,   -1)
    curses.init_pair(CP_PIN_OFF,  curses.COLOR_YELLOW,  -1)
    curses.init_pair(CP_PIN_ON,   curses.COLOR_GREEN,   -1)
    curses.init_pair(CP_TITLE,    curses.COLOR_WHITE,   -1)
    curses.init_pair(CP_LOG_LOW,  curses.COLOR_GREEN,   -1)   # LOW  = actif = vert
    curses.init_pair(CP_LOG_HIGH, curses.COLOR_YELLOW,  -1)   # HIGH = repos = gris

def A(pair, bold=False):
    a = curses.color_pair(pair)
    return a | curses.A_BOLD if bold else a

# ═══════════════════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════════════════

def put(win, row, col, text, attr=0):
    h, w = win.getmaxyx()
    if row < 0 or row >= h or col < 0 or col >= w:
        return
    if col + len(text) > w:
        text = text[:w - col]
    try:
        win.addstr(row, col, text, attr)
    except curses.error:
        pass

# ═══════════════════════════════════════════════════════════════════════════
# DESSIN STATIQUE
# ═══════════════════════════════════════════════════════════════════════════

# Toutes les lignes font exactement 68 chars (contenu entre les deux ║)
_PAD_ZONE = {
     7: "                                                                    ",
     8: "                                                                    ",
     9: "                ╭────╮                        ╭────╮                ",
    10: "                │    │                        │    │                ",
    11: "                │    │                        │    │                ",
    12: "    ╭────╮      ╰────╯        ╭────╮          ╰────╯                ",
    13: "    │    │                    │    │                                ",
    14: "    │    │                    │    │                                ",
    15: "    │    │                    │    │                                ",
    16: "    ╰────╯        ╭────╮      ╰────╯            ╭────╮              ",
    17: "                  │    │                        │    │              ",
    18: "                  │    │                        │    │              ",
    19: "                  │    │                        │    │              ",
    20: "                  ╰────╯                        ╰────╯              ",
    21: "                                                                    ",
    22: "                         TOUCH MAKER LAB                            ",
    23: "     SLmediation            V. 202605             F-ROBOTICS.FR     ",
}

def draw_static(win):
    ba = A(CP_BORDER)
    da = A(CP_DEFAULT)

    # Bordures horizontales
    put(win, R(0),  C(-1), "╔" + "═"*68 + "╗", ba)
    put(win, R(6),  C(-1), "╠" + "═"*68 + "╣", ba)
    put(win, R(24), C(-1), "╠" + "═"*68 + "╣", ba)
    put(win, R(27), C(-1), "╚" + "═"*68 + "╝", ba)

    # ║ latéraux — APRÈS le contenu pour ne pas être écrasés
    # (dessinés en dernier dans cette fonction)
    content_rows = list(range(1, 6)) + list(range(7, 24)) + [25, 26]

    # Jacks OFF
    for col in JACK_COLS:
        put(win, R(1), C(col),   "┌─┐", da)
        put(win, R(2), C(col),   "│ │", da)
        put(win, R(3), C(col),   "└┬┘", da)
        put(win, R(4), C(col+1), "│",   da)

    # Labels 16-21
    for i, lc in enumerate([6, 17, 28, 39, 50, 61]):
        put(win, R(5), C(lc), str(16 + i), da)

    # Zone pads
    grp_color = {"uart": CP_UART, "spi": CP_SPI, "i2c": CP_I2C,
                 "pwr": CP_SPI, "gnd": CP_GRAY}
    for br, line in _PAD_ZONE.items():
        put(win, R(br), C(0), line[:68], da)   # garantit 68 chars max
        if br == 22:
            put(win, R(br), C(25), "TOUCH MAKER LAB", A(CP_TITLE, bold=True))
        if br in GPIO_LABELS:
            lbl, grp = GPIO_LABELS[br]
            put(win, R(br), C(GPIO_LABEL_COL), lbl, A(grp_color[grp]))

    # GPIO 40p OFF
    for row_i in range(2):
        put(win, R(25 + row_i), C(0), " " * 68, da)
        for col_int in _GPIO40_COLS:
            put(win, R(25 + row_i), C(col_int), "▣", A(CP_PIN_OFF))

    # ║ latéraux — dessinés EN DERNIER pour ne jamais être écrasés
    for row in content_rows:
        put(win, R(row), BOARD_COL,      "║", ba)
        put(win, R(row), BOARD_COL + 69, "║", ba)

    # En-tête zone log
    put(win, R(28), 0,
        "  ── Journal des événements " + "─"*44,
        A(CP_GRAY))

    # Aide
    hint = ("  [SIM] Touches 1-6 = GPIO16-21  |  Ctrl+C = quitter"
            if not ON_PI else "  Ctrl+C pour quitter")
    put(win, R(LOG_ROW_START + LOG_LINES + 1), 0, hint, A(CP_GRAY))

# ═══════════════════════════════════════════════════════════════════════════
# MISES À JOUR DYNAMIQUES – carte
# ═══════════════════════════════════════════════════════════════════════════

def update_jack(win, idx, active):
    col = JACK_COLS[idx]
    if active:
        put(win, R(1), C(col),   "┌─┐", A(CP_ON, bold=True))
        put(win, R(2), C(col),   "│", A(CP_ON, bold=True))
        put(win, R(2), C(col+1), "●", A(CP_ON, bold=True))
        put(win, R(2), C(col+2), "│", A(CP_ON, bold=True))
        put(win, R(3), C(col),   "└┬┘", A(CP_ON, bold=True))
        put(win, R(4), C(col+1), "│",   A(CP_ON, bold=True))
    else:
        put(win, R(1), C(col),   "┌─┐", A(CP_DEFAULT))
        put(win, R(2), C(col),   "│ │", A(CP_DEFAULT))
        put(win, R(3), C(col),   "└┬┘", A(CP_DEFAULT))
        put(win, R(4), C(col+1), "│",   A(CP_DEFAULT))

def update_pad(win, idx, active):
    pr, pc = PAD_ORIGINS[idx]
    ab   = A(CP_ON, bold=True) if active else A(CP_DEFAULT)
    fill = "│●●●●│"             if active else "│    │"
    put(win, R(pr),                    C(pc), "╭────╮", ab)
    for i in range(PAD_INNER_H):
        put(win, R(pr + 1 + i),        C(pc), fill,     ab)
    put(win, R(pr + 1 + PAD_INNER_H), C(pc), "╰────╯", ab)

def update_pin40(win, gpio, active):
    row_i, col_int = GPIO_PIN_POS[gpio]
    if active:
        put(win, R(25 + row_i), C(col_int), "◆", A(CP_PIN_ON, bold=True))
    else:
        put(win, R(25 + row_i), C(col_int), "▣", A(CP_PIN_OFF))

def update_all(win, states):
    for i, gpio in enumerate(GPIOS):
        active = not states.get(gpio, True)   # LOW = actif
        update_jack(win, i, active)
        update_pad(win, i, active)
        update_pin40(win, gpio, active)

# ═══════════════════════════════════════════════════════════════════════════
# LOG DÉFILANT
# ═══════════════════════════════════════════════════════════════════════════

def draw_log(win, log):
    """Affiche les 5 dernières entrées du log (la plus récente en bas)."""
    entries = list(log)   # du plus ancien au plus récent
    for i in range(LOG_LINES):
        row = R(LOG_ROW_START + i)
        put(win, row, 0, " " * 72, 0)   # efface la ligne
        if i < len(entries):
            ts, msg, is_low = entries[i]
            line = f"  {ts}  {msg}"
            attr = A(CP_LOG_LOW, bold=True) if is_low else A(CP_LOG_HIGH)
            put(win, row, 0, line, attr)

def log_event(log, gpio, state_high):
    """Ajoute une entrée dans le buffer de log (deque de 5)."""
    pin  = _GPIO_TO_PIN[gpio]
    ts   = datetime.now().strftime("%H:%M:%S")
    lvl  = "Low " if not state_high else "High"
    msg  = f"GPIO {gpio:2d}  (pin {pin:2d})  -->  {lvl}"
    log.append((ts, msg, not state_high))   # is_low = not state_high

# ═══════════════════════════════════════════════════════════════════════════
# GPIO
# ═══════════════════════════════════════════════════════════════════════════

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for gpio in GPIOS:
        GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_gpio():
    return {gpio: bool(GPIO.input(gpio)) for gpio in GPIOS}

# ═══════════════════════════════════════════════════════════════════════════
# BOUCLE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════

def main(stdscr):
    init_colors()
    curses.curs_set(0)
    stdscr.nodelay(True)

    if ON_PI:
        setup_gpio()

    states      = {gpio: True for gpio in GPIOS}   # HIGH = repos
    prev_states = {}
    log = deque(maxlen=LOG_LINES)   # 5 entrées max, défilement auto

    draw_static(stdscr)
    update_all(stdscr, states)
    draw_log(stdscr, log)
    stdscr.refresh()

    try:
        while True:
            if ON_PI:
                new_states = read_gpio()
            else:
                new_states = dict(states)
                key = stdscr.getch()
                if key in (ord('q'), 3):
                    break
                if ord('1') <= key <= ord('6'):
                    gpio = GPIOS[key - ord('1')]
                    new_states[gpio] = not new_states[gpio]

            if new_states != prev_states:
                # Détecter les GPIO qui ont changé et les logger
                for gpio in GPIOS:
                    if new_states[gpio] != prev_states.get(gpio, True):
                        log_event(log, gpio, new_states[gpio])
                update_all(stdscr, new_states)
                draw_log(stdscr, log)
                stdscr.refresh()
                prev_states = dict(new_states)
                states = new_states

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        if ON_PI:
            GPIO.cleanup()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("TouchMakerLab – terminé.")
