"""Scenes of 'Ein Tag als K-Pop-Star … mit Halbo!'.

Clean TikTok layout: Halbo always big in the centre, max 2-3 other characters,
one clear action per scene. No text on screen except the intro signs and the
clock sign (and never both at once). Every scene function receives
(ctx, local time, scene length, local cue times) and returns a colour look.
"""
import math

import numpy as np

from kscast import *  # noqa: F401,F403
from paper import INK

ID = (540, 960, 1.0)
STAGE = dict(sat=1.15, tint=(1.04, 0.98, 1.06))
GREY = dict(sat=0.42, tint=(0.86, 0.93, 1.08))
POSES = [((150, 30), (25, -15)), ((30, 150), (-15, 25)), ((100, 100), (0, 0)), ((170, 170), (20, -20))]
S = 1.85           # Halbo's size: big in the centre
FEET = 1790


def frames_since(t, a):
    return int((t - a) * 12 + 1e-6)


# ============================================================ INTRO: one sign at a time
SIGN_WINDOWS = [  # start, end, w, h, paper, ink, text, size
    (0.0, 1.0, 600, 200, (250, 247, 238), INK, "EIN TAG", 132),
    (1.0, 2.5, 900, 200, PINK, (255, 255, 255), "ALS K-POP-STAR", 104),
    (2.5, 99, 720, 220, (214, 40, 60), (255, 255, 255), "mit Halbo!", 132),
]
SIGN_Y = 640


def _torn(w, h, seed):
    r = np.random.default_rng(seed)
    pts = [(x, -h / 2 + r.uniform(-9, 9)) for x in np.linspace(-w / 2, w / 2, 24)]
    pts += [(w / 2 + r.uniform(-10, 10), y) for y in np.linspace(-h / 2, h / 2, 8)[1:]]
    pts += [(x, h / 2 + r.uniform(-9, 9)) for x in np.linspace(w / 2, -w / 2, 24)[1:]]
    pts += [(-w / 2 + r.uniform(-10, 10), y) for y in np.linspace(h / 2, -h / 2, 8)[1:-1]]
    return pts


def intro(c, t, L, cues):
    c.cam = ID
    simple_stage(c, t)
    c.layer = "fg"
    pose = t >= 2.75
    if pose:
        star_girl(c, 540, FEET, S, rot=-5, outfit="jacket", arms=(30, 165), eyes="happy", mouth="grin", legs=(-10, 12))
        for k in range(5):
            a = k * 2 * math.pi / 5 + t * 2
            star(c, 540 + math.cos(a) * 300, 1350 + math.sin(a) * 260, 18 + 6 * math.sin(t * 9 + k), (255, 240, 150), w=4)
    else:
        wave = 120 + 30 * math.sin(t * 9)
        star_girl(c, 540, FEET, S, outfit="jacket", arms=(15, wave), eyes="dot", mouth="smile",
                  bounce=-10 * (int(t * 4) % 2))
    # exactly one sign at a time; each vanishes one frame before the next appears
    c.layer = "ui"
    for i, (a, b, w, h, paper, ink, txt, size) in enumerate(SIGN_WINDOWS):
        if a <= t < b - 0.09:
            k = frames_since(t, a)
            s = (1.6, 0.92, 1.04)[k] if k < 3 else 1.0
            c.push(540, SIGN_Y, s, (-3, 2, -2)[i])
            c.poly(_torn(w, h, 31 + i), paper, w=6)
            c.pop()
            c.push(540, SIGN_Y, s, 0)
            c.text(0, 4, txt, size, fill=ink, stroke=5 if i else 0, stroke_fill=INK)
            c.pop()
            if i == 2:
                for k2 in range(6):
                    ang = k2 * 2 * math.pi / 6 + t * 1.5
                    tw = 0.6 + 0.4 * math.sin(t * 9 + k2 * 2)
                    star(c, 540 + math.cos(ang) * 440, SIGN_Y + math.sin(ang) * 170, 20 * tw + 6, (255, 236, 120), w=4)
            break
    c.layer = "mid"
    return dict(STAGE)


