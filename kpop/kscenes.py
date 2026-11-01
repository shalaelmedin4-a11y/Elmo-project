"""Scenes of 'Ein Tag als K-Pop Trainee … mit Halbo!' (~52 s, 9:16).

Every scene function gets the scene-local time and returns a 'look':
  sat  - colour saturation (stage > 1, behind the scenes < 1)
  tint - RGB multiplier (pink/warm on stage, cold blue behind the scenes)
  spot - optional (x, y, radius, dark_level) light pool for the dark scenes
"""
import math

import numpy as np

from kcast import *  # noqa: F401,F403
from paper import INK

ID = (540, 960, 1.0)
STAGE_LOOK = dict(sat=1.18, tint=(1.04, 0.98, 1.06))
GREY_LOOK = dict(sat=0.42, tint=(0.86, 0.93, 1.08))


def mix_look(a, b, k):
    return dict(sat=lerp(a["sat"], b["sat"], k), tint=tuple(lerp(x, y, k) for x, y in zip(a["tint"], b["tint"])),
                spot=b.get("spot") if k > .5 else a.get("spot"))


# ============================================================ INTRO
SIGNS = [  # land time, y, w, h, paper, ink, text, size
    (0.35, 520, 560, 190, (250, 247, 238), INK, "EIN TAG", 128),
    (1.00, 760, 960, 190, PINK, (255, 255, 255), "ALS K-POP TRAINEE", 96),
    (2.50, 1010, 700, 210, (214, 40, 60), (255, 255, 255), "mit Halbo!", 128),
]


def _torn(w, h, seed):
    r = np.random.default_rng(seed)
    pts = [(x, -h / 2 + r.uniform(-9, 9)) for x in np.linspace(-w / 2, w / 2, 24)]
    pts += [(w / 2 + r.uniform(-10, 10), y) for y in np.linspace(-h / 2, h / 2, 8)[1:]]
    pts += [(x, h / 2 + r.uniform(-9, 9)) for x in np.linspace(w / 2, -w / 2, 24)[1:]]
    pts += [(-w / 2 + r.uniform(-10, 10), y) for y in np.linspace(h / 2, -h / 2, 8)[1:-1]]
    return pts


def slam_signs(c, t, signs):
    shake = 0
    for land, *_ in signs:
        if 0 <= t - land < 0.17:
            shake = 10 if int((t - land) * 12) % 2 == 0 else -10
    c.cam = (540 + shake, 960, 1.0)
    c.layer = "ui"
    for i, (land, y, w, h, paper, ink, txt, size) in enumerate(signs):
        if t < land - 0.17:
            continue
        p = (t - land) / 0.17
        s = 2.0 + (-p) * 1.2 if p < 0 else (0.92 if p < 1 else (1.04 if p < 2 else 1.0))
        c.push(540, y, s, (-3, 2, -2)[i])
        c.poly(_torn(w, h, 21 + i), paper, w=6)
        c.pop()
        c.push(540, y, s, 0)
        c.text(0, 4, txt, size, fill=ink, stroke=5 if i else 0, stroke_fill=INK)
        c.pop()
        if 0 <= p < 2:
            for k in range(4):
                a = k * math.pi / 2 + .6
                puff(c, 540 + math.cos(a) * (w / 2 + 20), y + math.sin(a) * (h / 2 + 10), 18, (255, 240, 250))
        if i == 2:
            for k in range(8):
                a = k * 2 * math.pi / 8 + t * 1.5
                tw = 0.6 + 0.4 * math.sin(t * 9 + k * 2)
                star(c, 540 + math.cos(a) * 430, y + math.sin(a) * 170, 20 * tw + 6, (255, 236, 120), w=4)
    c.layer = "mid"
    return shake


