"""Scenes & shots for 'Ein Tag als Profifußballer … mit Halbo!'.

Every scene = 2-3 quick shots (close-up / medium / side view / drone).
Halbo is always centred and big (except the drone shot, where a ring marks him).
Scene functions: fn(c, t, L, cues) -> look dict. All coordinates are screen px.
"""
import math

import numpy as np
from PIL import Image

from fb_rig import (HAIR, KIT_B, KIT_Y, LINE, SKIN, WHITE, Rig, kick_pose, run_pose, shade)

SS = 2
W, H = 1080, 1920

# framing presets (x, feet_y, scale) for the front view
FULL = (540, 1820, 1.9)
MED = (540, 2620, 3.0)
CLOSE = (540, 5700, 6.5)
SIDE = (540, 1790, 1.9)

_grad_cache = {}


def grad(c, top, bottom, y0=0, y1=H, layer="bg"):
    """Smooth vertical gradient painted straight into a layer (anime-style sky / wall light)."""
    key = (top, bottom, y0, y1)
    if key not in _grad_cache:
        h = max(1, int((y1 - y0) * SS))
        k = np.linspace(0, 1, h)[:, None]
        col = (np.array(top)[None, :] * (1 - k) + np.array(bottom)[None, :] * k).astype(np.uint8)
        arr = np.repeat(col[:, None, :], W * SS, axis=1)
        a = np.full((h, W * SS, 1), 255, np.uint8)
        _grad_cache[key] = Image.fromarray(np.concatenate([arr, a], 2), "RGBA")
    c.img[layer].alpha_composite(_grad_cache[key], (0, int(y0 * SS)))


def P(c, pts, col, ol=True, w=1.2):
    c.poly(pts, col, ol=LINE if ol else None, w=w)


def R(c, x0, y0, x1, y1, col, ol=True, w=1.2):
    c.rect(x0, y0, x1, y1, col, ol=LINE if ol else None, w=w)


def E(c, x, y, rx, ry, col, ol=True, w=1.2, n=30):
    c.ell(x, y, rx, ry, col, ol=LINE if ol else None, w=w, n=n)


def L_(c, pts, w, col=LINE):
    c.line(pts, w, col)


def shots(t, bounds):
    for i, b in enumerate(bounds):
        if t < b:
            return i, (t - (bounds[i - 1] if i else 0))
    return len(bounds), t - (bounds[-1] if bounds else 0)


def zoom(c, k, amount=0.05, cx=540, cy=960):
    c.cam = (cx, cy, 1.0 + amount * k)


def head_at(hx, hy, s, lean):
    """Feet position so that the head centre lands at (hx, hy) for a body rotated by `lean` degrees."""
    r = math.radians(lean)
    return hx - 748 * s * math.sin(r), hy + 748 * s * math.cos(r)


def draw_z(c, x, y, s):
    L_(c, [(x - 14 * s, y - 14 * s), (x + 14 * s, y - 14 * s), (x - 14 * s, y + 14 * s), (x + 14 * s, y + 14 * s)],
       5 * s, (240, 240, 250))


def hero(c, outfit="kit"):
    return Rig(c, outfit=outfit)


def mate(c, number, hair=(40, 34, 30), skin=(200, 150, 112), outfit="kit"):
    r = Rig(c, hair=hair, hair_s=shade(hair, .7), hair_h=shade(hair, 1.25), skin=skin, skin_s=shade(skin, .86),
            eye=(70, 60, 50), hero=False, number=number, outfit=outfit, style=1)
    return r


def opponent(c):
    r = mate(c, "8", hair=(30, 26, 24), skin=(236, 204, 178))
    r.o.update(shirt=(232, 234, 240), shirt_s=(196, 200, 212), trim=(50, 80, 150), shorts=(50, 80, 150),
               socks=(232, 234, 240))
    return r


def ball(c, x, y, r=34, rot=0):
    E(c, x, y, r, r, WHITE, n=24)
    for k in range(5):
        a = math.radians(rot + k * 72)
        E(c, x + math.cos(a) * r * .55, y + math.sin(a) * r * .55, r * .2, r * .2, (60, 60, 66), ol=False, n=8)
    E(c, x, y, r * .26, r * .26, (60, 60, 66), ol=False, n=8)
    P(c, [(x + r * .1, y - r * .9), (x + r * .8, y - r * .4), (x + r * .9, y + r * .3), (x + r * .6, y + r * .2)],
      (214, 214, 214), ol=False)


