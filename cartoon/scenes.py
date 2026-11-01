"""The six scenes of 'Ein Tag im Leben eines Soldaten' (45 s, 9:16).

Screen layout (1080x1920): clock top-right, subtitles centred around y=820,
the 'stage' with big characters in the lower half (y 1050-1900).
Each scene = two shots with a hard cut (3-5 s each).
"""
import math

import numpy as np

from cast import *  # noqa: F401,F403
from paper import INK

SUB_Y = 820
SUBS = [
    (1.0, 3.4, "Fünf Uhr morgens."),
    (3.5, 7.6, "Hier gibt's keine Snooze-Taste."),
    (8.8, 11.6, "Antreten, dann laufen."),
    (11.8, 14.6, "Jeden Tag."),
    (15.6, 17.4, "Hindernisbahn."),
    (17.6, 22.6, "Hier merkst du, wer wirklich durchzieht."),
    (23.6, 25.0, "Mittag."),
    (25.2, 29.6, "Die einzige halbe Stunde, in der keiner schreit."),
    (30.6, 33.4, "Nachmittags Übung im Gelände."),
    (33.6, 36.6, "Und dann wird's ernst."),
    (37.6, 40.0, "Morgen wieder um fünf."),
    (40.4, 44.6, "Folg mir für Tag zwei."),
]
ID = (540, 960, 1.0)


def run_pose(t, rate=3.2, amp=38):
    p = math.sin(t * rate * 2 * math.pi)
    return (amp * p, -amp * p), (40 + 50 * max(0, p), 40 + 50 * max(0, -p)), -abs(p) * 16


# ============================================================ 05:00 wake-up
FLOOR1 = 1700          # bunk feet
BUNK_L, BUNK_R = 230, 850


def barracks_dawn(c, t):
    room(c, (92, 110, 150), (150, 110, 80), floor_y=1440)
    for x0 in (90, 640):
        c.rect(x0, 300, x0 + 350, 560, (150, 190, 240), w=7)
        c.line([(x0 + 175, 300), (x0 + 175, 560)], 6)
        c.line([(x0, 430), (x0 + 350, 430)], 6)
    c.ell(370, 360, 26, 26, (240, 245, 255), w=4, n=16)
    door_open = t >= 0.7
    c.rect(460, 900, 620, 1445, (250, 236, 170) if door_open else (120, 80, 50), w=6)
    if not door_open:
        c.ell(595, 1180, 9, 9, (230, 200, 60), w=3, n=10)
    c.line([(540, -100), (540, 160)], 4)
    c.ell(540, 180, 80, 34, (255, 240, 170) if t >= 1.5 else (90, 90, 110), a0=180, a1=360, n=16)
    bunk(c, BUNK_L, FLOOR1)
    bunk(c, BUNK_R, FLOOR1)


