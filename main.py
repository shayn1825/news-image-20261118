#!/usr/bin/env python3
"""news-image-20261118 — Sum up Wednesday 18 November 2026 in one image.

A deterministic, stdlib-only renderer. It draws a newspaper front page
(1024x1024 PNG) with eight verified stories from 18 November 2026 and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

News verified 18 Nov 2026 (live web sources, same day):
 1. Gulf: US jets struck a Revolutionary Guard missile site on Qeshm
    Island; Iran fired drones at US bases in Bahrain and Kuwait.
    (Just Security Early Edition; Reuters via Zark News; OneTurn)
 2. Ukraine: Ukrainian drones and missiles partly collapsed the Kerch
    Bridge to Crimea, for a second day. (Horizon; OneTurn)
 3. China: Xi Jinping and Vladimir Putin met in Shenzhen, opened APEC
    talks and denounced protectionism/sanctions, ahead of a trilateral
    summit with Donald Trump. (Open Chronicle/AFP; Zark News)
 4. USA: Democrat Mary Peltola won Alaska's Senate seat over Dan
    Sullivan; Democrats hold 56 of 100 Senate seats. (AP via
    Open Chronicle; Zark News)
 5. Markets: Anthropic prices its IPO tonight, $70-$78 a share, 825m
    shares; trading as ANT on Nasdaq starts Thursday 19 Nov.
    (Invezz/SEC S-1; CNBC via Rebatly)
 6. Health: The US lost its measles elimination status, held since
    2000; 5,412 cases in 2026, 10 deaths. (PAHO via Zark News)
 7. Health: DR Congo Ebola outbreak passed 11,000 cases and 5,400
    deaths, more than doubling in three months. (UN via Zark/OneTurn)
 8. Space: Voyager 1 reached one light-day from Earth (about 16
    billion miles) at 5:16 a.m. ET. (NASA JPL via Zark News)

No network, no randomness, no timestamps: two runs write identical
bytes. Only the Python standard library is used (zlib, struct, os).
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (20, 20, 20)
RED = (178, 34, 24)
NAVY = (29, 78, 137)
TEAL = (0, 120, 113)
GOLD = (150, 105, 0)
GREEN = (46, 125, 50)
PURPLE = (90, 60, 140)
ORANGE = (198, 88, 0)
SLATE = (74, 84, 94)
LIGHT = (226, 219, 203)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one glyph = 7 rows of 5 pixels ('#' on, '.' off).
FONT = {
    'A': ("#####", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.set(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.set(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                elif abs(d2 - r * r) <= r:
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centre(self, y, s, scale, c):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, c)


# ---------------------------------------------------------------- icons
def draw_icon(cv, kind, x, y, c):
    """Small 44x44 pictogram inside the story cell, drawn in colour c."""
    if kind == "gulf":  # explosion + waves
        cx, cy = x + 22, y + 16
        for dx, dy in ((0, -12), (9, -9), (12, 0), (9, 9), (0, 12),
                       (-9, 9), (-12, 0), (-9, -9)):
            cv.line(cx, cy, cx + dx, cy + dy, c)
        cv.circle(cx, cy, 5, c, fill=True)
        for yy in (y + 34, y + 39):
            for xx in range(x + 4, x + 40, 8):
                cv.line(xx, yy, xx + 4, yy, c)
    elif kind == "bridge":  # bridge with a broken span
        cv.line(x + 2, y + 30, x + 18, y + 30, c)
        cv.line(x + 26, y + 30, x + 42, y + 30, c)
        cv.line(x + 6, y + 30, x + 6, y + 12, c)
        cv.line(x + 38, y + 30, x + 38, y + 12, c)
        cv.line(x + 6, y + 12, x + 22, y + 22, c)
        cv.line(x + 38, y + 12, x + 22, y + 22, c)
        cv.line(x + 18, y + 30, x + 18, y + 38, c)
        cv.line(x + 26, y + 30, x + 26, y + 38, c)
    elif kind == "summit":  # three leaders at a table
        for cx in (x + 10, x + 22, x + 34):
            cv.circle(cx, y + 12, 6, c, fill=True)
            cv.rect(cx - 6, y + 20, 12, 10, c)
        cv.line(x + 2, y + 32, x + 42, y + 32, c)
    elif kind == "ballot":  # ballot box + tick
        cv.rect(x + 8, y + 12, 28, 24, c)
        cv.rect(x + 16, y + 6, 12, 6, INK)
        cv.line(x + 12, y + 26, x + 18, y + 32, PAPER)
        cv.line(x + 18, y + 32, x + 32, y + 16, PAPER)
    elif kind == "ipo":  # rising chart
        cv.line(x + 6, y + 36, x + 6, y + 8, c)
        cv.line(x + 6, y + 36, x + 40, y + 36, c)
        cv.line(x + 8, y + 30, x + 18, y + 22, c)
        cv.line(x + 18, y + 22, x + 26, y + 26, c)
        cv.line(x + 26, y + 26, x + 38, y + 10, c)
        cv.line(x + 38, y + 10, x + 32, y + 10, c)
        cv.line(x + 38, y + 10, x + 38, y + 16, c)
    elif kind == "measles":  # virus: spiked circle
        cv.circle(x + 22, y + 22, 10, c, fill=True)
        for dx, dy in ((0, -16), (11, -11), (16, 0), (11, 11), (0, 16),
                       (-11, 11), (-16, 0), (-11, -11)):
            cv.line(x + 22, y + 22, x + 22 + dx, y + 22 + dy, c)
    elif kind == "ebola":  # medical cross + dots
        cv.rect(x + 18, y + 6, 8, 28, c)
        cv.rect(x + 8, y + 16, 28, 8, c)
        for dx, dy in ((4, 38), (14, 40), (30, 38), (40, 40)):
            cv.circle(x + dx, y + dy, 2, c, fill=True)
    elif kind == "voyager":  # probe + star trail
        cv.line(x + 8, y + 36, x + 34, y + 10, c)
        cv.line(x + 34, y + 10, x + 38, y + 18, c)
        cv.line(x + 34, y + 10, x + 26, y + 14, c)
        for dx, dy in ((6, 8), (14, 4), (20, 20)):
            cv.circle(x + dx, y + dy, 1, c, fill=True)
        cv.circle(x + 38, y + 6, 2, c, fill=True)


# ---------------------------------------------------------------- stories
# (kicker, colour, icon, headline, deck)
STORIES = [
    ("THE GULF", RED, "gulf",
     "US STRIKES IRAN, IRAN HITS BACK",
     "US jets hit a missile site on Qeshm Island. Iran fired drones "
     "at US bases in Bahrain and Kuwait."),
    ("UKRAINE", NAVY, "bridge",
     "KERCH BRIDGE HIT AGAIN",
     "Ukrainian drones and missiles partly collapsed the bridge to "
     "Crimea, for a second day in a row."),
    ("CHINA", TEAL, "summit",
     "XI AND PUTIN MEET IN SHENZHEN",
     "The two leaders opened APEC talks and denounced sanctions and "
     "protectionism before a summit with Trump."),
    ("UNITED STATES", GOLD, "ballot",
     "PELTOLA WINS ALASKA SENATE SEAT",
     "Democrat Mary Peltola beat Dan Sullivan. Democrats now hold "
     "56 of the 100 seats in the Senate."),
    ("MARKETS", GREEN, "ipo",
     "ANTHROPIC PRICES ITS IPO TONIGHT",
     "The Claude maker sets its share price at $70-$78. Trading as "
     "ANT on Nasdaq starts Thursday."),
    ("HEALTH", PURPLE, "measles",
     "US LOSES MEASLES-FREE STATUS",
     "After 26 years, measles has spread for over a year. 5,412 "
     "cases in 2026, and 10 deaths."),
    ("HEALTH", PURPLE, "ebola",
     "EBOLA IN CONGO PASSES 11,000 CASES",
     "The outbreak has doubled in three months, with over 5,400 "
     "deaths. The second-largest on record."),
    ("SPACE", ORANGE, "voyager",
     "VOYAGER 1 REACHES ONE LIGHT-DAY",
     "At 5:16 a.m. ET the probe passed 16 billion miles from Earth, "
     "a first for any human-made craft."),
]


def draw_story(cv, x, y, w, h, story):
    kicker, colour, icon, headline, deck = story
    cv.rect(x, y, 6, h, colour)
    cv.text(x + 16, y + 10, kicker, 2, colour)
    draw_icon(cv, icon, x + w - 56, y + 6, colour)
    head_w = w - 16 - 64
    lines = wrap(headline, head_w, 3)
    yy = y + 34
    for ln in lines[:2]:
        cv.text(x + 16, yy, ln, 3, INK)
        yy += 24
    # The embedded 5x7 font only defines capitals, digits and punctuation,
    # so decks are rendered in capitals (newspaper style) — lowercase
    # letters would otherwise render as blanks.
    deck_lines = wrap(deck.upper(), w - 32, 2)
    yy += 6
    for ln in deck_lines[:3]:
        cv.text(x + 16, yy, ln, 2, SLATE)
        yy += 17


def draw():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 10, RED)
    cv.text_centre(28, "THE WORLD TODAY", 7, INK)
    cv.hline(16, 92, W - 32, INK)
    cv.rect(0, 100, W, 52, RED)
    cv.text_centre(112, "WEDNESDAY  -  18 NOVEMBER 2026", 4, PAPER)
    cv.text_centre(164, "EIGHT STORIES THAT DEFINED THE DAY", 2, INK)
    cv.hline(16, 190, W - 32, INK)

    margin, gap = 16, 8
    cell_w = (W - 2 * margin - gap) // 2
    cell_h = 194
    top = 200
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cell_w + gap)
        cy = top + (i // 2) * (cell_h + gap)
        cv.rect(cx, cy, cell_w, cell_h, (255, 255, 255))
        cv.rect(cx, cy, cell_w, 2, LIGHT)
        cv.rect(cx, cy + cell_h - 2, cell_w, 2, LIGHT)
        draw_story(cv, cx, cy, cell_w, cell_h, story)

    cv.hline(16, 988, W - 32, INK)
    cv.text_centre(998, "REPORTED 18 NOVEMBER 2026", 2, INK)
    return cv


# ---------------------------------------------------------------- PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