def intro(c, t):
    c.cam = ID
    stage(c, t)
    c.layer = "fg"
    for i, x in enumerate((140, 940)):  # other trainees stretching at the side
        trainee(c, x, 1600, .8, hair=HAIRS[i + 1], hoodie=HOODIES[i], arms=(160, 160) if int(t * 3) % 2 else (100, 100),
                mouth="smile")
    shake = slam_signs(c, t, SIGNS)
    c.cam = (540 + shake, 960, 1.0)
    if t >= 2.9:
        p = (t - 2.9) / 0.25
        y = 2300 if p < 1 else (1800 if p < 2 else 1840)
        cute = t >= 3.2
        c.layer = "fg"
        trainee(c, 540, y, 1.45, hero=True, arms=(150, 150) if cute else (60, 60), eyes="happy" if cute else "wide",
                mouth="grin" if cute else "o")
        if cute:
            heart(c, 540, y - 560, 46, PINK)
            star(c, 380, y - 450, 20, (255, 240, 150))
            star(c, 700, y - 470, 16, (255, 240, 150))
    c.layer = "mid"
    return dict(STAGE_LOOK)


# ============================================================ 06:00 dorm
def bunk3(c, x, w=430, floor=1650, levels=(620, 1010, 1400)):
    col = (130, 136, 150)
    for sx in (-1, 1):
        c.rect(x + sx * w / 2 - 12, 380, x + sx * w / 2 + 12, floor, col, w=4)
    for y in levels:
        c.rect(x - w / 2, y, x + w / 2, y + 34, (225, 222, 214), w=4)
        c.rect(x - w / 2, y + 34, x + w / 2, y + 52, col, w=4)


DORM = [(270, 620), (810, 620), (270, 1010), (810, 1010), (810, 1400)]  # others; Halbo = (270, 1400)


def dorm_bg(c):
    plain_room(c, (160, 166, 180), (150, 140, 130), floor_y=1520)
    c.rect(450, 120, 630, 330, (210, 220, 235), w=6)
    c.line([(540, 120), (540, 330)], 5)
    bunk3(c, 270)
    bunk3(c, 810)


def phone_box(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-90, -70), (90, -70), (80, 60), (-80, 60)], (196, 160, 110), w=5)
    c.text(0, -5, "HANDYS", 30, fill=INK)
    c.pop()


def scene1(c, t):
    if t < 3.6:
        c.cam = ID
        dorm_bg(c)
        c.layer = "fg"
        for i, (x, y) in enumerate(DORM):
            sleeper_k(c, x, y, 1.15, hair=HAIRS[i], blanket=(150, 160, 190))
            zzz(c, x - 120, y - 70, t + i * .3, 1.0)
        sleeper_k(c, 270, 1400, 1.15, hair=BLOND, blanket=(220, 160, 190), hero=True)
        mx = lerp(1250, 960, ease(seg(t, 0, 1.0)))
        manager(c, mx, 1880, 1.0, flip=True, arm=60, arm_l=60, clipboard=False)
        phone_box(c, mx - 40, 1700, 1.0)
        for i, (x, y) in enumerate(DORM):
            p = seg(t, 1.0 + i * .45, 1.5 + i * .45)
            if 0 < p < 1:
                phone(c, lerp(x + 60, mx - 40, p), lerp(y - 40, 1640, p) - 220 * math.sin(math.pi * p), 1.2, rot=360 * p)
    else:
        lt = t - 3.6
        c.cam = (520, 1350, 1.3)
        dorm_bg(c)
        c.layer = "fg"
        sleeper_k(c, 810, 1010, 1.15, hair=HAIRS[3])
        sleeper_k(c, 810, 1400, 1.15, hair=HAIRS[4])
        zzz(c, 690, 1330, t, 1.0)
        given = lt > 1.6
        held = None if given else (lambda cc: phone(cc, 0, 110, 1.1))
        trainee(c, 330, 1760, 1.15, hero=True, arms=(15, 70 if not given else 15), eyes="dot",
                mouth="flat", held=held, look=8 if not given else 0)
        manager(c, 760, 1800, .95, flip=True, arm=50, arm_l=60, clipboard=False)
        phone_box(c, 640, 1650, .9)
        if 1.2 < lt < 1.7:
            p = seg(lt, 1.2, 1.7)
            phone(c, lerp(420, 640, p), lerp(1630, 1600, p) - 120 * math.sin(math.pi * p), 1.1, rot=300 * p)
        if lt > 3.2:
            c.text(330, 1210, "...", 70, fill=WHITE, stroke=5, stroke_fill=INK)
    c.layer = "mid"
    return dict(GREY_LOOK)


