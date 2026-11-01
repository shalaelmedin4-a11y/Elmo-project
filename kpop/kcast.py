"""Characters and sets for 'Ein Tag als K-Pop Trainee' (original, fictional).

Builds on the paper cut-out kit in ../cartoon (paper.py, cast.py).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon"))

import numpy as np  # noqa: E402

from cast import (BOOT, SKIN, SKIN2, WHITE, WOOD, WOOD_D, bubble, burst, clamp, ease, face,  # noqa: E402,F401
                  hero_mouth, lerp, puff, seg, star, sweat, zzz)
from paper import INK  # noqa: E402

BLOND = (252, 238, 168)
BLOND_D = (232, 210, 130)
HOODIE = (34, 32, 38)
HOODIE_L = (62, 60, 70)
JEANS = (62, 70, 96)
SNEAKER = (250, 250, 250)
PINK = (255, 92, 170)
PINK_L = (255, 170, 214)
PURPLE = (140, 70, 200)
SUIT = (30, 30, 38)
RED = (220, 40, 50)
HAIRS = [(40, 34, 40), (110, 70, 40), (230, 140, 190), (180, 160, 230), (60, 50, 70), (200, 110, 70)]
HOODIES = [(150, 150, 160), (235, 235, 240), (60, 70, 110), (120, 90, 140), (90, 120, 110), (200, 170, 140)]


# ---------------------------------------------------------------- characters

def hair_puff(c, cx, cy, col, dark, big=1.0):
    """Fluffy hair: a ring of overlapping paper circles over the top of the head."""
    for k, a in enumerate(np.linspace(190, 350, 7)):
        r = (26 + 6 * (k % 2)) * big
        c.ell(cx + math.cos(math.radians(a)) * 54, cy + math.sin(math.radians(a)) * 58, r, r * .9, col, w=4, n=14)
    for k, dx in enumerate((-34, -12, 12, 34)):
        c.ell(cx + dx, cy - 36 + (k % 2) * 6, 20 * big, 16 * big, col, w=4, n=12)
    c.ell(cx - 18, cy - 62, 10, 6, dark, ol=None, n=8)
    c.ell(cx + 20, cy - 54, 8, 5, dark, ol=None, n=8)


def trainee(c, x, y, s=1.0, rot=0, flip=False, hero=False, hair=BLOND, hoodie=HOODIE, arms=(15, 15), legs=(0, 0),
            eyes="dot", mouth="smile", look=0, held=None, bounce=0, head_rot=0):
    """Big-head trainee in an oversized hoodie. Origin = between the feet."""
    if hero:
        mouth = hero_mouth(mouth)
    hl = tuple(min(255, v + 28) for v in hoodie)
    c.push(x, y + bounce, s, rot, flip)
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        c.push(side * 22, -72, 1, ang)
        c.rect(-14, -4, 14, 52, JEANS, w=5)
        c.ell(side * 8, 60, 28, 14, SNEAKER, w=5, n=16)
        c.line([(side * 8 - 26, 66), (side * 8 + 26, 66)], 3, (190, 190, 200))
        c.pop()
    # hood behind the neck + oversized body
    c.ell(0, -205, 66, 26, hl, w=5, n=18)
    c.poly([(-62, -210), (62, -210), (86, -66), (-86, -66)], hoodie, w=6)
    c.rrect(-46, -130, 46, -92, 12, hl, w=4)
    c.line([(-14, -205), (-16, -160)], 4, WHITE)
    c.line([(14, -205), (16, -160)], 4, WHITE)
    for side, a in ((-1, arms[0]), (1, arms[1])):
        c.push(side * 60, -196, 1, -side * a)
        c.rrect(-17, -6, 17, 96, 15, hoodie, w=5)
        c.ell(0, 100, 13, 11, SKIN, n=12, w=4)
        if side == 1 and held:
            held(c)
        c.pop()
    c.push(0, -270, 1, head_rot)
    c.ell(0, 0, 56, 64, SKIN)
    c.ell(-54, 6, 8, 12, SKIN2, n=10)
    c.ell(54, 6, 8, 12, SKIN2, n=10)
    face(c, 0, 8, eyes, mouth, look)
    hair_puff(c, 0, 0, hair, BLOND_D if hair == BLOND else tuple(max(0, v - 30) for v in hair))
    if hero:
        c.rrect(30, -46, 58, -34, 5, PINK, w=3)
    c.pop()
    c.pop()


def trainee_sit(c, x, y, s=1.0, hero=False, hair=BLOND, hoodie=HOODIE, eyes="dot", mouth="flat", head_down=False):
    """Sitting on the floor hugging the knees."""
    if hero:
        mouth = hero_mouth(mouth)
    c.push(x, y, s)
    c.ell(0, -70, 95, 70, hoodie, w=6, n=22)
    for dx in (-30, 30):
        c.ell(dx + 40, -95, 26, 48, JEANS, w=5, n=16)
        c.ell(dx + 60, -18, 26, 13, SNEAKER, w=5, n=14)
    c.rrect(-10, -120, 110, -86, 16, hoodie, w=5)
    c.push(-10, -170 + (25 if head_down else 0), .9, 15 if head_down else 0)
    c.ell(0, 0, 56, 64, SKIN)
    face(c, 0, 14 if head_down else 8, "closed" if head_down else eyes, mouth)
    hair_puff(c, 0, 0, hair, BLOND_D)
    if hero:
        c.rrect(30, -46, 58, -34, 5, PINK, w=3)
    c.pop()
    c.pop()


def sleeper_k(c, x, y, s=1.0, hair=(40, 34, 40), blanket=(150, 160, 190), hero=False):
    c.push(x, y, s)
    c.rrect(-140, -36, -60, 8, 14, WHITE, w=4)
    c.push(-96, -42, .7, -80)
    c.ell(0, 0, 56, 64, SKIN)
    face(c, 0, 8, "closed", hero_mouth("flat") if hero else "flat")
    hair_puff(c, 0, 0, hair, tuple(max(0, v - 30) for v in hair))
    c.pop()
    c.rrect(-70, -30, 130, 14, 12, blanket, w=4)
    c.pop()


def manager(c, x, y, s=1.0, flip=False, arm=20, arm_l=10, head_rot=0, clipboard=True, mouth="flat", held=None):
    """Strict manager: black suit, sunglasses, clipboard."""
    c.push(x, y, s, 0, flip)
    for side in (-1, 1):
        c.rect(side * 22 - 15, -150, side * 22 + 15, -6, SUIT, w=5)
        c.ell(side * 28, 0, 30, 12, (15, 15, 18), n=14)
    c.rrect(-60, -340, 60, -140, 24, SUIT, w=6)
    c.poly([(-24, -340), (24, -340), (0, -280)], WHITE, w=4)
    c.poly([(-7, -330), (7, -330), (10, -250), (0, -236), (-10, -250)], (150, 20, 40), w=3)
    c.line([(-24, -340), (-6, -230)], 4, (60, 60, 72))
    c.line([(24, -340), (6, -230)], 4, (60, 60, 72))
    for side, a in ((-1, arm_l), (1, arm)):
        c.push(side * 58, -325, 1, -side * a)
        c.rrect(-14, -4, 14, 128, 12, SUIT, w=5)
        c.ell(0, 134, 15, 15, SKIN, n=12)
        if side == -1 and clipboard:
            c.push(0, 140, 1, side * a)
            c.rect(-46, -10, 46, 110, (150, 110, 60), w=5)
            c.rect(-36, 4, 36, 100, WHITE, w=3)
            for k in range(5):
                c.line([(-26, 22 + k * 16), (26, 22 + k * 16)], 2, (150, 150, 160))
            c.rect(-16, -18, 16, -2, (180, 180, 190), w=3)
            c.pop()
        if side == 1 and held:
            held(c)
        c.pop()
    c.push(0, -400, 1, head_rot)
    c.ell(0, 0, 48, 58, SKIN)
    c.ell(0, -36, 50, 30, (20, 20, 24), a0=180, a1=360, n=16)
    c.rrect(-42, -16, -6, 8, 8, (10, 10, 14), w=3)
    c.rrect(6, -16, 42, 8, 8, (10, 10, 14), w=3)
    c.line([(-6, -6), (6, -6)], 4, (10, 10, 14))
    if mouth == "flat":
        c.line([(-14, 32), (14, 32)], 5)
    else:
        c.arc(0, 40, 14, 9, 200, 340, 5)
    c.pop()
    c.pop()


def judge(c, x, y, s=1.0, hair=(40, 34, 40), suit=(60, 60, 80), card=None, card_up=0.0, glasses=False):
    c.push(x, y, s)
    c.rrect(-58, -120, 58, 40, 24, suit, w=5)
    c.poly([(-18, -120), (18, -120), (0, -80)], WHITE, w=3)
    c.ell(0, -175, 46, 54, SKIN)
    c.ell(0, -205, 48, 28, hair, a0=180, a1=360, n=16)
    for sx in (-1, 1):
        c.ell(sx * 16, -172, 5, 5, INK, ol=None, n=10)
        c.line([(sx * 30, -192), (sx * 6, -186)], 5)
    if glasses:
        c.ell(-16, -172, 13, 11, (230, 240, 255), w=3, n=12)
        c.ell(16, -172, 13, 11, (230, 240, 255), w=3, n=12)
    c.arc(0, -138, 12, 7, 200, 340, 4)
    if card is not None:
        cy = -60 - 170 * card_up
        c.line([(30, cy + 50), (50, -40)], 6, (150, 110, 60))
        c.rect(-20, cy - 70, 100, cy + 50, WHITE, w=5)
        c.text(40, cy - 8, str(card), 80, fill=RED)
    c.pop()


def phone(c, x, y, s=1.0, rot=0, screen=(120, 200, 255)):
    c.push(x, y, s, rot)
    c.rrect(-22, -40, 22, 40, 8, (30, 30, 36), w=4)
    c.rect(-16, -32, 16, 30, screen, w=2)
    c.pop()


def heart(c, x, y, r, col=PINK, w=5):
    pts = []
    for a in np.linspace(0, 2 * math.pi, 28, endpoint=False):
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 16, y + hy * r / 16))
    c.poly(pts, col, w=w)


def fan(c, x, y, s, t, i, sign=True):
    c.push(x, y, s)
    hair = HAIRS[i % len(HAIRS)]
    c.rrect(-60, -60, 60, 120, 26, HOODIES[(i + 2) % len(HOODIES)], w=5)
    c.ell(0, -110, 50, 56, SKIN)
    c.ell(0, -140, 52, 30, hair, a0=180, a1=360, n=16)
    face(c, 0, -104, "happy", "grin")
    if sign:
        up = 18 * math.sin(t * 7 + i)
        c.line([(46, -40), (60, -230 + up)], 7, (150, 110, 60))
        heart(c, 64, -270 + up, 60, (PINK, (255, 60, 90), (200, 90, 255))[i % 3])
    c.pop()


# ---------------------------------------------------------------- sets

def bands(c, cols, top=0, bottom=1500):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, 3000, cols[-1], ol=None, jit=False)
    c.rect(-400, -1000, 1500, top + 5, cols[0], ol=None, jit=False)
    h = (bottom - top) / len(cols)
    for i, col in enumerate(cols):
        y0 = top + i * h
        pts = [(-400, y0 - 2)] + [(x, y0 + h + 10 * math.sin(x / 90 + i * 1.7)) for x in range(-400, 1560, 60)] + [(1500, y0 - 2)]
        c.poly(pts, col, ol=None, jit=False)
    c.layer = "mid"


def sparkles(c, t, n=26, seed=3, area=(0, 0, 1080, 1500), col=(255, 250, 220)):
    r = np.random.default_rng(seed)
    for k in range(n):
        x = r.uniform(area[0], area[2])
        y = r.uniform(area[1], area[3])
        ph = r.uniform(0, 6.28)
        tw = .5 + .5 * math.sin(t * 6 + ph)
        if tw > .25:
            star(c, x, y, 8 + 16 * tw, col, pts_n=4, w=3)


def stage(c, t, floor=1450, crowd=False):
    bands(c, [(70, 20, 110), (110, 30, 150), (160, 40, 170), (210, 60, 170), (245, 90, 175), (255, 130, 190)], 0, floor)
    c.layer = "bg"
    for k, x0 in enumerate((150, 540, 930)):
        sw = 40 * math.sin(t * 1.3 + k)
        c.poly([(x0 - 30, -50), (x0 + 30, -50), (x0 + 200 + sw, floor), (x0 - 200 + sw, floor)], (255, 190, 230), ol=None)
    c.layer = "mid"
    for side in (-1, 1):
        x = 540 + side * 560
        c.poly([(x - 140, -100), (x + 140, -100), (x + 110 * -side + 20, floor), (x - 20, floor)], (90, 20, 90), w=6)
        for k in range(3):
            c.line([(x - 90 + k * 60, -100), (x - 60 + k * 50 - side * 40, floor)], 3, (60, 10, 60))
    c.rect(-400, floor, 1500, 3000, (200, 50, 150), w=6)
    c.rect(-400, floor, 1500, floor + 26, (255, 120, 200), w=5)
    for k in range(12):
        on = (k + int(t * 6)) % 3 != 0
        c.ell(30 + k * 92, floor + 13, 9, 9, (255, 250, 200) if on else (180, 120, 160), w=3, n=10)
    sparkles(c, t, 30, area=(0, 60, 1080, floor - 40))


def studio(c, t, dark=False, floor=1420):
    """Dance studio with mirror wall, ballet bar and a big wall clock."""
    wall = (70, 74, 96) if dark else (196, 200, 214)
    c.layer = "bg"
    c.rect(-400, -1000, 1500, floor, wall, ol=None, jit=False)
    c.layer = "mid"
    mirror = (40, 52, 80) if dark else (186, 216, 236)
    shine = (70, 86, 120) if dark else (236, 248, 255)
    c.rect(20, 520, 1060, floor, mirror, w=6)
    for k in range(1, 4):
        c.line([(20 + k * 260, 520), (20 + k * 260, floor)], 5)
    for k in range(4):
        x = 80 + k * 260
        c.poly([(x, 560), (x + 40, 560), (x - 60, 820), (x - 100, 820)], shine, ol=None)
    c.rect(20, 1180, 1060, 1196, (150, 150, 160) if not dark else (80, 80, 96), w=4)
    floor_col = (120, 86, 60) if dark else (196, 150, 100)
    c.rect(-400, floor, 1500, 3000, floor_col, w=5)
    for k in range(-3, 14):
        c.line([(k * 120 + 40, floor), (k * 170 - 160, 3000)], 3, tuple(max(0, v - 30) for v in floor_col))


def wall_clock(c, x, y, r, hh, mm):
    c.ell(x, y, r, r, WHITE, w=7, n=30)
    for k in range(12):
        a = math.radians(k * 30)
        c.line([(x + math.cos(a) * r * .8, y + math.sin(a) * r * .8), (x + math.cos(a) * r * .92, y + math.sin(a) * r * .92)], 4)
    for ang, ln, wd in (((hh % 12 + mm / 60) * 30, .5, 9), (mm * 6, .78, 6)):
        a = math.radians(ang - 90)
        c.line([(x, y), (x + math.cos(a) * r * ln, y + math.sin(a) * r * ln)], wd)
    c.ell(x, y, 8, 8, INK, ol=None, n=10)


def plain_room(c, wall, floor_col, floor_y=1450):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, floor_y, wall, ol=None, jit=False)
    for k in range(-1, 12):
        c.line([(k * 110, -1000), (k * 110, floor_y)], 3, tuple(max(0, v - 12) for v in wall), jit=False)
    c.layer = "mid"
    c.rect(-400, floor_y, 1500, 3000, floor_col, w=5)
    for k in range(-2, 12):
        c.line([(k * 120 + 40, floor_y), (k * 160 - 120, 3000)], 3, tuple(max(0, v - 22) for v in floor_col))


def sign(c, x, y, w, h, txt, size, paper=WHITE, ink=INK, rot=0, icon=None):
    c.push(x, y, 1, rot)
    c.rect(-w / 2, -h / 2, w / 2, h / 2, paper, w=6)
    c.pop()
    c.text(x + (55 if icon else 0), y + 3, txt, size, fill=ink)
    if icon == "noheart":
        heart(c, x - w / 2 + 60, y, 34, PINK, w=4)
        c.arc(x - w / 2 + 60, y, 46, 46, 0, 360, 8, RED)
        c.line([(x - w / 2 + 28, y - 32), (x - w / 2 + 92, y + 32)], 9, RED)