# ================================================================ INTRO
def intro(c, t, L, cues):
    zoom(c, t / L, 0.04)
    grad(c, (60, 74, 96), (150, 132, 112))
    c.layer = "bg"
    for k in range(5):                                           # stadium bowl silhouette + lights
        R(c, -50, 1080 + k * 70, 1130, 1150 + k * 70, shade((70, 74, 86), 1 + k * .06), ol=False)
    for x in (120, 960):
        R(c, x - 6, 300, x + 6, 1080, (80, 84, 96), ol=False)
        E(c, x, 290, 70, 26, (255, 236, 190), ol=False)
    c.layer = "mid"
    R(c, -50, 1500, 1130, 2600, (88, 128, 76), ol=False)
    for k in range(6):
        R(c, -50 + k * 200, 1500, 50 + k * 200, 2600, (96, 138, 82), ol=False)
    c.layer = "fg"
    hero(c).front(540, 3000, 2.9, t=t, hands=((-60, -470), (60, -470)) if t < cues[1][0] else ((-150, -650), (140, -840)),
                  held=(None, None), mouth="smile" if t < cues[1][0] else "grin", eyes="open", brows="calm")
    c.layer = "ui"
    c.cam = (540, 960, 1.0)
    c.stack = [np.eye(3)]
    c.boil = 0
    pop = min(1, (t - 0.1) / 0.25)
    if t > 0.1:
        s = 0.9 + 0.1 * pop
        c.push(540, 250, s)
        c.text(4, 6, "Ein Tag als", 86, fill=(30, 30, 34))
        c.text(0, 0, "Ein Tag als", 86, fill=WHITE)
        c.text(4, 116, "Profifußballer", 112, fill=(30, 30, 34))
        c.text(0, 110, "Profifußballer", 112, fill=(250, 214, 96))
        c.pop()
    if t >= cues[1][0] - 0.05:
        k = min(1, (t - cues[1][0]) / 0.2)
        c.push(540, 500, 0.8 + 0.2 * k)
        c.text(4, 6, "… mit Halbo!", 92, fill=(30, 30, 34))
        c.text(0, 0, "… mit Halbo!", 92, fill=WHITE)
        c.pop()
    c.layer = "mid"
    return dict(sat=0.88, warm=0.04)


# ================================================================ 06:30 wake up
def bedroom(c, sunrise=1.0):
    grad(c, (198, 190, 184), (170, 160, 152))
    c.layer = "bg"
    R(c, 170, 260, 910, 1080, (60, 56, 60), ol=True)                                   # big window
    c.layer = "mid"
    grad(c, (120, 130, 170), (246, 170, 120), 270, 1070, layer="mid")
    c.layer = "mid"
    E(c, 540, 1000, 130, 130, (255, 214, 150), ol=False)
    R(c, -50, 1000, 1130, 1076, (150, 132, 140), ol=False)
    R(c, 160, 250, 920, 270, (60, 56, 60))
    R(c, 160, 1070, 920, 1090, (60, 56, 60))
    R(c, 533, 260, 547, 1080, (60, 56, 60))
    R(c, -50, 1600, 1130, 2600, (150, 126, 104), ol=False)


def wake(c, t, L, cues):
    i, lt = shots(t, [1.7])
    r = hero(c, "sleep")
    if i == 0:                                                       # close-up on the pillow
        zoom(c, lt / 1.7, 0.04)
        grad(c, (176, 170, 168), (150, 144, 140))
        c.layer = "mid"
        P(c, [(-40, 700), (1120, 640), (1120, 1500), (-40, 1560)], (236, 232, 226))     # pillow
        c.layer = "fg"
        r.front(540 + 748 * 5.6, 1010, 5.6, t=t, lean=-90, eyes="closed" if lt < 1.0 else "half",
                mouth="flat", show_legs=False, hands=((-100, -420), (100, -420)))
        P(c, [(-60, 1300), (1140, 1240), (1140, 2600), (-60, 2600)], (120, 136, 170))  # blanket
        c.rrect(820, 1330, 940, 1530, 18, (40, 40, 46), ol=LINE, w=1.2)                 # phone alarm
        R(c, 834, 1350, 926, 1505, (150, 190, 230) if int(lt * 6) % 2 else (90, 110, 140), ol=False)
        if int(lt * 6) % 2:
            for k in range(3):
                L_(c, [(960 + k * 20, 1300 - k * 30), (990 + k * 20, 1280 - k * 30)], 4, (255, 236, 160))
        return dict(sat=0.85, warm=0.06)
    zoom(c, lt / (L - 1.7), 0.04)
    bedroom(c)
    c.layer = "mid"
    P(c, [(-60, 1500), (1140, 1500), (1140, 2600), (-60, 2600)], (220, 214, 206))     # bed
    c.layer = "fg"
    k = min(1, lt / 0.8)
    up = ((-150 - 30 * k, -640 - 320 * k), (150 + 30 * k, -640 - 320 * k))
    yawn = 0.4 < lt < 1.6
    r.front(*MED, t=t, hands=up, eyes="closed" if yawn else "open", mouth="yawn" if yawn else "smile",
            brows="up" if yawn else "calm", show_legs=False)
    return dict(sat=0.88, warm=0.08)


