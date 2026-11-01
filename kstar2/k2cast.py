"""Big centred pop-star rig for 'Ein Tag als K-Pop-Star' (version 2).

Halbo is always drawn with the same transform: centred, from the knees up,
about two thirds of the frame height. Arms have elbows (2-bone IK) so hand
gestures like yawning, wiping sweat or a hand heart read clearly.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kstar"))

import numpy as np  # noqa: E402

from kscast import *  # noqa: E402,F401,F403  (kpop + cartoon kits)
from paper import INK  # noqa: E402

X0, FEET, SC = 540, 2090, 4.2      # fixed "camera": same size and place in every scene
WMUL = 0.42                        # keep outlines bold but not huge at this scale
HEAD_Y = -270
SHOULDER = 58, -196


def to_screen(lx, ly):
    return X0 + lx * SC, FEET + ly * SC


def limb(c, p1, p2, w, col):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    c.poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], col, w=4)
    c.ell(x1, y1, w / 2, w / 2, col, w=4, n=14)


def ik(sx, sy, tx, ty, l1, l2, side):
    dx, dy = tx - sx, ty - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 0.5))
    th = math.atan2(dy, dx)
    al = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    best = None
    for sg in (1, -1):
        ex, ey = sx + l1 * math.cos(th + sg * al), sy + l1 * math.sin(th + sg * al)
        score = side * ex + 0.3 * ey          # elbow out to the side and slightly down
        if best is None or score > best[0]:
            best = (score, ex, ey)
    hx, hy = sx + d * math.cos(th), sy + d * math.sin(th)
    return (best[1], best[2]), (hx, hy)


def arm(c, side, target, col, held=None):
    sx, sy = side * SHOULDER[0], SHOULDER[1]
    (ex, ey), (hx, hy) = ik(sx, sy, target[0], target[1], 62, 62, side)
    limb(c, (sx, sy), (ex, ey), 34, col)
    limb(c, (ex, ey), (hx, hy), 30, col)
    c.ell(hx, hy, 15, 15, SKIN, w=4, n=14)
    if held:
        held(c, hx, hy)
    return hx, hy


BIG_EYES = dict(rx=15, ry=19)


def big_face(c, eyes="open", mouth="smile", look=(0, 0), brows="calm", skin=SKIN, blink=False):
    mouth = hero_mouth(mouth)
    ex, ey = 22, 4
    lx, ly = look
    for sx in (-1, 1):
        x = sx * ex
        if eyes in ("closed", "sleep") or blink:
            c.arc(x, ey + 2, 14, 9, 20, 160, 4)
        elif eyes == "happy":
            c.arc(x, ey + 8, 13, 12, 200, 340, 5)
        else:
            c.ell(x, ey, 15, 19, WHITE, w=4, n=20)
            c.ell(x + lx * 5, ey + ly * 6 + 2, 8.5, 11, (40, 30, 50), ol=None, n=16)
            c.ell(x + lx * 5 + 3, ey + ly * 6 - 3, 3, 3.5, WHITE, ol=None, n=8)
            if eyes == "tired":       # heavy eyelids
                c.poly([(x - 17, ey - 21), (x + 17, ey - 21), (x + 17, ey - 3), (x - 17, ey - 3)], skin, w=3)
            if eyes == "sad":
                c.line([(x - 15, ey - 6), (x + 15, ey - 6)], 3, (90, 70, 90))
        # brows
        if brows == "sad":
            c.line([(x - 12 * sx, ey - 28), (x + 12 * sx, ey - 33 + 8)], 4)
        elif brows == "up":
            c.arc(x, ey - 30, 12, 6, 200, 340, 4)
        else:
            c.line([(x - 11, ey - 29), (x + 11, ey - 29)], 4)
    c.ell(-34, 22, 9, 5, (255, 170, 180), ol=None, n=10)
    c.ell(34, 22, 9, 5, (255, 170, 180), ol=None, n=10)
    my = 36
    if mouth == "smile":
        c.arc(0, my - 6, 11, 8, 20, 160, 4)
    elif mouth == "grin":
        c.ell(0, my, 13, 8, (150, 40, 60), w=3, a0=0, a1=180, n=12)
    elif mouth == "o":
        c.ell(0, my, 6, 7, (120, 30, 40), w=3, n=12)
    elif mouth == "open":
        c.ell(0, my + 2, 10, 11, (120, 30, 40), w=3, n=14)
    elif mouth == "yawn":
        c.ell(0, my + 6, 14, 20, (120, 30, 40), w=3, n=16)
    elif mouth == "sad":
        c.arc(0, my + 6, 10, 7, 200, 340, 4)
    else:
        c.line([(-9, my), (9, my)], 4)


HAIR_L = (255, 170, 214)


def big_back_hair(c):
    """Voluminous long hair behind the head and shoulders (head-local coords)."""
    pts = []
    for a in np.linspace(180, 360, 13):
        r = math.radians(a)
        pts.append((math.cos(r) * 78, -6 + math.sin(r) * 86))
    pts += [(84, 40), (90, 120), (94, 196)]
    for k in range(6):
        x = 94 - k * 37.6
        pts.append((x - 19, 214 if k % 2 == 0 else 200))
    pts += [(-94, 196), (-90, 120), (-84, 40)]
    c.poly(pts, HAIR, w=5)
    for x in (-60, -20, 20, 60):
        c.line([(x * .9, 30), (x, 190)], 3, HAIR_D)


def big_front_hair(c):
    """Fringe cap with scalloped bangs + two thin wavy side locks."""
    cap = []
    for a in np.linspace(188, 352, 15):
        r = math.radians(a)
        cap.append((math.cos(r) * 62, -2 + math.sin(r) * 72))
    for k in range(5):                       # five rounded bangs, right to left
        x0 = 58 - k * 23.2
        for a in np.linspace(0, 180, 6):
            r = math.radians(a)
            cap.append((x0 - 11.6 + math.cos(r) * 11.6, -36 + math.sin(r) * 12))
    c.poly(cap, HAIR, w=5)
    c.line([(-30, -60), (-6, -66), (22, -58)], 6, HAIR_L)
    for sx in (-1, 1):
        lock = [(sx * 54, -34), (sx * 62, -20), (sx * 66, 30), (sx * 60, 80), (sx * 68, 130),
                (sx * 54, 134), (sx * 46, 80), (sx * 52, 30), (sx * 44, -20)]
        c.poly(lock, HAIR, w=4)


def popstar(c, t, outfit="hoodie", hands=((-80, -70), (80, -70)), eyes="open", mouth="smile", look=(0, 0),
            brows="calm", head_rot=0, sway=0, held=(None, None), skin=SKIN, headphones=False, bob=0.0, blink_ok=True):
    """Draw Halbo with the fixed framing. hands = targets in body-local coords (x, y)."""
    c.push(X0, FEET + bob * SC, SC, sway)
    c.wmul = WMUL
    body = SILVER if outfit == "jacket" else HOODIE
    blink = blink_ok and (int(t * 12) % 41) in (0, 1) and eyes in ("open", "tired", "sad")
    c.push(0, HEAD_Y, 1, head_rot * .5)
    big_back_hair(c)
    c.pop()
    # torso (continues below the frame)
    c.ell(0, -206, 64, 22, HOODIE_L if outfit == "hoodie" else (40, 40, 48), w=5, n=18)
    c.poly([(-62, -206), (62, -206), (86, 20), (-86, 20)], body, w=6)
    if outfit == "jacket":
        c.poly([(-22, -206), (22, -206), (14, 20), (-14, 20)], (40, 40, 48), w=4)
        c.poly([(-62, -206), (-22, -206), (-36, -150)], SILVER_D, w=4)
        c.poly([(62, -206), (22, -206), (36, -150)], SILVER_D, w=4)
        r = np.random.default_rng(int(t * 12) // 2)
        for k in range(14):
            sx = r.uniform(-70, 70)
            sy = r.uniform(-190, 0)
            if abs(sx) > 24:
                star(c, sx, sy, r.uniform(4, 8), WHITE, pts_n=4, w=2)
    else:
        c.rrect(-46, -100, 46, -56, 14, HOODIE_L, w=4)
        c.line([(-14, -204), (-17, -150)], 4, WHITE)
        c.line([(14, -204), (17, -150)], 4, WHITE)
        c.ell(-17, -146, 4, 4, WHITE, w=2, n=8)
        c.ell(17, -146, 4, 4, WHITE, w=2, n=8)
    # head
    c.push(0, HEAD_Y, 1, head_rot)
    c.ell(0, 0, 56, 64, skin)
    c.ell(-54, 8, 8, 12, tuple(max(0, v - 20) for v in skin), n=10)
    c.ell(54, 8, 8, 12, tuple(max(0, v - 20) for v in skin), n=10)
    big_face(c, eyes, mouth, look, brows, skin, blink)
    big_front_hair(c)
    if headphones:
        c.arc(0, -10, 74, 80, 190, 350, 14, (40, 40, 50))
        for sx in (-1, 1):
            c.rrect(sx * 64 - 16, -20, sx * 64 + 16, 34, 12, (60, 60, 72), w=4)
    c.pop()
    # arms in front
    hp = []
    for i, side in enumerate((-1, 1)):
        hp.append(arm(c, side, hands[i], body, held[i]))
    c.pop()
    c.wmul = 1.0
    return [to_screen(*p) for p in hp]


# ---------------------------------------------------------------- props & extras (screen coords)

def manager_side(c, x, y, s=1.5, **kw):
    c.wmul = 0.8
    manager(c, x, y, s, **kw)
    c.wmul = 1.0


def clock_left(c, txt):
    """Small paper clock sign, top-left corner (the only text in the video)."""
    c.cam = (540, 960, 1.0)
    c.stack = [np.eye(3)]
    c.layer = "ui"
    c.push(175, 150, 1, -3)
    c.rrect(-140, -56, 140, 56, 18, (255, 244, 230), w=6)
    c.ell(-88, 0, 34, 34, (255, 92, 170), w=5, n=24)
    c.ell(-88, 0, 24, 24, WHITE, w=3, n=20)
    h = int(txt[:2]) % 12 + int(txt[3:]) / 60
    m = int(txt[3:])
    for ang, ln, wd in ((h / 12 * 360, 14, 5), (m / 60 * 360, 20, 4)):
        a = math.radians(ang - 90)
        c.line([(-88, 0), (-88 + math.cos(a) * ln, math.sin(a) * ln)], wd)
    c.text(36, 3, txt, 56, fill=INK)
    c.pop()


def flat_bg(c, col, floor_y=None, floor_col=None):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, 3000, col, ol=None, jit=False)
    for k in range(-1, 12):
        c.line([(k * 120, -1000), (k * 120, floor_y or 3000)], 3, tuple(max(0, v - 10) for v in col), jit=False)
    c.layer = "mid"
    if floor_y:
        c.rect(-400, floor_y, 1500, 3000, floor_col, w=5)


def sweat_drop(c, x, y, s=1.6):
    c.poly([(x, y - 18 * s), (x + 9 * s, y), (x, y + 8 * s), (x - 9 * s, y)], (140, 210, 250), w=4)


def note_shape(c, x, y, s=1.0, col=WHITE):
    c.ell(x, y, 18 * s, 13 * s, col, w=4, n=12)
    c.line([(x + 16 * s, y), (x + 16 * s, y - 64 * s), (x + 38 * s, y - 48 * s)], 6 * s)