def scene1(c, t):
    bot = FLOOR1 - 190 * 1.25 + 5
    topb = FLOOR1 - 470 * 1.25 + 5
    if t < 4.5:
        c.cam = ID
        barracks_dawn(c, t)
        if t >= 0.7:
            whistle = 1.0 <= t < 2.6
            instructor(c, 540, 1440, 0.95, arm=150 if whistle else (100 if t >= 2.6 else 20),
                       arm_l=15, mouth="whistle" if whistle else "shout", whistle=whistle)
            if whistle:
                r = 60 + 25 * ((t * 6) % 1)
                for k in range(3):
                    a = math.radians(-60 + k * 40)
                    c.line([(560 + math.cos(a) * r, 1100 + math.sin(a) * r),
                            (560 + math.cos(a) * (r + 35), 1100 + math.sin(a) * (r + 35))], 7, (255, 230, 80))
        c.layer = "fg"
        others = [(BUNK_L, bot), (BUNK_R, topb), (BUNK_R, bot)]
        stand = [(650, 1830), (820, 1880), (990, 1820)]
        for i, ((bx, by), (sx, sy)) in enumerate(zip(others, stand)):
            if t < 2.0:
                sleeper(c, bx, by, 1.25, blanket=(70, 90, 150))
                zzz(c, bx - 90, by - 110, t + i * .3, 1.2)
            elif t < 2.5:
                soldier(c, lerp(bx, sx, .5), by - 40, 1.1, arms=(150, 150), eyes="wide", mouth="o")
            else:
                soldier(c, sx, sy, 1.1, arms=(10, 160 if t > 3 else 10), eyes="wide", mouth="flat")
        if t >= 2.6:
            bubble(c, 760, 1020, "AUFSTEHEN!", 44)
        if t < 2.2:
            sleeper(c, BUNK_L, topb, 1.25, hero=True, blanket=(160, 70, 70))
            zzz(c, BUNK_L - 90, topb - 120, t + .5, 1.2)
        elif t < 2.8:
            sleeper(c, BUNK_L, topb, 1.25, hero=True, blanket=(160, 70, 70), eyes="wide", mouth="o", awake=True)
        elif t < 3.6:
            p = seg(t, 2.8, 3.6)
            x = lerp(240, 420, p)
            y = lerp(topb - 20, 1830, p * p) - 180 * math.sin(math.pi * p)
            soldier(c, x, y, 1.15, rot=-120 * p - 20, hero=True, arms=(140, 160), legs=(30, -30),
                    eyes="wide", mouth="open")
        else:
            soldier(c, 420, 1810, 1.15, rot=-90, hero=True, arms=(40, 120), eyes="x", mouth="wavy")
            if t < 4.1:
                burst(c, 110, 1820, 90 + 60 * seg(t, 3.6, 3.9))
                c.text(120, 1820, "KRACH!", 42, fill=(200, 30, 40))
        c.layer = "mid"
    else:
        c.cam = (420, 1430, 1.3)
        barracks_dawn(c, 9)
        instructor(c, 540, 1440, 0.95, arm=8, arm_l=8, mouth="flat")
        c.layer = "fg"
        soldier(c, 650, 1830, 1.1, arms=(10, 160), mouth="flat", look=-6)
        soldier(c, 820, 1880, 1.1, arms=(10, 160), mouth="flat", look=-6)
        if t < 5.8:
            soldier(c, 420, 1810, 1.15, rot=-90, hero=True, arms=(40, 120), eyes="x", mouth="wavy")
            stars_ring(c, 120, 1740, t, 80)
        elif t < 6.1:
            p = seg(t, 5.8, 6.1)
            soldier(c, 360, 1850 - 160 * math.sin(math.pi * p), 1.15, rot=-90 * (1 - p), hero=True,
                    arms=(150, 150), eyes="wide", mouth="o")
            c.text(200, 1500, "BOING!", 44, fill=(200, 30, 40), stroke=4)
        else:
            soldier(c, 360, 1850, 1.15, hero=True, arms=(10, 165), eyes="dot", mouth="grin")
            if t < 6.7:
                star(c, 230, 1500, 24, (255, 230, 90))
        c.layer = "mid"
    return (0.6, 0.68, 1.05) if t < 1.5 else (0.92, 0.97, 1.1)


# ============================================================ 06:00 formation + run
def outdoor(c, t, sky_cols, sun=None, hill_cols=((80, 120, 110), (90, 150, 80)), ground=(120, 170, 80), horizon=1150):
    sky(c, sky_cols, 0, horizon + 200)
    if sun:
        sx, sy, r, col = sun
        c.layer = "bg"
        for k in range(12):
            a = k * math.pi / 6 + t * .2
            c.poly([(sx + math.cos(a - .08) * r * 1.2, sy + math.sin(a - .08) * r * 1.2),
                    (sx + math.cos(a) * r * 2.0, sy + math.sin(a) * r * 2.0),
                    (sx + math.cos(a + .08) * r * 1.2, sy + math.sin(a + .08) * r * 1.2)],
                   tuple(min(255, v + 25) for v in col), ol=None)
        c.layer = "mid"
        c.ell(sx, sy, r, r, col, w=6)
    hills(c, horizon, 170, hill_cols[0], 0.3)
    for px, s in ((70, .8), (200, .95), (880, .85), (1010, 1.0), (620, .7)):
        pine(c, px, horizon - 10 + 30 * math.sin(px), s)
    hills(c, horizon + 120, 100, hill_cols[1], 2.2)
    c.rect(-400, horizon + 190, 1500, 3000, ground, w=5)


SUNRISE = [(70, 60, 130), (130, 70, 140), (200, 90, 130), (240, 110, 100), (250, 150, 80), (255, 190, 90)]