# ================================================================ 07:30 breakfast
def kitchen_bg(c):
    grad(c, (214, 206, 194), (190, 180, 168))
    c.layer = "bg"
    for k in range(4):
        R(c, 40 + k * 260, 200, 280 + k * 260, 560, (232, 226, 216))
        L_(c, [(250 + k * 260, 360), (250 + k * 260, 420)], 6, (150, 140, 130))
    R(c, -50, 560, 1130, 600, (170, 160, 150), ol=False)
    c.layer = "mid"


def bowl_food(c, x, y, s=1.0):
    E(c, x, y, 150 * s, 50 * s, (240, 238, 232))
    E(c, x, y - 6 * s, 128 * s, 34 * s, (226, 206, 160), ol=False)
    for k in range(6):
        E(c, x - 80 * s + k * 30 * s, y - 10 * s, 12 * s, 10 * s, (120, 60, 110) if k % 2 else (200, 70, 80), n=12)
    P(c, [(x - 140 * s, y), (x + 140 * s, y), (x + 110 * s, y + 80 * s), (x - 110 * s, y + 80 * s)], (240, 238, 232))


def breakfast_table(c):
    R(c, -60, 1640, 1140, 2600, (190, 150, 110))
    R(c, -60, 1640, 1140, 1660, (210, 170, 128), ol=False)
    bowl_food(c, 540, 1680)
    E(c, 190, 1700, 120, 36, (240, 238, 232))                                         # eggs
    for dx in (-40, 40):
        E(c, 190 + dx, 1690, 44, 28, WHITE)
        E(c, 190 + dx, 1690, 18, 14, (240, 190, 70), n=14)
    P(c, [(800, 1690), (900, 1660), (980, 1700), (900, 1720)], (240, 210, 90))        # banana
    E(c, 990, 1640, 40, 40, (200, 70, 60), n=18)                                      # apple


def mug(c, x, y, s=1.0):
    R(c, x - 50 * s, y - 70 * s, x + 50 * s, y + 50 * s, (236, 232, 224))
    c.arc(x + 58 * s, y - 10 * s, 26 * s, 30 * s, -90, 90, 8 * s, LINE)
    E(c, x, y - 70 * s, 48 * s, 12 * s, (110, 74, 50), n=18)


def breakfast(c, t, L, cues):
    i, lt = shots(t, [cues[1][0] - 0.25])
    r = hero(c, "home")
    if i == 0:
        zoom(c, lt / 3, 0.04)
        kitchen_bg(c)
        c.layer = "fg"
        up = int(t * 1.4) % 2

        def spoon(rr, hx, hy):
            L_(c, [(0, 0), (0, 0)], 1)
        hand = (40, -730) if up else (60, -470)
        r.front(*MED, t=t, hands=((-120, -450), hand), mouth="chew" if up else "smile", show_legs=False,
                look=(0, 1) if not up else (0, 0))
        breakfast_table(c)
        return dict(sat=0.86, warm=0.07)
    zoom(c, lt / 3, 0.05)
    kitchen_bg(c)
    c.layer = "fg"
    sip = lt > 0.3
    r.front(*CLOSE, t=t, hands=((-120, -450), (30, -690) if sip else (90, -560)), eyes="closed" if sip else "open",
            mouth="smile", show_legs=False)
    mug(c, 560 if sip else 760, 1490 if sip else 1760, 2.4)
    if sip:
        for k in range(3):
            ph = (lt * .8 + k / 3) % 1
            c.line([(500 + k * 50, 1200 - 160 * ph), (520 + k * 50, 1140 - 160 * ph)], 5, (246, 246, 246))
    return dict(sat=0.86, warm=0.08)