# ============================================================ 05:00 van at night
def van_bg(c, t):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, 3000, (60, 64, 84), ol=None, jit=False)
    c.layer = "mid"
    c.rrect(80, 330, 1000, 900, 60, (16, 22, 52), w=8)            # big side window
    c.ell(820, 450, 40, 40, (250, 240, 200), w=4, n=18)
    c.ell(838, 438, 36, 36, (16, 22, 52), ol=None, n=18)
    for k in range(3):                                          # street lights rushing by
        x = 1100 - ((t * 900 + k * 420) % 1400)
        c.rect(x, 600, x + 26, 900, (60, 66, 90), ol=None)
        c.ell(x + 13, 590, 30, 14, (255, 220, 140), ol=None, n=12)
    c.rrect(160, 980, 920, 1700, 50, (40, 44, 60), w=7)          # seat back
    c.rrect(120, 1600, 960, 1760, 40, (52, 56, 74), w=7)         # seat
    c.rect(-400, 1760, 1500, 3000, (30, 32, 44), w=6)


def schedule(c, x, y, length):
    c.rect(x - 90, y, x + 90, y + length, (250, 248, 240), w=5)
    k = 0
    while 30 + k * 46 < length - 10:
        yy = y + 30 + k * 46
        c.rect(x - 70, yy, x - 46, yy + 22, (120, 200, 240) if k % 3 else PINK_L, w=3)
        c.line([(x - 34, yy + 11), (x + 70 - (k * 23) % 50, yy + 11)], 4, (160, 160, 170))
        k += 1


def van(c, t, L, cues):
    c.cam = ID
    van_bg(c, t)
    c.layer = "fg"
    awake = t >= 2.4
    nod = 6 * math.sin(t * 3)
    star_girl(c, 540, 1770, S, outfit="hoodie", seated=True, arms=(8, 8),
              eyes=("closed" if not awake else ("wide" if t < 3.0 else "tired")),
              mouth="flat", head_rot=(16 + nod) if not awake else 0)
    if not awake:
        zz(c, 660, 1080, t, 1.4)
    if t >= 1.4:
        mx = lerp(1250, 880, ease(seg(t, 1.4, 2.0)))
        shake = 10 * math.sin(t * 30) if 1.9 < t < 2.5 else 0
        manager(c, mx, 1900, 1.2, flip=True, arm=75 + shake if t < 2.7 else 40, arm_l=10, clipboard=False)
        if t >= 2.7:
            length = lerp(60, 1100, ease(seg(t, 2.7, 3.9)))
            schedule(c, mx - 150, 1290, length)
    c.layer = "mid"
    return dict(sat=0.5, tint=(0.62, 0.68, 0.98), spot=(540, 1300, 900, .72))


# ============================================================ 07:00 make-up room
def makeup(c, t, L, cues):
    c.cam = ID
    plain_room(c, (176, 180, 192), (150, 146, 150), floor_y=1460)
    c.rect(300, 420, 780, 960, (200, 220, 236), w=7)            # mirror with bulbs
    for k in range(5):
        for x in (270, 810):
            c.ell(x, 450 + k * 120, 18, 18, (255, 240, 190), w=3, n=12)
    c.rrect(330, 1000, 750, 1660, 40, (40, 40, 48), w=7)         # chair back
    brush = 40 + 30 * math.sin(t * 8)
    staff(c, 170, 1720, 1.15, (60, 50, 70), (90, 100, 130), arms=(10, 100 + brush * .4),
          held=lambda cc: cc.rrect(-12, 100, 12, 170, 6, (150, 110, 60), w=3))
    staff(c, 910, 1720, 1.15, (110, 70, 40), (200, 170, 150), arms=(10, 95), flip=True,
          held=lambda cc: (cc.rrect(-22, 96, 22, 170, 10, (230, 120, 170), w=4), cc.rect(-12, 160, 12, 210, (230, 120, 170), w=3)))
    for k in range(3):  # hair-dryer air
        ph = (t * 3 + k / 3) % 1
        c.line([(740 - 120 * ph, 1170 + k * 22), (700 - 120 * ph, 1170 + k * 22)], 4, (240, 240, 255))
    c.layer = "fg"
    sad = t >= cues[-1][0]
    star_girl(c, 540, 1790, S, outfit="hoodie", seated=True, arms=(10, 10), eyes="dot",
              mouth="flat" if sad else "smile", look=0 if t < cues[1][0] else 0, head_rot=8 if t >= cues[1][0] else 0)
    c.rect(-60, 1660, 1140, 1720, (210, 210, 220), w=6)          # table
    c.rect(-40, 1720, 1120, 2100, (186, 186, 198), w=6)
    c.ell(450, 1640, 80, 30, WHITE, w=5, n=20)                   # small salad
    for k, (dx, col) in enumerate(((-30, (110, 190, 80)), (0, (80, 160, 60)), (30, (130, 200, 90)))):
        c.ell(450 + dx, 1622, 26, 14, col, w=3, n=12)
    c.rect(640, 1560, 700, 1665, (210, 235, 250), w=5)           # glass of water
    c.rect(643, 1595, 697, 1662, (160, 205, 240), ol=None)
    c.layer = "mid"
    return dict(GREY)