def scene2(c, t):
    c.cam = ID
    if t < 3.5:
        outdoor(c, t, SUNRISE, sun=(300, 1160 - 30 * t, 120, (255, 170, 50)))
        tent(c, 150, 1400, 1.0)
        barracks_hut(c, 560, 1410, .9)
        flagpole(c, 930, 1500, t, h=480)
        c.layer = "fg"
        xs = [95, 245, 395, 545, 695]
        for i, x in enumerate(xs):
            if i == 4:
                late = seg(t, 0, .9)
                if late < 1:
                    lg, ar, b = run_pose(t)
                    soldier(c, lerp(1150, x, ease(late)), 1700 + b, 1.05, hero=True, legs=lg, arms=ar,
                            eyes="wide", mouth="open", flip=True)
                else:
                    soldier(c, x, 1700, 1.05, hero=True, arms=(10, 165), eyes="tired" if t < 2.2 else "dot",
                            mouth="o" if 1.4 < t < 2.2 else "flat")
            else:
                soldier(c, x, 1700, 1.05, arms=(10, 165), mouth="flat")
        instructor(c, 900, 1890, 1.0, flip=True, arm=90 if t > 1.2 else 20, mouth="shout" if t > 1.2 else "flat",
                   legs=(-8, 8))
        if t > 1.4:
            bubble(c, 820, 1050, "ACHTUNG!", 40, tail=(30, 80))
        c.layer = "mid"
    else:
        lt = t - 3.5
        outdoor(c, t, SUNRISE, sun=(300, 1060, 120, (255, 175, 60)))
        tent(c, 130, 1400, 1.0)
        tent(c, 420, 1400, .9)
        barracks_hut(c, 820, 1410, .9)
        c.layer = "fg"
        for i in range(4):
            x = -40 + lt * 300 + i * 140 - (i % 2) * 30
            lg, ar, b = run_pose(t + i * .13)
            soldier(c, x, 1660 + (i % 2) * 50 + b, 1.0, legs=lg, arms=ar, mouth="flat")
            if int(t * 6 + i) % 3 == 0:
                puff(c, x - 40, 1380 + (i % 2) * 50, 18, (245, 245, 255))
        hx = -280 + lt * 200
        lg, ar, b = run_pose(t, 2.4, 30)
        soldier(c, hx, 1850 + b, 1.15, hero=True, legs=lg, arms=ar, eyes="tired", mouth="tongue", rot=8)
        sweat(c, hx - 85, 1520 + 25 * ((t * 3) % 1))
        sweat(c, hx + 95, 1540 + 25 * ((t * 3 + .5) % 1))
        puff(c, hx + 80, 1560, 22, (245, 245, 255))
        c.layer = "mid"
    return (1.1, 0.98, 0.86)


# ============================================================ 10:00 obstacle course
def field_bg(c, t):
    outdoor(c, t, [(100, 170, 240), (120, 185, 245), (145, 200, 248), (170, 215, 250), (195, 228, 250)],
            sun=(880, 330, 85, (255, 220, 60)), hill_cols=((70, 140, 90), (110, 175, 70)), ground=(196, 168, 110))
    c.layer = "bg"
    cloud(c, 230, 420, .9)
    cloud(c, 640, 260, .7)
    c.layer = "mid"


def cheer(c, t, xs, y=1470, s=.8):
    for i, x in enumerate(xs):
        up = int(t * 6 + i) % 2
        soldier(c, x, y - 20 * up, s, arms=(150 - 20 * up, 150 - 20 * (1 - up)), mouth="open", eyes="happy")