# ================================================================ 09:30 training
def pitch_bg(c, t, speed=0.0, horizon=1060, crowd=False, sky=((150, 176, 200), (214, 214, 206))):
    grad(c, sky[0], sky[1], 0, horizon)
    c.layer = "bg"
    if crowd:
        R(c, -50, horizon - 380, 1130, horizon, (70, 72, 84), ol=False)
        rng = np.random.default_rng(3)
        off = (t * speed * .25) % 60
        cols = [(200, 170, 70), (60, 60, 66), (180, 70, 60), (90, 110, 150), (220, 210, 200)]
        for row in range(7):
            for k in range(22):
                x = (k * 60 - off + row * 23) % 1200 - 60
                jump = 6 if (int(t * 8) + k + row) % 5 == 0 else 0
                E(c, x, horizon - 350 + row * 50 - jump, 16, 16, cols[(k * 3 + row) % 5], ol=False, n=10)
    else:
        for k in range(8):
            x = (k * 170 - t * speed * .2) % 1300 - 100
            E(c, x, horizon - 60, 90, 120, (96, 128, 96), ol=False)
        R(c, -50, horizon - 30, 1130, horizon, (120, 120, 126), ol=False)
    c.layer = "mid"
    R(c, -50, horizon, 1130, 2600, (98, 140, 82), ol=False)
    for k in range(10):
        x = (k * 240 - t * speed) % 2400 - 400
        P(c, [(x, horizon), (x + 120, horizon), (x + 320, 2600), (x + 80, 2600)], (108, 150, 90), ol=False)
    L_(c, [(-50, 1880), (1130, 1880)], 8, (236, 236, 228))


def cone(c, x, y):
    P(c, [(x - 30, y), (x + 30, y), (x + 8, y - 70), (x - 8, y - 70)], (236, 140, 60))


def training(c, t, L, cues):
    i, lt = shots(t, [L / 3, 2 * L / 3])
    if i == 0:                                                        # side view sprint
        pitch_bg(c, t, speed=900)
        for k in range(4):
            cone(c, (k * 300 - t * 900) % 1400 - 100, 1860)
        c.layer = "fg"
        hero(c, "train").side(*SIDE, t=t, **run_pose(t, 2.0), mouth="open")
        for k in range(5):
            L_(c, [(120 - k * 10, 900 + k * 120), (300 - k * 10, 900 + k * 120)], 4, (230, 236, 230))
        return dict(sat=0.86, warm=0.03)
    if i == 1:                                                        # cross (Flanke), slight low angle
        zoom(c, lt / 2, 0.05)
        pitch_bg(c, t)
        c.layer = "fg"
        p = min(1, lt / 1.0)
        foot = [0, 0]
        hero(c, "train").side(*SIDE, t=t, **kick_pose(p), ball_foot=foot)
        if p < 0.55:
            ball(c, 680, 1795, 34)
        else:
            k = (lt - 0.55) / 1.2
            ball(c, 680 + 900 * k, 1795 - 900 * k + 700 * k * k, 34, rot=lt * 500)
        return dict(sat=0.86, warm=0.03)
    pitch_bg(c, t, speed=500)                                        # duel shoulder to shoulder
    c.layer = "fg"
    push = 10 * math.sin(lt * 9)
    mate(c, "14", outfit="train").side(380 + push, 1760, 1.8, t=t + .3, **run_pose(t + .3, 1.8))
    P(c, [(300, 900), (460, 900), (480, 1300), (280, 1300)], (240, 140, 60))          # orange training bib
    hero(c, "train").side(SIDE[0] + 40 - push, SIDE[1], SIDE[2], t=t, **run_pose(t, 1.8), mouth="flat")
    ball(c, 760, 1800, 34, rot=t * 400)
    return dict(sat=0.86, warm=0.03)


