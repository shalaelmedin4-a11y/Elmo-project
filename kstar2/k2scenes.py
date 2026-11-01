"""Nine scenes, one clear action each. Halbo is always drawn by popstar() with the
fixed framing (centre, knees up, ~2/3 of the frame). Backgrounds are one main
colour with 1-2 big objects; other characters stay small and at the side.
Hand targets are in Halbo's body coordinates: head centre (0,-270), mouth
(0,-234), shoulders (+-58,-196), visible down to y=-40, x within +-125.
"""
import math

import numpy as np

from k2cast import *  # noqa: F401,F403
from paper import INK

GREY = dict(sat=0.45, tint=(0.86, 0.93, 1.08))
PINK_LOOK = dict(sat=1.15, tint=(1.04, 0.98, 1.06))


def osc(t, f, a=1.0, ph=0.0):
    return a * math.sin(t * f * 2 * math.pi + ph)


def in_cue(t, cues, i, pad=0.0):
    return cues[i][0] - pad <= t < cues[i][1] + pad


# ---------------------------------------------------------------- 05:00 bed
def bed_set(c, dark=False):
    flat_bg(c, (40, 46, 74) if dark else (150, 158, 178))
    c.rrect(90, 980, 990, 2100, 60, (70, 60, 70) if dark else (120, 100, 96), w=7)        # headboard
    c.rrect(170, 1120, 910, 1560, 80, (200, 206, 220) if dark else (245, 245, 250), w=6)   # pillow


def blanket(c, col=(150, 170, 210), y=1640):
    c.poly([(-60, y + 20), (300, y - 10), (700, y + 10), (1140, y - 20), (1140, 2100), (-60, 2100)], col, w=7)
    for k in range(4):
        c.line([(120 + k * 240, y + 40), (60 + k * 260, 2000)], 4, tuple(max(0, v - 35) for v in col))