def scene3(c, t):
    c.cam = ID
    if t < 3.5:
        field_bg(c, t)
        cheer(c, t, [650, 790, 930], y=1460, s=.85)
        instructor(c, 140, 1560, .95, arm=110, mouth="shout")
        c.layer = "fg"
        bubble(c, 330, 1040, "SCHNELLER!", 38, tail=(-80, 80))
        for x in (170, 1010):
            c.rect(x - 11, 1640, x + 11, 1830, WOOD_D, w=4)
        p = seg(t, 0, 3.4)
        hx = lerp(60, 900, p)
        wig = math.sin(t * 14) * 18
        soldier(c, hx, 1800, 1.1, rot=90, hero=True, legs=(10 + wig * .5, -10 - wig * .5),
                arms=(150 + wig, 130 - wig), eyes="dot", mouth="flat")
        puff(c, hx - 300, 1830, 22, (225, 200, 150))
        for k in range(0, 18):
            x = 170 + k * 48
            c.line([(x, 1650), (x + 46, 1830)], 4, (60, 70, 40))
            c.line([(x + 46, 1650), (x, 1830)], 4, (60, 70, 40))
        c.line([(160, 1650), (1020, 1650)], 7, (60, 70, 40))
        c.layer = "mid"
    else:
        lt = t - 3.5
        field_bg(c, t)
        won = lt >= 2.8
        cheer(c, t if won else 0, [110, 250, 850, 990], y=1560, s=.9)
        c.layer = "fg"
        top, gnd = 1270, 1830
        c.rect(480, top, 660, gnd, WOOD, w=6)
        for k in range(1, 11):
            c.line([(480, top + k * 52), (660, top + k * 52)], 3, WOOD_D)
        if lt < .8:
            y = lerp(gnd, 1580, ease(seg(lt, 0, .8)))
            soldier(c, 400, y, 1.1, hero=True, arms=(160, 160),
                    legs=(20 * math.sin(t * 12), -20 * math.sin(t * 12)), eyes="dot", mouth="flat")
        elif lt < 1.3:
            p = seg(lt, .8, 1.3)
            soldier(c, 390, lerp(1580, gnd + 10, p * p), 1.1, hero=True, arms=(170, 170), eyes="wide", mouth="o", rot=-10 * p)
        elif lt < 1.9:
            soldier(c, 350, gnd + 10, 1.1, hero=True, arms=(40, 40), eyes="x", mouth="wavy", rot=-12)
            star(c, 300, 1450 - 30 * seg(lt, 1.3, 1.9), 20, (255, 220, 60))
            if lt < 1.5:
                c.text(220, 1400, "BOING!", 46, fill=(200, 30, 40), stroke=4)
        elif lt < 2.8:
            p = ease(seg(lt, 1.9, 2.8))
            soldier(c, lerp(400, 480, p), lerp(gnd, top + 20, p), 1.1, hero=True, arms=(165, 165),
                    legs=(25 * math.sin(t * 14), -25 * math.sin(t * 14)), eyes="dot", mouth="tongue")
            sweat(c, 320, lerp(1500, 1100, p))
        else:
            soldier(c, 570, top, 1.1, hero=True, arms=(160, 160), eyes="happy", mouth="grin")
            for k in range(6):
                a = k * math.pi / 3 + lt
                star(c, 570 + math.cos(a) * 200, top - 170 + math.sin(a) * 100, 15, (255, 225, 70))
        c.layer = "mid"
    return (1.03, 1.03, 1.0)


# ============================================================ 12:30 canteen
def canteen_bg(c, floor=1450):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, floor, (150, 186, 108), ol=None, jit=False)
    for k in range(-4, 16):
        if k % 2:
            c.poly([(540 + (k - 6) * 40, -100), (540 + (k - 5) * 40, -100), (k * 100 + 100, floor), (k * 100, floor)],
                   (120, 160, 90), ol=None, jit=False)
    c.layer = "mid"
    for x in (60, 1020):
        c.rect(x - 14, 100, x + 14, floor, WOOD_D, w=4)
    c.line([(-10, 260), (1090, 300)], 4)
    for k in range(5):
        c.ell(80 + k * 230, 270 + k * 8, 16, 20, (255, 235, 140), w=3, n=10)
    c.rect(-400, floor, 1500, 3000, (150, 120, 90), w=5)


def table(c, y, x0=-60, x1=1140, h=140):
    c.rect(x0, y, x1, y + 40, (190, 140, 90), w=5)
    c.rect(x0, y + 40, x1, y + h, (160, 112, 70), w=5)


def tray(c, x, y, blob=0.0, w=110):
    c.rect(x - w, y - 12, x + w, y + 6, (190, 196, 204), w=4)
    if blob > 0:
        r = 70 * blob
        pts = []
        for a in np.linspace(math.pi, 2 * math.pi, 14):
            pts.append((x + math.cos(a) * r * (1 + .12 * math.sin(a * 5)), y - 12 + math.sin(a) * r * 1.05))
        c.poly(pts, GREY_FOOD, w=4)
        c.ell(x - 20 * blob, y - 12 - r * .6, 12 * blob, 8 * blob, (205, 203, 200), ol=None, n=10)
        c.ell(x + 22 * blob, y - 12 - r * .35, 8 * blob, 6 * blob, (130, 128, 126), ol=None, n=10)


def eaters(c, t, xs, y, s, lt=0):
    for i, x in enumerate(xs):
        up = (int(t * 5) + i) % 2
        soldier(c, x, y, s, arms=(15, 60 + 60 * up), mouth="o" if up else "smile")