# ================================================================ 12:00 canteen
def canteen_bg(c):
    grad(c, (200, 204, 200), (176, 178, 172))
    c.layer = "bg"
    for k in range(3):
        R(c, 80 + k * 330, 240, 340 + k * 330, 700, (220, 230, 236))
        R(c, 80 + k * 330, 240, 340 + k * 330, 270, (160, 166, 170), ol=False)
    c.layer = "mid"


def tray_food(c, x, y, s=1.0):
    R(c, x - 230 * s, y - 20 * s, x + 230 * s, y + 70 * s, (200, 204, 210))
    E(c, x - 120 * s, y, 70 * s, 26 * s, (248, 246, 238))                            # rice
    P(c, [(x - 20 * s, y - 10 * s), (x + 70 * s, y - 24 * s), (x + 90 * s, y + 10 * s), (x, y + 20 * s)], (206, 150, 90))
    for k in range(3):                                                                 # broccoli
        E(c, x + 150 * s + k * 26 * s, y - 6 * s, 20 * s, 18 * s, (90, 150, 80), n=12)


def canteen(c, t, L, cues):
    i, lt = shots(t, [L * 0.55])
    if i == 0:
        zoom(c, lt / 3, 0.04)
        canteen_bg(c)
        mate(c, "21", hair=(60, 40, 30), outfit="train").front(150, 2400, 2.4, t=t, show_legs=False,
                                                             hands=((-120, -460), (60, -560)), mouth="smile")
        c.layer = "fg"
        up = int(t * 1.3) % 2
        hero(c, "train").front(*MED, t=t, hands=((-120, -450), (40, -730) if up else (70, -470)),
                               mouth="chew" if up else "smile", show_legs=False, look=(0, 1))
        R(c, -60, 1650, 1140, 2600, (176, 170, 160))
        tray_food(c, 540, 1700, 1.3)
        return dict(sat=0.85, warm=0.05)
    zoom(c, lt / 3, 0.05)
    canteen_bg(c)
    c.layer = "fg"
    hero(c, "train").front(*CLOSE, t=t, hands=((-120, -450), (120, -450)), mouth="chew" if lt < 1.2 else "grin",
                           eyes="happy" if lt > 1.2 else "open", show_legs=False)
    return dict(sat=0.85, warm=0.05)


# ================================================================ 14:00 home
def living_bg(c, tv=True):
    grad(c, (176, 168, 160), (150, 140, 132))
    c.layer = "bg"
    R(c, 700, 300, 1000, 640, (210, 206, 196))
    E(c, 140, 420, 90, 140, (110, 140, 100))                                           # plant
    R(c, 110, 540, 170, 700, (150, 110, 80))
    c.layer = "mid"
    P(c, [(-60, 1150), (1140, 1150), (1140, 2600), (-60, 2600)], (106, 112, 126))    # couch back
    R(c, -60, 1150, 1140, 1190, (124, 130, 146), ol=False)


def controller(rr, hx, hy):
    pass


def home(c, t, L, cues):
    i, lt = shots(t, [L * 0.55])
    if i == 0:
        zoom(c, lt / 3, 0.04)
        living_bg(c)
        c.layer = "fg"
        tap = int(t * 8) % 2
        hero(c, "home").front(*MED, t=t, hands=((-46 - 4 * tap, -560), (46 + 4 * tap, -560)), eyes="open",
                              brows="focused", mouth="flat", show_legs=False, look=(0, 0))
        c.rrect(420, 900, 660, 990, 40, (46, 46, 54), ol=LINE, w=1.2)                    # controller
        E(c, 470, 945, 14, 14, (80, 80, 90), n=10)
        E(c, 610, 945, 14, 14, (80, 80, 90), n=10)
        return dict(sat=0.82, tint=(0.92, 0.96, 1.08), glow=(540, 900, 900, (150, 190, 255)))
    zoom(c, lt / 3, 0.04)
    living_bg(c, tv=False)
    c.layer = "fg"
    P(c, [(-40, 760), (1120, 700), (1120, 1450), (-40, 1500)], (176, 150, 130))     # cushion
    fx, fy = head_at(560, 1000, 5.4, -70)
    hero(c, "home").front(fx, fy, 5.4, t=t, lean=-70, eyes="closed", mouth="flat", show_legs=False,
                          hands=((-120, -450), (120, -450)))
    P(c, [(-60, 1500), (1140, 1440), (1140, 2600), (-60, 2600)], (150, 130, 110))     # blanket
    for k in range(3):
        ph = (lt * .5 + k / 3) % 1
        draw_z(c, 300 + 40 * ph + k * 10, 640 - 160 * ph, 1.2 + ph)
    return dict(sat=0.8, warm=0.06)