# ============================================================ 07:00 weighing
def tiles_bg(c):
    plain_room(c, (190, 200, 210), (170, 176, 186), floor_y=1450)
    c.layer = "bg"
    for y in range(0, 1450, 90):
        c.line([(-100, y), (1200, y)], 2, (170, 180, 192), jit=False)
    c.layer = "mid"


def scale(c, x, y, txt, red=False):
    c.rrect(x - 110, y - 30, x + 110, y + 10, 12, (230, 232, 238), w=5)
    c.rect(x - 70, y - 120, x + 70, y - 60, (40, 44, 52), w=5)
    c.line([(x, y - 60), (x, y - 30)], 8, (160, 160, 170))
    c.text(x, y - 90, txt, 40, fill=(255, 80, 80) if red else (120, 255, 160))


def scene2(c, t):
    if t < 3.7:
        c.cam = ID
        tiles_bg(c)
        c.layer = "fg"
        for i, x in enumerate((80, 220, 360)):
            trainee(c, x, 1660, .95, hair=HAIRS[i + 1], hoodie=HOODIES[i], arms=(10, 10), mouth="flat",
                    eyes="wide" if i == 2 else "dot", look=6)
        weight = "48.6" if t < 1.2 else "49.1"
        scale(c, 590, 1800, weight, red=t >= 1.2)
        trainee(c, 590, 1770, 1.1, hero=True, arms=(10, 10), eyes="wide" if t > 1.2 else "dot",
                mouth="o" if t > 1.2 else "flat", look=10)
        shake = 10 * math.copysign(1, math.sin(t * 9)) if 1.5 < t < 3.4 else 0
        manager(c, 920, 1900, 1.0, flip=True, arm=70, arm_l=40, head_rot=shake)
        if t > 1.3:
            sweat(c, 500, 1330)
    else:
        lt = t - 3.7
        c.cam = (540, 1400, 1.2)
        tiles_bg(c)
        for i, x in enumerate((180, 900)):
            trainee(c, x, 1600, .95, hair=HAIRS[i + 2], hoodie=HOODIES[i + 2], arms=(10, 10), mouth="flat", look=4)
        c.layer = "fg"
        trainee(c, 540, 1780, 1.1, hero=True, arms=(10, 10), eyes="dot", mouth="flat", look=6 if lt > .5 else 0)
        c.rect(150, 1560, 930, 1600, (210, 210, 220), w=5)
        c.rect(180, 1600, 900, 1900, (180, 180, 190), w=5)
        c.ell(470, 1520, 40, 38, (220, 40, 50), w=5, n=20)
        c.line([(470, 1484), (476, 1460)], 5, (110, 70, 40))
        c.ell(492, 1468, 14, 7, (90, 170, 70), w=3, n=10)
        c.rect(610, 1450, 670, 1560, (200, 230, 250), w=5)
        c.rect(612, 1490, 668, 1556, (150, 200, 240), ol=None)
        if lt > 1.2:
            c.text(540, 1300, "?", 110, fill=(255, 225, 70), stroke=7, stroke_fill=INK)
    c.layer = "mid"
    return dict(GREY_LOOK)


# ============================================================ 09:00-15:00 dance studio
POSES = [((150, 30), (25, -15)), ((30, 150), (-15, 25)), ((100, 100), (0, 0)), ((170, 170), (20, -20))]


def dancer(c, x, y, s, t, k, **kw):
    arms, legs = POSES[(int(t * 3) + k) % 4]
    trainee(c, x, y, s, arms=arms, legs=legs, bounce=-12 * (int(t * 6) % 2), **kw)