def scene4(c, t):
    c.cam = ID
    if t < 3.5:
        canteen_bg(c)
        eaters(c, t, (70, 210, 350), 1330, .75)
        table(c, 1220, -60, 470, 110)
        # cook behind counter
        soldier(c, 860, 1640, 1.05, arms=(20, 130 if 1.0 < t < 1.6 else 60), mouth="smile")
        c.push(860, 1640, 1.05)
        c.ell(0, -330, 54, 32, WHITE, w=4)
        c.rect(-42, -330, 42, -296, WHITE, w=4)
        c.pop()
        c.layer = "fg"
        c.rect(640, 1560, 1140, 1800, (200, 200, 210), w=6)
        c.rect(690, 1530, 920, 1560, (150, 150, 160), w=4)
        if 1.0 < t < 1.6:
            p = seg(t, 1.0, 1.6)
            c.ell(lerp(760, 440, p), lerp(1430, 1690, p), 50, 38, GREY_FOOD, w=4)
        blob = 1 if t >= 1.6 else 0
        soldier(c, 400, 1860, 1.15, hero=True, arms=(55, 55), eyes="wide" if blob else "dot",
                mouth="o" if blob else "smile", look=8)
        tray(c, 400, 1745 + (14 if 1.6 <= t < 1.9 else 0), blob)
        if 1.6 <= t < 2.1:
            burst(c, 640, 1700, 80, (235, 235, 235), 8)
            c.text(640, 1700, "PLATSCH!", 30, fill=INK)
        if t >= 2.1:
            c.text(560, 1330, "?", 130, fill=(255, 225, 70), stroke=7, stroke_fill=INK)
        c.layer = "mid"
    else:
        lt = t - 3.5
        canteen_bg(c)
        eaters(c, t, (120, 290, 790, 960), 1690, 1.0)
        c.layer = "fg"
        if lt < 1.1:
            soldier(c, 540, 1720, 1.1, hero=True, arms=(15, 15), eyes="dot", mouth="flat", look=-4)
            c.text(540, 1260, "?", 120, fill=(255, 225, 70), stroke=7, stroke_fill=INK)
        elif lt < 1.9:
            soldier(c, 540, 1720, 1.1, hero=True, arms=(78, 78), eyes="dot", mouth="flat")
            c.text(540, 1250, "na gut...", 40, fill=WHITE, stroke=4, stroke_fill=INK)
        else:
            up = (int(t * 6)) % 2

            def spoon(cc):
                cc.line([(0, 70), (-30, 10)], 8, (190, 196, 204))
                cc.ell(-34, 4, 15, 11, (190, 196, 204), w=3, n=10)
            soldier(c, 540, 1720, 1.1, hero=True, arms=(20, 150 if up else 80), eyes="happy",
                    mouth="o" if up else "grin", held=spoon)
            for k in range(2):
                ph = (lt * .7 + k * .5) % 1
                hx, hy = 680 + 50 * k, 1330 - 140 * ph
                c.poly([(hx, hy), (hx - 24, hy - 20), (hx - 13, hy - 35), (hx, hy - 24), (hx + 13, hy - 35),
                        (hx + 24, hy - 20)], (240, 80, 110), w=3)
        table(c, 1580, h=400)
        tray(c, 540, 1585, .8 if lt >= 1.9 else 1)
        c.layer = "mid"
    return (1.08, 1.0, 0.88)


# ============================================================ 15:00 field exercise
def truck(c, x, y, t, s=1.0):
    c.push(x, y, s)
    for hx in (-150, 150):
        c.ell(hx, 0, 52, 52, BOOT, w=5, n=20)
        c.ell(hx, 0, 20, 20, (170, 170, 170), w=4, n=12)
        a = -t * 9
        c.line([(hx + math.cos(a) * 20, math.sin(a) * 20), (hx + math.cos(a) * 46, math.sin(a) * 46)], 5, (120, 120, 120))
    for i, hx in enumerate((-235, -150, -65)):
        bob = 8 * math.sin(t * 15 + i)
        hero = i == 1
        c.push(hx, -135 + bob, .55)
        c.ell(0, -40, 54, 62, SKIN)
        face(c, 0, -34, "wide" if hero else "dot", hero_mouth("flat") if hero else "flat")
        helmet(c, 0, -62, big=hero)
        c.pop()
    c.rect(-290, -140, 30, -30, (80, 120, 60), w=6)
    for k in range(4):
        c.line([(-290 + k * 80, -140), (-290 + k * 80, -30)], 3, (60, 90, 44))
    c.poly([(40, -30), (40, -190), (160, -190), (220, -110), (230, -30)], (90, 132, 66), w=6)
    c.poly([(70, -170), (150, -170), (195, -115), (70, -115)], (180, 220, 240), w=4)
    c.rect(-300, -40, 240, 10, (70, 100, 52), w=5)
    c.pop()