# ================================================================ 17:00 drive + arrival
def drive(c, t, L, cues):
    i, lt = shots(t, [L * 0.48])
    if i == 0:                                                        # close-up in the car, window passing
        grad(c, (240, 180, 120), (170, 150, 150))
        c.layer = "bg"
        for k in range(6):
            x = (1200 - (t * 1400 + k * 330)) % 1500 - 200
            E(c, x, 700, 110, 170, (90, 110, 86), ol=False)
            R(c, x - 10, 760, x + 10, 900, (80, 66, 56), ol=False)
        c.layer = "mid"
        P(c, [(-60, 120), (1140, 60), (1140, 300), (-60, 360)], (50, 50, 58))          # car roof/frame
        P(c, [(-60, 1300), (1140, 1300), (1140, 2600), (-60, 2600)], (56, 56, 64))
        c.layer = "fg"
        hero(c, "hoodie").front(*CLOSE, t=t, hands=((-120, -450), (120, -450)), eyes="open", brows="focused",
                                mouth="flat", show_legs=False, headphones=True, look=(1, 0))
        return dict(sat=0.86, warm=0.1)
    zoom(c, lt / 3, 0.05)
    grad(c, (230, 170, 120), (200, 170, 150), 0, 1200)                               # stadium entrance at dusk
    c.layer = "bg"
    P(c, [(-60, 380), (1140, 300), (1140, 1300), (-60, 1300)], (120, 122, 134))
    for k in range(9):
        R(c, -40 + k * 135, 430 - k * 8, 40 + k * 135, 1300, (140, 142, 154), ol=False)
    R(c, 380, 820, 700, 1300, (60, 60, 70))
    c.layer = "mid"
    R(c, -60, 1300, 1140, 2600, (150, 146, 140), ol=False)
    for side in (-1, 1):                                              # fans at the sides
        for k in range(3):
            x = 540 + side * (450 + k * 45)
            fan = mate(c, "", hair=((40, 34, 30), (130, 90, 50), (200, 170, 120))[k], skin=((236, 204, 178), (200, 150, 112), (170, 120, 90))[k],
                       outfit="home")
            fan.o.update(shirt=(KIT_Y, KIT_B, KIT_Y)[k], shirt_s=shade((KIT_Y, KIT_B, KIT_Y)[k]))
            up = (int(t * 5) + k) % 2
            fan.front(x, 2050 + k * 40, 1.25 + k * .08, t=t, show_legs=False,
                      hands=((-120, -900 - 60 * up), (120, -900 - 60 * (1 - up))), mouth="open")
    c.layer = "fg"
    bob = 6 * abs(math.sin(t * 7))
    hero(c, "hoodie").front(MED[0], MED[1] + bob, MED[2], t=t, hands=((-110, -440), (150, -820)), eyes="open",
                            mouth="smile", show_legs=False, headphones=True)
    return dict(sat=0.86, warm=0.1)


# ================================================================ 19:30 match
def drone(c, t, lt):
    """High-angle view of the pitch; the pitch scrolls so Halbo stays centred."""
    off = lt * 260
    R(c, -50, -50, 1130, 2600, (90, 132, 78), ol=False)
    for k in range(14):
        y = (k * 180 + off) % 2520 - 300
        R(c, -50, y, 1130, y + 90, (98, 142, 86), ol=False)
    L_(c, [(440, -50), (440, 2600)], 8, (236, 236, 228))
    y0 = (900 + off) % 2520 - 300
    L_(c, [(440, y0), (1130, y0)], 8, (236, 236, 228))
    c.arc(1130, y0, 260, 260, 90, 270, 8, (236, 236, 228))
    rng = np.random.default_rng(4)
    for k in range(9):
        x, y = rng.uniform(620, 1060), (rng.uniform(0, 1900) + off * .6) % 1900
        col = KIT_Y if k % 2 else (232, 234, 240)
        E(c, x, y, 26, 18, col, n=14)
        E(c, x, y - 2, 12, 12, (60, 50, 40), ol=False, n=10)
    E(c, 540, 960, 110, 110, (255, 250, 200), ol=False, n=36)            # highlight ring under Halbo
    E(c, 540, 960, 96, 96, (90, 132, 78), ol=False, n=36)
    for k in range(4):
        L_(c, [(540, 1040 + k * 50), (540, 1066 + k * 50)], 8, (220, 230, 210))
    E(c, 540, 960, 62, 40, KIT_Y, n=18)
    E(c, 540, 960, 30, 22, KIT_B, ol=False, n=12)
    E(c, 540, 952, 28, 28, HAIR, n=14)
    ball(c, 540, 870, 18, rot=lt * 300)