# ============================================================ 10:00 stage -> backstage
def stage_scene(c, t, L, cues):
    c.cam = ID
    cut = cues[1][0] - 0.35
    if t < cut:
        simple_stage(c, t)
        c.layer = "fg"
        arms, legs = POSES[int(t * 3) % 4]
        star_girl(c, 540, 1650, S * .95, outfit="jacket", arms=arms, legs=legs, eyes="happy", mouth="grin",
                  bounce=-12 * (int(t * 6) % 2))
        for i, x in enumerate((200, 540, 880)):
            fan(c, x, 1990, 1.0, t, i)
        c.layer = "mid"
        return dict(STAGE)
    plain_room(c, (150, 152, 164), (120, 118, 124), floor_y=1480)
    c.rect(60, 1300, 300, 1480, (70, 70, 80), w=6)               # flight cases
    c.rect(80, 1320, 280, 1340, (150, 150, 160), w=3)
    c.rect(800, 1340, 1020, 1480, (70, 70, 80), w=6)
    c.line([(300, 1470), (520, 1500), (800, 1470)], 6, (40, 40, 48))  # cable
    c.layer = "fg"
    lt = t - cut
    br = 0.05 * math.sin(lt * 14)
    girl_sit_floor(c, 540, 1800, 2.0, outfit="jacket", eyes="tired", mouth="o", breathe=br, head_down=lt < 1.2)
    for k in range(2):
        ph = (lt * 1.6 + k * .5) % 1
        puff(c, 650 + 40 * ph, 1300 - 60 * ph, 16 + 14 * ph, (240, 240, 250))
    sweat(c, 420, 1260 + 40 * ((lt * 2) % 1))
    sweat(c, 670, 1240 + 40 * ((lt * 2 + .5) % 1))
    c.layer = "mid"
    return dict(sat=0.42, tint=(0.84, 0.92, 1.08), spot=(540, 1500, 900, .6))


# ============================================================ 14:00 manager's office
def office(c, t, L, cues):
    c.cam = ID
    plain_room(c, (160, 168, 184), (130, 128, 136), floor_y=1450)
    c.rect(120, 380, 420, 640, WHITE, w=6)                        # sign: crossed-out heart (no words)
    heart(c, 270, 515, 80, PINK, w=6)
    c.line([(170, 420), (370, 610)], 14, RED)
    c.rect(560, 380, 960, 760, (200, 214, 230), w=6)              # window with blinds
    for k in range(1, 8):
        c.line([(560, 380 + k * 47), (960, 380 + k * 47)], 4, (150, 160, 176))
    c.layer = "fg"
    manager(c, 860, 1690, 1.2, arm=55 if t < 2.2 else 15, arm_l=10, clipboard=False)
    c.poly([(560, 1440), (1120, 1440), (1160, 1560), (520, 1560)], (110, 80, 60), w=6)   # desk top
    c.rect(540, 1560, 1140, 1900, (90, 64, 48), w=6)
    p = ease(seg(t, 0.8, 1.9))
    cx = lerp(880, 650, p)
    c.poly([(cx - 130, 1452), (cx + 110, 1452), (cx + 130, 1546), (cx - 150, 1546)], (250, 248, 240), w=5)
    c.push(cx - 10, 1499, 1, 0)
    drawn_zeros(c, 0, 0, 6, 15)
    c.pop()
    look = 10 if t < cues[2][0] else 0
    eyes = "wide" if cues[1][0] <= t < cues[2][0] else "dot"
    star_girl(c, 330, 1800, S, outfit="hoodie", arms=(10, 30), eyes=eyes, mouth="flat", look=look,
              head_rot=-8 if t >= cues[2][0] else 0)
    c.layer = "mid"
    return dict(GREY)


