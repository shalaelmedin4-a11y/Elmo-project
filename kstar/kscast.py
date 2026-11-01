"""Halbo the pop star + simple sets for 'Ein Tag als K-Pop-Star' (original, fictional)."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kpop"))

import numpy as np  # noqa: E402

from kcast import *  # noqa: E402,F401,F403  (also puts ../cartoon on the path)
from paper import INK  # noqa: E402

HAIR = (255, 118, 186)
HAIR_D = (220, 80, 150)
SILVER = (206, 210, 224)
SILVER_D = (160, 166, 184)


def drawn_z(c, x, y, s):
    """A 'Z' drawn with lines (no font) for sleeping."""
    c.line([(x - 12 * s, y - 12 * s), (x + 12 * s, y - 12 * s), (x - 12 * s, y + 12 * s), (x + 12 * s, y + 12 * s)],
           5 * s, (240, 240, 255))


def zz(c, x, y, t, s=1.0):
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        drawn_z(c, x + 30 * ph * s + k * 6, y - 130 * ph * s, (0.8 + 0.6 * ph) * s)


def back_hair(c, length=200):
    """Long pink hair behind the body with a wavy bottom edge."""
    pts = [(-60, -50), (-80, 0), (-92, 80), (-96, length - 30)]
    for k in range(7):
        x = -96 + k * 32
        pts.append((x + 16, length + (12 if k % 2 == 0 else -4)))
    pts += [(96, length - 30), (92, 80), (80, 0), (60, -50), (0, -66)]
    c.poly(pts, HAIR, w=5)
    for x in (-50, 0, 50):
        c.line([(x * .8, 0), (x, length - 30)], 3, HAIR_D)


def front_hair(c):
    c.ell(0, -40, 62, 36, HAIR, w=5, a0=180, a1=360, n=18)
    c.poly([(-62, -40), (-44, -40), (-50, 30), (-60, 70), (-70, 40)], HAIR, w=4)
    c.poly([(62, -40), (44, -40), (50, 30), (60, 70), (70, 40)], HAIR, w=4)
    c.ell(-20, -58, 10, 6, HAIR_D, ol=None, n=8)
    c.ell(16, -50, 8, 5, HAIR_D, ol=None, n=8)


def star_girl(c, x, y, s=1.0, rot=0, outfit="jacket", arms=(15, 15), legs=(0, 0), eyes="dot", mouth="smile",
              look=0, held=None, bounce=0, head_rot=0, seated=False, breathe=0.0):
    """Halbo: long pink hair, sparkly silver jacket (stage) or plain black hoodie (off stage)."""
    mouth = hero_mouth(mouth)
    body = SILVER if outfit == "jacket" else HOODIE
    body_d = SILVER_D if outfit == "jacket" else HOODIE_L
    c.push(x, y + bounce, s, rot)
    # long hair behind the body
    c.push(0, -270, 1, head_rot * .5)
    back_hair(c)
    c.pop()
    if seated:
        for side in (-1, 1):
            c.rect(side * 24 - 14, -70, side * 24 + 14, -6, JEANS, w=5)
            c.ell(side * 26, -78, 30, 22, JEANS, w=5, n=14)
            c.ell(side * 30, 0, 28, 14, SNEAKER, w=5, n=16)
    else:
        for side, ang in ((-1, legs[0]), (1, legs[1])):
            c.push(side * 22, -72, 1, ang)
            c.rect(-14, -4, 14, 52, JEANS, w=5)
            c.ell(side * 8, 60, 28, 14, SNEAKER, w=5, n=16)
            c.pop()
    sy = 1 + breathe
    c.push(0, -66, 1, 0)
    c.push(0, 0, 1, 0)
    c.stack[-1] = c.stack[-1] @ np.array([[1, 0, 0], [0, sy, 0], [0, 0, 1]], float)
    c.poly([(-58, -144), (58, -144), (80, 0), (-80, 0)], body, w=6)
    if outfit == "jacket":
        c.line([(0, -144), (0, 0)], 4, SILVER_D)
        c.poly([(-58, -144), (-10, -144), (-30, -96)], body_d, w=4)
        c.poly([(58, -144), (10, -144), (30, -96)], body_d, w=4)
    else:
        c.rrect(-44, -64, 44, -26, 12, body_d, w=4)
        c.line([(-14, -140), (-16, -96)], 4, WHITE)
        c.line([(14, -140), (16, -96)], 4, WHITE)
    c.pop()
    c.pop()
    for side, a in ((-1, arms[0]), (1, arms[1])):
        c.push(side * 58, -198, 1, -side * a)
        c.rrect(-16, -6, 16, 92, 14, body, w=5)
        c.ell(0, 98, 13, 11, SKIN, n=12, w=4)
        if side == 1 and held:
            held(c)
        c.pop()
    if outfit == "jacket":  # sparkles on the jacket
        for k, (sx, syy) in enumerate(((-34, -170), (30, -120), (-20, -100), (40, -180), (-50, -130))):
            star(c, sx, syy * (1 + breathe), 7 + 2 * ((k + int(c.rng.random() * 3)) % 2), WHITE, pts_n=4, w=2)
    c.push(0, -270, 1, head_rot)
    c.ell(0, 0, 56, 64, SKIN)
    face(c, 0, 10, eyes, mouth, look)
    front_hair(c)
    c.pop()
    c.pop()


def girl_sit_floor(c, x, y, s=1.0, outfit="jacket", eyes="dot", mouth="flat", head_down=False, breathe=0.0, look=0):
    """Sitting on the floor, knees up, arms around the knees."""
    mouth = hero_mouth(mouth)
    body = SILVER if outfit == "jacket" else HOODIE
    c.push(x, y, s)
    c.push(0, -190 + (20 if head_down else 0), .95, 0)
    back_hair(c, 150)
    c.pop()
    c.ell(0, -70 - 6 * breathe * 10, 92, 72 * (1 + breathe), body, w=6, n=22)
    for dx in (-36, 36):
        c.ell(dx, -96, 30, 52, JEANS, w=5, n=16)
        c.ell(dx, -16, 30, 14, SNEAKER, w=5, n=14)
    c.rrect(-80, -130, 80, -98, 16, body, w=5)
    c.push(0, -190 + (20 if head_down else 0), .95, 12 if head_down else 0)
    c.ell(0, 0, 56, 64, SKIN)
    face(c, 0, 12, "closed" if head_down else eyes, mouth, look)
    front_hair(c)
    c.pop()
    c.pop()


def staff(c, x, y, s, hair, shirt, arms=(15, 15), held=None, flip=False, mouth="flat"):
    trainee(c, x, y, s, hair=hair, hoodie=shirt, arms=arms, held=held, flip=flip, mouth=mouth)


def simple_stage(c, t, floor=1560):
    bands(c, [(90, 30, 140), (140, 40, 170), (200, 60, 175), (245, 100, 185), (255, 150, 205)], 0, floor)
    c.layer = "bg"
    for x0 in (300, 780):
        c.poly([(x0 - 26, -50), (x0 + 26, -50), (x0 + 210, floor), (x0 - 210, floor)], (255, 196, 232), ol=None)
    c.layer = "mid"
    c.rect(-400, floor, 1500, 3000, (205, 55, 155), w=6)
    c.rect(-400, floor, 1500, floor + 26, (255, 130, 205), w=5)
    sparkles(c, t, 10, seed=4, area=(60, 120, 1020, floor - 300))


def drawn_zeros(c, x, y, n=7, r=34, col=RED):
    """A 'huge number' made from drawn shapes (no font): a red bar + rings of zeros."""
    c.rect(x - n * r * 1.1 - 60, y - 10, x - n * r * 1.1 - 20, y + 10, col, w=3)
    for k in range(n):
        cx = x - (n - 1) * r * 1.1 + k * r * 2.2
        c.ell(cx, y, r * .75, r, col, w=4, n=20)
        c.ell(cx, y, r * .38, r * .62, (250, 248, 240), w=3, n=16)


def angry_note(c, x, y, kind, rot=0, s=1.0):
    """Small paper note with an angry symbol (no readable words)."""
    c.push(x, y, s, rot)
    c.rect(-70, -56, 70, 56, (250, 246, 230), w=4)
    if kind == 0:      # angry face
        c.ell(0, 4, 34, 34, (255, 210, 90), w=4, n=20)
        c.line([(-22, -16), (-6, -8)], 5)
        c.line([(22, -16), (6, -8)], 5)
        c.arc(0, 26, 14, 8, 200, 340, 5)
    elif kind == 1:    # big red X
        c.line([(-30, -30), (30, 30)], 10, RED)
        c.line([(-30, 30), (30, -30)], 10, RED)
    elif kind == 2:    # scribble
        c.line([(-44, 10), (-30, -20), (-14, 18), (0, -22), (16, 20), (30, -18), (44, 12)], 6, RED)
    elif kind == 3:    # crossed-out heart
        heart(c, 0, 4, 28, PINK, w=4)
        c.line([(-34, -30), (34, 36)], 8, RED)
    else:              # lightning bolt
        c.poly([(8, -40), (-20, 6), (0, 6), (-10, 40), (22, -8), (2, -8)], (255, 210, 60), w=4)
    c.pop()