def net_insert(c, lt):
    grad(c, (60, 64, 80), (120, 120, 120))
    c.layer = "mid"
    R(c, -50, 1500, 1130, 2600, (90, 132, 78), ol=False)
    bulge = 60 * max(0, 1 - abs(lt - 0.25) / 0.25)
    for k in range(-2, 16):
        L_(c, [(k * 80, 300), (k * 80 + bulge * .4, 1500)], 3, (230, 230, 230))
    for k in range(16):
        L_(c, [(-50, 300 + k * 80), (1130, 300 + k * 80 + bulge * math.sin(k / 15 * math.pi))], 3, (230, 230, 230))
    ball(c, 540, 900 + bulge, 70, rot=lt * 200)
    R(c, -50, 280, 1130, 320, WHITE)
    R(c, 20, 280, 60, 1500, WHITE)
    R(c, 1020, 280, 1060, 1500, WHITE)


def match(c, t, L, cues):
    goal = cues[1][0] - 0.15          # ball hits the net when he shouts
    b = [1.8, 3.8, 5.4, 6.6, goal - 1.0, goal + 0.7]
    i, lt = shots(t, b)
    if i == 0:
        drone(c, t, lt)
        return dict(sat=0.85, warm=0.06)
    if i == 1:                                                            # side: running down the left wing
        pitch_bg(c, t, speed=1000, crowd=True, sky=((40, 50, 80), (120, 110, 120)))
        c.layer = "fg"
        hero(c).side(*SIDE, t=t, **run_pose(t, 2.0), mouth="flat")
        ball(c, 760 + 20 * math.sin(t * 12), 1805, 32, rot=t * 600)
        return dict(sat=0.86, warm=0.05)
    if i == 2:                                                            # duel - wins the ball
        pitch_bg(c, t, speed=300, crowd=True, sky=((40, 50, 80), (120, 110, 120)))
        c.layer = "fg"
        p = min(1, lt / 1.2)
        opponent(c).side(860 + 120 * p, 1770, 1.8, t=t, flip=True, **run_pose(t + .2, 1.5, 1 - .6 * p),
                         head_rot=-15 * p)
        hero(c).side(*SIDE, t=t, **run_pose(t, 1.6), mouth="flat")
        ball(c, lerp(760, 700, p), 1805, 32, rot=t * 400)
        if 0.2 < p < 0.6:
            for k in range(5):
                L_(c, [(700 + k * 20, 1500 - k * 40), (760 + k * 30, 1480 - k * 50)], 5, (250, 250, 230))
        return dict(sat=0.86, warm=0.05)
    if i == 3:                                                            # sprint with speed lines
        pitch_bg(c, t, speed=1500, crowd=True, sky=((40, 50, 80), (120, 110, 120)))
        c.layer = "fg"
        hero(c).side(*SIDE, t=t, **run_pose(t, 2.4, 1.15), mouth="flat")
        ball(c, 790, 1805, 32, rot=t * 900)
        for k in range(10):
            y = 300 + k * 150
            L_(c, [(-20, y), (240 - (k % 3) * 60, y)], 5, (250, 250, 240))
        return dict(sat=0.86, warm=0.05)
    if i == 4:                                                            # slow motion strike: side + front angles
        dur = b[4] - b[3]
        half = dur / 2
        p = 0.35 + 0.55 * (lt / dur)            # slow progress through the kick
        if lt < half:
            pitch_bg(c, t * .2, crowd=True, sky=((40, 50, 80), (120, 110, 120)))
            c.layer = "fg"
            hero(c).side(*SIDE, t=t, **kick_pose(p), mouth="shout", brows="focused")
            bp = max(0, p - 0.6) / 0.4
            ball(c, 690 + 500 * bp, 1795 - 260 * bp, 34, rot=bp * 300)
        else:
            zoom(c, (lt - half) / half, 0.08, 540, 1100)
            grad(c, (40, 50, 80), (120, 110, 120), 0, 1200)
            c.layer = "mid"
            R(c, -50, 1200, 1130, 2600, (90, 132, 78), ol=False)
            c.layer = "fg"
            hero(c).front(*FULL, t=t, hands=((-220, -560), (200, -520)), legs=(-6, 30), mouth="shout",
                          brows="focused", lean=4)
            k = (lt - half) / half
            ball(c, 600 + 60 * k, 1700 - 500 * k, 40 + 140 * k, rot=k * 200)
        return dict(sat=0.78, warm=0.02, slowmo=True)
    if i == 5:                                                            # ball in the net
        net_insert(c, lt)
        return dict(sat=0.8, warm=0.02)
    # celebration
    zoom(c, lt / 4, 0.06)
    pitch_bg(c, t, crowd=True, sky=((40, 50, 80), (120, 110, 120)))
    for side, num, hair, skin in ((-1, "7", (30, 26, 24), (200, 150, 112)), (1, "10", (180, 150, 100), (236, 204, 178))):
        m = mate(c, num, hair=hair, skin=skin)
        m.front(540 + side * 430, 2500, 2.25, t=t, show_legs=False, hands=((-60 * side, -700), (-200 * side, -640)),
                mouth="shout", eyes="happy", lean=-side * 10)
    c.layer = "fg"
    hero(c).front(*MED, t=t, hands=((-280, -860), (280, -860)), mouth="shout", eyes="happy", brows="up",
                  show_legs=False)
    rng = np.random.default_rng(int(t * 12))
    for k in range(14):
        E(c, rng.uniform(0, 1080), rng.uniform(0, 900), 8, 14, (KIT_Y, (240, 240, 240), KIT_B)[k % 3], ol=False, n=8)
    return dict(sat=0.88, warm=0.06)