def bush(c, x, y, s=1.0, col=(60, 150, 60)):
    c.push(x, y, s)
    for dx, dy, r in ((-90, 0, 70), (-30, -40, 85), (50, -30, 80), (110, 5, 62), (0, 20, 90)):
        c.ell(dx, dy, r, r * .8, col, w=5, n=18)
    c.pop()


GOLDEN = [(110, 130, 190), (170, 150, 170), (230, 170, 130), (250, 190, 110), (255, 210, 120), (255, 225, 150)]


def scene5(c, t):
    c.cam = ID
    if t < 3.5:
        outdoor(c, t, GOLDEN, sun=(820, 560, 95, (255, 200, 70)),
                hill_cols=((110, 130, 80), (150, 170, 70)), ground=(150, 170, 70))
        c.layer = "fg"
        p = seg(t, 0, 3.5)
        x = lerp(-480, 1560, p)
        terrain = 1740 - 70 * math.sin(x / 180)
        bump = 22 * abs(math.sin(t * 9))
        rot = 7 * math.cos(x / 180) + 3 * math.sin(t * 13)
        for k in range(3):
            puff(c, x - 530 - k * 70, terrain - 10 - k * 24, 30 + k * 9, (230, 200, 140))
        c.push(x, terrain - bump, 1, rot)
        truck(c, 0, 0, t, 1.6)
        c.pop()
        hills(c, 1830, 60, (130, 160, 60), 4.0)
        c.layer = "mid"
    else:
        lt = t - 3.5
        outdoor(c, t, GOLDEN, sun=(820, 600, 95, (255, 200, 70)),
                hill_cols=((110, 130, 80), (150, 170, 70)), ground=(150, 170, 70))
        c.layer = "fg"
        look = 18 * math.copysign(1, math.sin(lt * 2.4)) if lt > .5 else 0
        duck = 90 if 1.9 < lt < 2.6 else 0
        for i, x in enumerate((190, 540, 890)):
            hero = i == 1
            c.push(x, 1600 + duck + (10 if hero else 0), 1.1)
            c.ell(0, -40, 54, 62, SKIN)
            face(c, 0, -34, "wide" if hero else "dot", hero_mouth("flat") if hero else "flat", look=look)
            helmet(c, 0, -62, big=hero, branches=True, sway=4 * math.sin(t * 3 + i))
            c.pop()
        if lt > 1.0 and duck == 0:
            sweat(c, 640, 1460)
        if lt > 2.7:
            c.text(540, 1180, "!", 120, fill=(255, 225, 70), stroke=7, stroke_fill=INK)
        for x in (150, 540, 930):
            bush(c, x, 1720, 1.4, (60, 150, 60) if x != 540 else (70, 160, 66))
        c.layer = "mid"
    return (1.12, 1.0, 0.78)


# ============================================================ 21:00 lights out
LAMP = (640, 1330)


def night_room(c, t):
    room(c, (52, 56, 92), (110, 80, 66), floor_y=1440)
    c.rect(90, 290, 470, 600, (20, 26, 70), w=7)
    for sx, sy in ((140, 330), (250, 380), (400, 320), (190, 520), (420, 550), (330, 460)):
        star(c, sx, sy, 10 + 3 * math.sin(t * 4 + sx), (255, 240, 150), w=3)
    c.ell(390, 400, 34, 34, (250, 240, 200), w=4, n=16)
    c.ell(405, 390, 30, 30, (20, 26, 70), ol=None, n=16)
    c.line([(280, 290), (280, 600)], 6)
    c.line([(90, 445), (470, 445)], 6)
    bunk(c, BUNK_L, FLOOR1)
    bunk(c, BUNK_R, FLOOR1)
    c.rect(570, 1450, 710, 1620, WOOD, w=5)
    c.rect(625, 1340, 655, 1450, (90, 90, 90), w=4)
    c.poly([(580, 1350), (600, 1270), (680, 1270), (700, 1350)], (255, 200, 90), w=5)