# ============================================================ 18:00 phone in the dressing room
def phone_scene(c, t, L, cues):
    c.cam = ID
    plain_room(c, (150, 154, 168), (124, 120, 126), floor_y=1480)
    c.rect(330, 430, 750, 900, (120, 134, 150), w=7)
    for k in range(4):
        for x in (300, 780):
            c.ell(x, 470 + k * 130, 16, 16, (150, 150, 140), w=3, n=12)
    c.rect(430, 1600, 650, 1640, (70, 70, 80), w=5)               # stool
    c.rect(450, 1640, 470, 1800, (70, 70, 80), w=4)
    c.rect(610, 1640, 630, 1800, (70, 70, 80), w=4)
    c.layer = "fg"
    sad = t >= cues[1][0]
    held = lambda cc: phone(cc, -10, 116, 1.15, rot=-25, screen=(200, 235, 255))
    star_girl(c, 540, 1800, S, outfit="hoodie", seated=True, arms=(10, -38), eyes="dot", mouth="flat" if sad else "smile",
              head_rot=10, held=held)
    for k in range(9):
        born = 0.6 + k * 0.75
        p = seg(t, born, born + 2.6)
        if 0 < p < 1:
            side = -1 if k % 2 else 1
            x = 540 + side * (150 + 160 * p) + 20 * math.sin(t * 2 + k)
            y = 1440 - 640 * p
            angry_note(c, x, y, k % 5, rot=(-10, 8, -4, 12, -7)[k % 5], s=0.9 + 0.3 * p)
    c.layer = "mid"
    return dict(GREY)


# ============================================================ 23:00 practice room
def practice(c, t, L, cues, outro=False):
    c.cam = ID
    studio(c, t, dark=True)
    c.ell(540, 300, 60, 26, (230, 230, 210), w=4, a0=180, a1=360, n=16)
    c.line([(540, -100), (540, 280)], 4)
    c.layer = "fg"
    sit_t = cues[0][1] + 0.1 if cues else 0
    if outro or t >= sit_t:
        smile = outro or t >= cues[1][0] + 0.6
        girl_sit_floor(c, 540, 1800, 2.0, outfit="hoodie", eyes="dot", mouth="smile" if smile else "flat")
    else:
        arms, legs = POSES[int(t * 3) % 4]
        star_girl(c, 540, FEET, S, outfit="hoodie", arms=arms, legs=legs, eyes="dot", mouth="flat",
                  bounce=-12 * (int(t * 6) % 2))
    c.layer = "mid"
    return dict(sat=0.4, tint=(0.62, 0.68, 0.92), spot=(540, 1450, 760, .45))


def outro(c, t, L, cues):
    practice(c, t, L, cues, outro=True)
    k = ease(seg(t, 0.1, 1.6))
    if k > .3:
        c.layer = "fg"
        sparkles(c, t, int(10 * k), seed=8, area=(80, 300, 1000, 1200), col=(255, 230, 250))
        c.layer = "mid"
    return dict(sat=lerp(0.4, 0.95, k), tint=tuple(lerp(a, b, k) for a, b in zip((0.62, 0.68, 0.92), (1.02, 0.98, 1.04))),
                spot=(540, 1450, lerp(760, 1700, k), lerp(.45, .85, k)))


FUNCS = dict(intro=intro, van=van, makeup=makeup, stage=stage_scene, office=office, phone=phone_scene,
             practice=practice, outro=outro)