def lerp(a, b, k):
    return a + (b - a) * k


# ================================================================ 22:30 evening
def night(c, t, L, cues):
    i, lt = shots(t, [cues[1][0] - 0.3])
    if i == 0:                                                        # ice bath
        grad(c, (170, 190, 204), (130, 150, 166))
        c.layer = "bg"
        for y in range(0, 1400, 140):
            L_(c, [(-50, y), (1130, y)], 3, (150, 170, 186), )
        for x in range(0, 1100, 140):
            L_(c, [(x, -50), (x, 1400)], 3, (150, 170, 186))
        c.layer = "fg"
        shiver = 4 * math.sin(t * 40)
        hero(c, "bare").front(MED[0] + shiver, MED[1], MED[2], t=t, hands=((-60, -560), (60, -560)), eyes="half",
                              mouth="flat", brows="sad", show_legs=False)
        P(c, [(-60, 1400), (1140, 1400), (1140, 2600), (-60, 2600)], (196, 220, 236))   # water
        R(c, -60, 1380, 1140, 1420, (240, 242, 246))
        for k in range(5):
            P(c, [(150 + k * 190, 1440), (210 + k * 190, 1430), (220 + k * 190, 1480), (160 + k * 190, 1490)], (236, 246, 252))
        for k in range(2):
            ph = (lt * .7 + k * .5) % 1
            E(c, 600 + 60 * ph, 1000 - 120 * ph, 30 + 30 * ph, 20 + 20 * ph, (240, 244, 248), ol=False, n=14)
        return dict(sat=0.75, tint=(0.92, 0.98, 1.08))
    zoom(c, lt / 3, 0.04)
    grad(c, (60, 56, 70), (40, 38, 50))
    c.layer = "mid"
    P(c, [(-40, 700), (1120, 640), (1120, 1500), (-40, 1560)], (200, 196, 200))
    c.layer = "fg"
    hero(c, "sleep").front(540 + 748 * 5.6, 1010, 5.6, t=t, lean=-90, eyes="closed", mouth="smile",
                           show_legs=False, hands=((-100, -420), (100, -420)))
    P(c, [(-60, 1300), (1140, 1240), (1140, 2600), (-60, 2600)], (110, 104, 130))
    return dict(sat=0.75, warm=0.12, spot=(540, 1000, 900, 0.55))


FUNCS = dict(intro=intro, wake=wake, breakfast=breakfast, training=training, canteen=canteen, home=home,
             drive=drive, match=match, night=night)