def bed(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    bed_set(c)
    up = ease(seg(t, 0.0, 0.8))
    tap = int(t * 4) % 2
    manager_side(c, 990, 2080, 2.0, flip=True, arm=60 + 25 * tap, arm_l=70, clipboard=False,
                 held=lambda cc: cc.ell(0, 120, 14, 9, (230, 210, 120), w=3, n=10))
    c.layer = "fg"
    rub = t < 2.6
    popstar(c, t, "hoodie", hands=((-26 + osc(t, 3, 4), -262) if rub else (-70, -60), (75, -55)),
            eyes="tired", mouth="flat", brows="sad", sway=-12 * (1 - up), bob=10 * (1 - up), head_rot=-4 * (1 - up))
    blanket(c)
    c.layer = "mid"
    return dict(GREY)


# ---------------------------------------------------------------- 06:00 kitchen
def scale_prop(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rrect(-110, -120, 110, 120, 30, (240, 240, 245), w=6)
    c.ell(0, -40, 60, 60, WHITE, w=5, n=24)
    a = math.radians(-60)
    c.line([(0, -40), (math.cos(a) * 46, -40 + math.sin(a) * 46)], 6, RED)
    c.rect(-70, 50, 70, 80, (200, 200, 210), w=4)
    c.pop()


def kitchen(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (156, 168, 182))
    c.rect(660, 380, 980, 700, (210, 222, 236), w=7)                       # small window
    c.line([(820, 380), (820, 700)], 5)
    manager_side(c, 120, 2000, 1.55, arm=110, arm_l=110, clipboard=False)
    scale_prop(c, 120, 1150, 1.0)
    c.layer = "fg"
    worry = t >= cues[2][0]
    fork_y = -95 + osc(t, 1.5, 6)

    def fork(cc, hx, hy):
        cc.line([(hx, hy), (hx - 18, hy + 34)], 5, (190, 196, 204))
        for k in range(3):
            cc.line([(hx - 18 + (k - 1) * 4, hy + 34), (hx - 20 + (k - 1) * 4, hy + 46)], 2, (190, 196, 204))
    popstar(c, t, "hoodie", hands=((-70, -92), (52, fork_y)), held=(None, fork),
            eyes="sad" if worry else "open", mouth="flat", brows="sad" if worry else "calm",
            look=(-1, 0) if worry else (0, 1))
    c.rect(-60, 1720, 1140, 1770, (176, 150, 120), w=6)                    # table
    c.rect(-60, 1770, 1140, 2100, (150, 124, 96), w=6)
    c.ell(540, 1735, 230, 52, WHITE, w=6, n=30)                           # big plate
    c.ell(540, 1735, 170, 36, (236, 236, 240), w=3, n=26)
    for dx, col in ((-14, (110, 190, 80)), (6, (80, 160, 60)), (20, (140, 205, 95))):
        c.ell(540 + dx, 1728, 14, 8, col, w=3, n=10)                     # tiny salad
    c.layer = "mid"
    return dict(GREY)


# ---------------------------------------------------------------- 08:00 make-up
def makeup(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (172, 168, 186))
    c.rect(130, 330, 950, 1500, (196, 214, 230), w=8)                     # big mirror
    for k in range(6):
        for x in (100, 980):
            c.ell(x, 380 + k * 210, 24, 24, (255, 240, 190), w=4, n=14)
        c.ell(200 + k * 136, 300, 24, 24, (255, 240, 190), w=4, n=14)
    staff(c, 990, 2000, 1.5, (60, 50, 70), (200, 170, 150), arms=(10, 120), flip=True)
    c.layer = "fg"
    yawn = (1.0 <= t < 2.2) or (3.4 <= t < 4.4)
    popstar(c, t, "hoodie", hands=((-60, -60), (8, -232) if yawn else (62, -60)),
            eyes="closed" if yawn else "tired", mouth="yawn" if yawn else "flat", brows="calm",
            head_rot=-6 if yawn else 0)
    bx = 905 + osc(t, 2.2, 14)                                           # brush at the hair edge
    c.rrect(bx - 14, 1060, bx + 14, 1180, 8, (150, 110, 60), w=4)
    c.rrect(bx - 26, 1010, bx + 26, 1070, 10, (90, 70, 60), w=4)
    c.layer = "mid"
    return dict(GREY)


# ---------------------------------------------------------------- 11:00 dance studio
DANCE = [((-110, -320), (110, -130)), ((-110, -130), (110, -320)), ((-120, -210), (120, -210)), ((-60, -330), (60, -330))]


def dance(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (150, 162, 184))
    c.rect(40, 300, 1040, 1700, (186, 210, 230), w=8)                    # big mirror
    for k in range(1, 3):
        c.line([(40 + k * 333, 300), (40 + k * 333, 1700)], 6)
    for k in range(3):
        x = 140 + k * 333
        c.poly([(x, 340), (x + 50, 340), (x - 70, 700), (x - 120, 700)], (226, 240, 252), ol=None)
    c.rect(40, 1240, 1040, 1262, (130, 130, 140), w=4)                   # barre
    c.layer = "fg"
    wipe_t = cues[1][0] - 0.2
    if t < wipe_t:
        k = int(t * 3) % 4
        popstar(c, t, "hoodie", hands=DANCE[k], eyes="open", mouth="flat", brows="calm",
                sway=(-4, 4, 0, 0)[k], bob=-4 * (int(t * 6) % 2))
        for i in range(4):
            ph = (t * 1.6 + i * .25) % 1
            sweat_drop(c, 540 + (i - 1.5) * 260 * ph * 1.4, 760 - 200 * ph + 380 * ph * ph)
    else:
        lt = t - wipe_t
        hx = 40 - 70 * min(1, (lt % 1.6) / 0.8)
        popstar(c, t, "hoodie", hands=((-95, -95), (hx, -305)), eyes="tired", mouth="o" if lt < 1 else "flat",
                brows="sad", head_rot=-4)
        sweat_drop(c, 360, 1000 + 40 * ((lt * 2) % 1))
        sweat_drop(c, 720, 960 + 40 * ((lt * 2 + .5) % 1))
    c.layer = "mid"
    return dict(GREY)


# ---------------------------------------------------------------- 13:00 recording studio
def studio(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (110, 120, 146))
    c.rect(60, 330, 1020, 1250, (150, 180, 206), w=8)                    # big window to the control room
    shake = 12 * math.copysign(1, osc(t, 2.2)) if t > 1.0 else 0
    manager_side(c, 900, 1240, 1.05, flip=True, arm=20, arm_l=40, head_rot=shake)
    c.rect(-400, 1250, 1500, 3000, (110, 120, 146), w=6)                 # wall under the window
    c.rect(60, 1250, 1020, 1280, (90, 96, 120), w=5)
    c.line([(560, 340), (420, 760)], 5, (200, 222, 240))
    c.layer = "fg"
    popstar(c, t, "hoodie", hands=((-64, -262), (62, -60)), eyes="closed" if (int(t) % 3 == 0) else "open",
            mouth="o", brows="up", headphones=True)
    c.line([(110, 2100), (300, 1260)], 14, (70, 70, 80))                 # big mic on a stand
    c.line([(300, 1260), (360, 1150)], 10, (70, 70, 80))
    c.push(360, 1080, 1, 20)
    c.rrect(-46, -90, 46, 70, 40, (90, 92, 104), w=6)
    for k in range(5):
        c.line([(-36, -60 + k * 26), (36, -60 + k * 26)], 3, (150, 152, 164))
    c.pop()
    for k in range(2):
        ph = (t * .7 + k * .5) % 1
        note_shape(c, 260 - 60 * ph, 900 - 300 * ph, 1.2)
    c.layer = "mid"
    return dict(sat=0.5, tint=(0.84, 0.92, 1.1))


# ---------------------------------------------------------------- 16:00 fan meeting
def fans(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (255, 150, 200))
    sparkles(c, t, 8, seed=6, area=(220, 120, 1040, 700), col=(255, 250, 230))
    fan(c, 110, 1520, 1.25, t, 0)
    c.layer = "fg"
    tired = t >= cues[2][0]
    if t < 0.9:
        hands = ((-70, -70), (100, -260 + osc(t, 3, 12)))
    else:
        hands = ((-14, -150), (14, -150))
    popstar(c, t, "jacket", hands=hands, eyes="tired" if tired else "happy", mouth="smile",
            brows="sad" if tired else "calm")
    if t >= 0.9:
        heart(c, 540, 1395 - 6 * (int(t * 4) % 2), 54, PINK, w=6)
    c.rect(-60, 1730, 1140, 1790, WHITE, w=6)                            # table
    c.rect(-60, 1790, 1140, 2100, (255, 200, 225), w=6)
    c.rect(700, 1690, 900, 1745, (255, 236, 160), w=4)                   # poster to sign
    c.line([(640, 1720), (700, 1680)], 7, (60, 60, 70))
    c.layer = "mid"
    return dict(PINK_LOOK)


# ---------------------------------------------------------------- 19:00 concert
def concert(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    bands(c, [(70, 20, 120), (110, 30, 150), (160, 45, 175), (210, 70, 180), (250, 110, 195)], 0, 1700)
    c.layer = "bg"
    c.poly([(470, -50), (610, -50), (900, 1900), (180, 1900)], (255, 200, 236), ol=None)   # spotlight
    c.layer = "mid"
    sparkles(c, t, 8, seed=2, area=(240, 300, 1040, 900), col=(255, 250, 220))
    c.layer = "fg"
    k = int(t * 2) % 2

    def mic(cc, hx, hy):
        cc.rrect(hx - 9, hy - 10, hx + 9, hy + 40, 6, (60, 60, 70), w=3)
        cc.ell(hx, hy - 18, 14, 14, (150, 150, 160), w=3, n=12)
    popstar(c, t, "jacket", hands=((-115 if k else -90, -330 if k else -250), (26, -226)), held=(None, mic),
            eyes="happy" if int(t * 1.5) % 2 else "open", mouth="open", brows="up", sway=3 * (1 if k else -1),
            bob=-3 * (int(t * 4) % 2))
    cols = [(120, 255, 200), (255, 120, 210), (150, 180, 255), (255, 240, 120)]
    for i in range(9):                                                   # light sticks at the bottom edge
        x = 60 + i * 120
        a = 14 * osc(t, 1.2, 1, i)
        tx, ty = x + math.sin(math.radians(a)) * 110, 1920 - math.cos(math.radians(a)) * 110
        c.line([(x, 1960), (tx, ty)], 14, (50, 50, 60))
        c.ell(tx, ty, 18, 26, cols[i % 4], w=4, n=14)
    c.layer = "mid"
    return dict(PINK_LOOK)


# ---------------------------------------------------------------- 23:00 office
def office(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    flat_bg(c, (146, 156, 176))
    c.rect(740, 330, 1010, 560, WHITE, w=6)                              # crossed-out heart
    heart(c, 875, 450, 74, PINK, w=6)
    c.line([(780, 360), (970, 535)], 14, RED)
    manager_side(c, 975, 1980, 1.55, flip=True, arm=60 if t < 1.6 else 20, arm_l=10, clipboard=False)
    c.layer = "fg"
    sad = t >= cues[1][0]
    dating = t >= cues[2][0]
    popstar(c, t, "hoodie", hands=((-75, -82), (75, -82)), eyes="sad" if sad else "open", mouth="flat",
            brows="sad" if sad else "calm", look=(1, -1) if dating else (0, 1))
    c.rect(-60, 1700, 1140, 1760, (110, 80, 60), w=6)                    # desk
    c.rect(-60, 1760, 1140, 2100, (90, 64, 48), w=6)
    p = ease(seg(t, 0.6, 1.6))
    cx = lerp(1000, 560, p)
    c.poly([(cx - 200, 1600), (cx + 180, 1600), (cx + 200, 1740), (cx - 220, 1740)], (250, 248, 240), w=6)
    c.push(cx, 1670, 1, 0)
    drawn_zeros(c, 0, 0, 6, 24)
    c.pop()
    c.layer = "mid"
    return dict(GREY)


# ---------------------------------------------------------------- 01:00 night
def night(c, t, L, cues):
    c.cam = (540, 960, 1.0)
    bed_set(c, dark=True)
    c.ell(880, 420, 46, 46, (250, 240, 200), w=4, n=18)                 # moon in the dark
    c.ell(898, 408, 42, 42, (40, 46, 74), ol=None, n=18)
    c.layer = "fg"
    away = t >= cues[2][0] - 0.8
    if not away:
        popstar(c, t, "hoodie", hands=((-24, -168), (24, -168)), eyes="tired", mouth="flat", brows="sad",
                look=(0, 1), sway=-5, skin=(176, 204, 246))
        c.rrect(470, 1260, 610, 1330, 14, (30, 30, 36), w=5)            # phone (screen faces her)
        c.rect(480, 1268, 600, 1322, (140, 200, 255), ol=None)
    else:
        lt = t - (cues[2][0] - 0.8)
        popstar(c, t, "hoodie", hands=((-70, -60), (70, -60)), eyes="tired" if lt < 0.6 else "open",
                mouth="smile", brows="calm", look=(0, 0))
        c.rrect(930, 1500, 1010, 1640, 14, (30, 30, 36), w=5)           # phone put away
    blanket(c, (90, 100, 150), 1620)
    c.layer = "mid"
    if not away:
        return dict(sat=0.5, tint=(0.5, 0.58, 0.92), spot=(540, 1150, 700, .35))
    return dict(sat=0.5, tint=(0.62, 0.66, 0.9), spot=(540, 1150, 900, .5))


# ---------------------------------------------------------------- INTRO
from ksscenes import _torn  # noqa: E402  (torn-paper outline)

INTRO_SIGNS = [  # paper, ink, text, size, width
    ((250, 247, 238), INK, "EIN TAG IM LEBEN", 100, 960),
    (PINK, (255, 255, 255), "EINES K-POP-STARS", 100, 1000),
    ((214, 40, 60), (255, 255, 255), "mit Halbo!", 128, 720),
]
SIGN_Y = 400


def intro(c, t, L, cues):
    """Pink stage, Halbo big in the centre; three paper signs, strictly one at a time."""
    c.cam = (540, 960, 1.0)
    bands(c, [(70, 20, 120), (110, 30, 150), (160, 45, 175), (210, 70, 180), (250, 110, 195)], 0, 1700)
    c.layer = "bg"
    c.poly([(470, -50), (610, -50), (900, 1900), (180, 1900)], (255, 200, 236), ol=None)
    c.layer = "mid"
    sparkles(c, t, 8, seed=12, area=(60, 620, 1020, 1100), col=(255, 250, 220))
    (a1, e1), (a2, _) = cues[0], cues[1]
    windows = [(0.0, a1 + 0.45 * (e1 - a1)), (a1 + 0.45 * (e1 - a1), a2), (a2, L + 1)]
    c.layer = "fg"
    pose = t >= a2 + 0.2
    if pose:
        popstar(c, t, "jacket", hands=((-118, -330), (40, -250)), eyes="happy", mouth="grin", brows="up", sway=-3)
    else:
        popstar(c, t, "jacket", hands=((-75, -70), (110, -270 + osc(t, 2.5, 14))), eyes="open", mouth="smile",
                brows="up", bob=-3 * (int(t * 4) % 2))
    c.layer = "ui"
    for i, (wa, wb) in enumerate(windows):
        if wa <= t < wb - 0.09:        # one sign at a time, one empty frame between signs
            paper, ink, txt, size, w = INTRO_SIGNS[i]
            k = int((t - wa) * 12 + 1e-6)
            sc = (1.6, 0.92, 1.04)[k] if k < 3 else 1.0
            c.push(540, SIGN_Y, sc, (-3, 2, -2)[i])
            c.poly(_torn(w, 200, 41 + i), paper, w=6)
            c.pop()
            c.push(540, SIGN_Y, sc, 0)
            c.text(0, 4, txt, size, fill=ink, stroke=5 if i else 0, stroke_fill=INK)
            c.pop()
            if i == 2:
                for k2 in range(6):
                    ang = k2 * 2 * math.pi / 6 + t * 1.5
                    tw = 0.6 + 0.4 * math.sin(t * 9 + k2 * 2)
                    star(c, 540 + math.cos(ang) * 430, SIGN_Y + math.sin(ang) * 170, 20 * tw + 6, (255, 236, 120), w=4)
            break
    c.layer = "mid"
    return dict(PINK_LOOK)


FUNCS = dict(intro=intro, bed=bed, kitchen=kitchen, makeup=makeup, dance=dance, studio=studio, fans=fans, concert=concert,
             office=office, night=night)