def scene6(c, t):
    bot = FLOOR1 - 190 * 1.25 + 5
    topb = FLOOR1 - 470 * 1.25 + 5
    if t < 4.0:
        c.cam = ID
        night_room(c, t)
        c.layer = "fg"
        for i, (x, y) in enumerate(((BUNK_R, topb), (BUNK_R, bot), (BUNK_L, topb))):
            sleeper(c, x, y, 1.25, blanket=(70, 90, 150))
            zzz(c, x - 90, y - 110, t + i * .35, 1.2)
        rub = math.sin(t * 16) * 25

        def boot(cc):
            cc.ell(-10 + rub * .3, 92, 36, 22, BOOT, w=4, n=14)
            cc.rect(-32 + rub * .3, 40, 6 + rub * .3, 92, BOOT, w=4)
        soldier(c, 300, 1860, 1.15, hero=True, arms=(55 + rub * .6, 35), eyes="dot", mouth="smile", held=boot)
        if int(t * 4) % 2:
            star(c, 440, 1660, 20, (255, 255, 200))
        c.layer = "mid"
        return ("lamp", 0)
    c.cam = (360, 1330, 1.45)
    lt = t - 4.0
    night_room(c, t)
    c.layer = "fg"
    sleeper(c, BUNK_L, topb, 1.25, blanket=(70, 90, 150))
    zzz(c, BUNK_L - 90, topb - 110, t, 1.2)
    sleeper(c, BUNK_R, bot, 1.25, blanket=(70, 90, 150))
    awake = lt > .8
    sleeper(c, BUNK_L, bot, 1.25, hero=True, blanket=(160, 70, 70), eyes="tired" if awake else "closed",
            mouth="smile" if awake else "flat", awake=awake)
    if lt > 1.5:
        p = ease(seg(lt, 1.5, 2.0))
        c.push(BUNK_L + 90, bot - 10 - 90 * p, 1.6, 0)
        c.rrect(-12, 0, 12, 60, 10, CAMO)
        c.ell(0, 0, 20, 24, SKIN)
        c.rrect(-8, -50, 8, -12, 7, SKIN, w=4)
        c.pop()
        if 2.0 < lt < 2.8:
            star(c, BUNK_L + 170, bot - 230, 26, (255, 240, 120))
    c.ell(420, 1745, 40, 22, BOOT, w=4, n=14)
    c.ell(500, 1750, 40, 22, BOOT, w=4, n=14)
    c.layer = "mid"
    return ("lamp", 1)


SCENES = [
    (0.0, 8.0, "05:00", scene1),
    (8.0, 15.0, "06:00", scene2),
    (15.0, 23.0, "10:00", scene3),
    (23.0, 30.0, "12:30", scene4),
    (30.0, 37.0, "15:00", scene5),
    (37.0, 45.0, "21:00", scene6),
]


# ============================================================ INTRO (0-4 s, before scene 1)
INTRO = 4.0
SIGNS = [  # (land time, y, w, h, paper colour, text colour, text, size)
    (0.35, 560, 560, 190, (250, 247, 238), INK, "EIN TAG", 128),
    (1.00, 790, 760, 190, (92, 168, 76), (255, 255, 255), "ALS SOLDAT", 120),
    (2.25, 1040, 700, 210, (214, 52, 52), (255, 255, 255), "mit Halbo!", 128),
]


def _torn(w, h, seed):
    """Fixed jagged outline of a torn paper sheet (local coords, centred)."""
    r = np.random.default_rng(seed)
    pts = []
    for x in np.linspace(-w / 2, w / 2, 22):
        pts.append((x, -h / 2 + r.uniform(-9, 9)))
    for y in np.linspace(-h / 2, h / 2, 8)[1:]:
        pts.append((w / 2 + r.uniform(-10, 10), y))
    for x in np.linspace(w / 2, -w / 2, 22)[1:]:
        pts.append((x, h / 2 + r.uniform(-9, 9)))
    for y in np.linspace(h / 2, -h / 2, 8)[1:-1]:
        pts.append((-w / 2 + r.uniform(-10, 10), y))
    return pts