def metronome(c, x, y, t, bpm=112):
    c.poly([(x - 50, y), (x + 50, y), (x + 20, y - 150), (x - 20, y - 150)], (150, 100, 60), w=5)
    a = math.radians(28 * math.sin(t * bpm / 60 * math.pi))
    c.line([(x, y - 20), (x + math.sin(a) * 130, y - 20 - math.cos(a) * 130)], 6)


def studio_time(lt, L=7.8):
    m = int(lt / L * 360)
    return f"{9 + m // 60:02d}:{(m % 60) // 15 * 15:02d}"


def scene3(c, t):
    L = 7.8
    m = t / L * 360 + 9 * 60
    c.cam = ID
    studio(c, t)
    wall_clock(c, 200, 330, 110, int(m // 60), m % 60)
    c.layer = "fg"
    if t < 4.0:
        for k, x in enumerate((140, 340, 740, 940)):
            dancer(c, x, 1600, .85, t, 0, hair=HAIRS[k], hoodie=HOODIES[k], eyes="dot", mouth="flat")
        dancer(c, 540, 1800, 1.1, t, 0, hero=True, eyes="dot", mouth="flat")
        for k in range(5):
            ph = (t * 2 + k * .2) % 1
            sweat(c, 540 + (k - 2) * 90 * ph * 2, 1350 - 120 * ph + 200 * ph * ph)
        metronome(c, 960, 1880, t)
    else:
        lt = t - 4.0
        for k, x in enumerate((160, 360)):
            dancer(c, x, 1620, .9, t, 0, hair=HAIRS[k], hoodie=HOODIES[k], eyes="tired", mouth="flat")
        if lt < .6 or lt > 2.6:
            dancer(c, 820, 1660, .95, t, 0, hair=HAIRS[2], hoodie=HOODIES[2], eyes="tired", mouth="flat")
        elif lt < 2.2:
            trainee(c, 900, 1760, .95, rot=-90, hair=HAIRS[2], hoodie=HOODIES[2], arms=(40, 40), eyes="closed", mouth="wavy")
            for k in range(3):
                sweat(c, 760 + k * 50, 1660 - 30 * ((t * 2 + k * .3) % 1))
        else:
            trainee(c, 840, 1680, .95, rot=-35, hair=HAIRS[2], hoodie=HOODIES[2], arms=(60, 20), eyes="tired", mouth="flat")
        dancer(c, 540, 1820, 1.1, t, 0, hero=True, eyes="tired", mouth="flat")
        sweat(c, 450, 1300 + 30 * ((t * 3) % 1))
        sweat(c, 640, 1320 + 30 * ((t * 3 + .5) % 1))
        metronome(c, 120, 1880, t)
    c.layer = "mid"
    return dict(GREY_LOOK)


# ============================================================ 16:00 evaluation
def eval_room(c):
    plain_room(c, (150, 150, 168), (120, 116, 120), floor_y=1400)
    c.rect(80, 820, 280, 1405, (110, 90, 70), w=6)  # door frame
    c.rect(100, 840, 260, 1405, (230, 230, 240), w=4)  # open door (light behind)


def scene4(c, t):
    lt = t
    c.cam = ID
    eval_room(c)
    c.layer = "mid"
    # trainee who leaves with her bag (background)
    p = seg(lt, 3.6, 6.4)
    if lt < 3.6:
        trainee_sit(c, 380, 1420, .7, hair=HAIRS[2], hoodie=HOODIES[3], mouth="flat", head_down=True)
        c.rrect(470, 1360, 600, 1420, 20, (120, 60, 90), w=4)
    elif p < 1:
        hx = lerp(420, 180, p)
        bag = lambda cc: cc.rrect(-50, 90, 60, 150, 20, (120, 60, 90), w=4)
        trainee(c, hx, 1420, .7, hair=HAIRS[2], hoodie=HOODIES[3], arms=(10, 25), mouth="flat", eyes="closed",
                legs=(15 * math.sin(lt * 10), -15 * math.sin(lt * 10)), held=bag, flip=True)
    c.layer = "fg"
    # judges' table
    c.rect(560, 1500, 1120, 1560, (60, 60, 70), w=5)
    c.rect(580, 1560, 1100, 1800, (80, 80, 92), w=5)
    cards = (3, 2, 4)
    up = ease(seg(lt, 2.4, 2.8))
    for i, x in enumerate((620, 790, 960)):
        judge(c, x, 1500, 1.0, hair=HAIRS[(i * 2) % 6], card=cards[i] if lt > 2.4 else None, card_up=up, glasses=i == 1)
    c.rect(560, 1490, 1120, 1520, (60, 60, 70), w=5)
    # spotlight + Halbo singing
    c.ell(250, 1830, 220, 50, (230, 230, 200), w=4, n=24)
    sad = lt > 2.9
    mic = lambda cc: (cc.line([(0, 100), (-10, 40)], 8, (60, 60, 70)), cc.ell(-12, 32, 16, 18, (40, 40, 50), w=3, n=12))
    trainee(c, 250, 1830, 1.1, hero=True, arms=(15, 120 if not sad else 30), held=mic if not sad else None,
            eyes="closed" if not sad else "dot", mouth="o" if not sad else "flat", look=8)
    if not sad and lt > .2:
        for k in range(3):
            ph = (lt * .8 + k / 3) % 1
            nx, ny = 360 + 100 * ph + k * 20, 1300 - 200 * ph
            c.ell(nx, ny, 16, 12, WHITE, w=4, n=12)
            c.line([(nx + 14, ny), (nx + 14, ny - 60), (nx + 34, ny - 44)], 5)
    if lt > 2.9:
        c.text(250, 1180, "...", 70, fill=WHITE, stroke=5, stroke_fill=INK)
    c.layer = "mid"
    return dict(sat=0.42, tint=(0.84, 0.9, 1.06), spot=(250, 1600, 650, .62))


# ============================================================ 19:00 fan event -> grey
def backstage(c):
    plain_room(c, (120, 124, 140), (100, 96, 100), floor_y=1450)
    sign(c, 540, 470, 820, 150, "DATING VERBOTEN", 66, paper=WHITE, ink=RED, rot=-3, icon="noheart")
    c.rect(780, 900, 960, 1450, (90, 80, 70), w=5)


def contract(c, x, y, rot):
    c.push(x, y, 1, rot)
    c.rect(-200, -250, 200, 250, (250, 248, 240), w=6)
    for k in range(7):
        c.line([(-150, -110 + k * 30), (150, -110 + k * 30)], 3, (170, 170, 180))
    c.pop()
    c.text(x, y - 190, "VERTRAG", 52, fill=INK)
    c.text(x, y + 150, "-287.000.000", 62, fill=RED, stroke=3, stroke_fill=(255, 255, 255))
    c.text(x, y + 210, "WON SCHULDEN", 30, fill=RED)


def scene5(c, t):
    if t < 3.6:
        c.cam = ID
        fade = ease(seg(t, 2.8, 3.6))
        stage(c, t if fade == 0 else 2.8)
        c.layer = "fg"
        smile = fade < .4
        wave = 150 + 25 * math.sin(t * 10) if smile else 20
        trainee(c, 540, 1420, 1.15, hero=True, arms=(15, wave), eyes="happy" if smile else "dot",
                mouth="grin" if smile else "flat")
        for i, x in enumerate((90, 270, 450, 630, 810, 990)):
            fan(c, x, 1860 + (i % 2) * 30, .9, t if fade == 0 else 2.8, i)
        if fade == 0 and int(t * 12) % 5 == 0:
            r = np.random.default_rng(int(t * 12))
            burst(c, r.uniform(100, 980), r.uniform(1500, 1700), 60, (255, 255, 255), 8)
        c.layer = "mid"
        look = mix_look(STAGE_LOOK, GREY_LOOK, fade)
        return look
    lt = t - 3.6
    c.cam = ID
    backstage(c)
    c.layer = "fg"
    trainee(c, 400, 1800, 1.15, hero=True, arms=(10, 10), eyes="dot", mouth="flat", look=6 if lt < 2.5 else 0)
    if lt > 2.6:
        p = seg(lt, 2.6, 5.2)
        manager(c, lerp(1300, -200, p), 1880, 1.0, flip=True, arm=20, arm_l=70)
    p = seg(lt, 0.3, 2.2)
    if 0 < p < 1:
        contract(c, lerp(-300, 1400, p), 1100 - 150 * math.sin(math.pi * p), -12 + 20 * p)
    elif p >= 1 and lt < 2.6:
        pass
    c.layer = "mid"
    return dict(GREY_LOOK)


# ============================================================ 23:00 alone in the dark studio
NOTES = ["Gib auf!", "Talentlos", "Zu dick", "Keiner mag dich"]


def scene6(c, t, outro=False):
    c.cam = ID
    studio(c, t, dark=True)
    c.ell(540, 300, 60, 26, (230, 230, 210), w=4, a0=180, a1=360, n=16)
    c.line([(540, -100), (540, 280)], 4)
    c.layer = "fg"
    sitting = (not outro) and 2.9 <= t < 4.8
    if outro:
        trainee(c, 540, 1820, 1.15, hero=True, arms=(15, 15), eyes="dot", mouth="smile")
        trainee(c, 540, 1395, .55, hair=BLOND, arms=(15, 15), mouth="smile")  # reflection
    elif sitting:
        trainee_sit(c, 520, 1830, 1.1, hero=True, mouth="flat", head_down=t < 4.3)
        trainee_sit(c, 520, 1400, .5, hair=BLOND, mouth="flat", head_down=t < 4.3)
    else:
        dancer(c, 540, 1820, 1.15, t, 0, hero=True, eyes="dot", mouth="flat")
        arms, legs = POSES[int(t * 3) % 4]
        trainee(c, 540, 1395, .55, flip=True, arms=arms, legs=legs, mouth="flat")
    if not outro:
        buzz = 6 * math.sin(t * 60) if 0.9 < t < 1.6 else 0
        phone(c, 860 + buzz, 1820, 1.4, rot=90, screen=(240, 90, 110) if t > 0.9 else (60, 70, 90))
        for k, txt in enumerate(NOTES):
            p = seg(t, 1.2 + k * .5, 4.6 + k * .4)
            if 0 < p < 1 and t < 5.2:
                x = 860 + (k - 1.5) * 120 * p + 30 * math.sin(t * 3 + k)
                y = 1760 - 650 * p
                c.push(x, y, 1, (-8, 6, -4, 8)[k])
                c.rect(-150, -50, 150, 50, (250, 246, 230), w=4)
                c.pop()
                c.text(x, y + 2, txt, 42, fill=RED)
    c.layer = "mid"
    return dict(sat=0.4, tint=(0.62, 0.68, 0.92), spot=(540, 1500, 700, .45))


def outro(c, t):
    look = scene6(c, t + 10, outro=True)
    k = ease(seg(t, 0.3, 2.6))
    c.layer = "fg"
    if k > .3:
        sparkles(c, t, int(14 * k), seed=8, area=(60, 200, 1020, 1300), col=(255, 230, 250))
    c.layer = "mid"
    return dict(sat=lerp(0.4, 0.95, k), tint=tuple(lerp(a, b, k) for a, b in zip(look["tint"], (1.02, 0.98, 1.04))),
                spot=(540, 1500, lerp(700, 1600, k), lerp(.45, .85, k)))


# (start, end, clock text or callable, function) in final-video seconds
TIMELINE = [
    (0.0, 4.0, None, intro),
    (4.0, 11.2, "06:00", scene1),
    (11.2, 18.1, "07:00", scene2),
    (18.1, 25.9, studio_time, scene3),
    (25.9, 32.6, "16:00", scene4),
    (32.6, 41.7, "19:00", scene5),
    (41.7, 48.7, "23:00", scene6),
    (48.7, 52.0, "23:00", outro),
]
DUR = 52.0