def base_from_above(c, t):
    """Top-down view of the little cartoon base in warm morning light."""
    c.layer = "bg"
    c.rect(-400, -1000, 1500, 3000, (118, 176, 82), ol=None, jit=False)
    for k in range(40):
        x, y = (k * 389) % 1300 - 100, (k * 677) % 2300 - 200
        c.ell(x, y, 30, 18, (104, 160, 72), ol=None, jit=False, n=12)
    c.layer = "mid"
    # sandy paths
    c.poly([(470, -400), (610, -400), (610, 2400), (470, 2400)], (222, 196, 140), w=5)
    c.poly([(-400, 1290), (1500, 1220), (1500, 1340), (-400, 1410)], (222, 196, 140), w=5)
    # parade ground with flagpole (seen from above)
    c.ell(540, 1310, 190, 120, (210, 184, 128), w=5)
    c.ell(540, 1310, 14, 14, (200, 200, 210), w=4, n=12)
    wave = 8 * math.sin(t * 6)
    c.poly([(554, 1306), (660, 1290 + wave), (660, 1330 + wave), (554, 1318)], FLAG_GREEN, w=4)
    # tents from above (squares with a ridge)
    for x, y in ((140, 300), (330, 300), (140, 520), (330, 520), (760, 1560), (950, 1560), (760, 1780)):
        c.rect(x - 75, y - 60, x + 75, y + 60, (86, 132, 62), w=5)
        c.line([(x - 75, y), (x + 75, y)], 4, (48, 76, 36))
    # barracks roofs
    for x, y in ((830, 330), (830, 620)):
        c.rect(x - 180, y - 90, x + 180, y + 90, (176, 70, 56), w=6)
        c.line([(x - 180, y), (x + 180, y)], 5, (120, 44, 36))
        for k in range(1, 6):
            c.line([(x - 180 + k * 60, y - 90), (x - 180 + k * 60, y + 90)], 2, (150, 56, 46))
    # training field with obstacle wall and net
    c.rect(60, 1550, 420, 1900, (196, 168, 110), w=5)
    c.rect(120, 1610, 360, 1640, WOOD, w=4)
    for k in range(6):
        c.line([(120 + k * 48, 1720), (160 + k * 48, 1840)], 3, (60, 70, 40))
    # pine trees from above
    for x, y in ((40, 980), (130, 1080), (980, 900), (1050, 1050), (60, 60), (1000, 1000), (920, 1180)):
        star(c, x, y, 70, PINE, pts_n=8, w=5)
        c.ell(x, y, 22, 22, PINE_D, w=3, n=12)
    # tiny soldiers marching along the path (helmets from above)
    for i in range(6):
        y = (2000 - t * 120 - i * 75)
        c.ell(540, y, 26, 26, HELM, w=4, n=14)
        c.ell(540, y + 4, 14, 8, HELM_D, ol=None, n=10)
        c.ell(540 + 28 * ((i % 2) * 2 - 1), y, 9, 9, SKIN, w=3, n=8)


def intro(c, t):
    # slight slow zoom over the base; tiny shake right after each sign lands
    shake = 0
    for land, *_ in SIGNS:
        if 0 <= t - land < 0.17:
            shake = 10 if int((t - land) * 12) % 2 == 0 else -10
    c.cam = (540 + shake, 960 - shake * .6, 1.0 + 0.05 * t / INTRO)
    base_from_above(c, t)
    c.cam = (540 + shake, 960, 1.0)
    c.layer = "ui"
    for i, (land, y, w, h, paper, ink, txt, size) in enumerate(SIGNS):
        if t < land - 0.17:
            continue
        p = (t - land) / 0.17          # 2 frames falling in, then a small overshoot bounce
        if p < 0:
            s = 2.0 + (-p) * 1.2
        elif p < 1:
            s = 0.92
        elif p < 2:
            s = 1.04
        else:
            s = 1.0
        rot = (-3, 2, -2)[i]
        c.push(540, y, s, rot)
        c.poly(_torn(w, h, 11 + i), paper, w=6)
        c.pop()
        c.push(540, y, s, 0)
        c.text(0, 4, txt, size, fill=ink, stroke=5 if i else 0, stroke_fill=INK)
        c.pop()
        if 0 <= p < 2:  # paper dust on impact
            for k in range(4):
                a = k * math.pi / 2 + .6
                puff(c, 540 + math.cos(a) * (w / 2 + 20), y + math.sin(a) * (h / 2 + 10), 18, (250, 245, 230))
        if i == 2:
            for k in range(7):
                a = k * 2 * math.pi / 7 + t * 1.5
                tw = 0.6 + 0.4 * math.sin(t * 9 + k * 2)
                star(c, 540 + math.cos(a) * 420, y + math.sin(a) * 170, 20 * tw + 6, (255, 228, 80), w=4)
    # Halbo pops up below the signs and salutes
    if t >= 2.7:
        p = (t - 2.7) / 0.25
        y = 2250 if p < 1 else (1760 if p < 2 else 1800)
        salute = t >= 3.05
        c.layer = "fg"
        soldier(c, 540, y, 1.45, hero=True, arms=(12, 165 if salute else 60),
                eyes="happy" if salute else "wide", mouth="grin" if salute else "o")
        if 3.05 <= t < 3.4:
            star(c, 700, 1300, 26, (255, 240, 120))
    c.layer = "mid"
    return (1.1, 1.0, 0.88)
