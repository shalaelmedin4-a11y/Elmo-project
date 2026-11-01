"""POV: Ein Tag als junger Naruto – draws every frame (12 fps) with Pillow + numpy."""
import json, math, os, random, sys
from multiprocessing import Pool
from PIL import Image, ImageDraw
from sketch import Canvas, INK
from chars import anime, pov_arm, hand, cat, headband, leaf_mark, SKIN, ORANGE, ORANGE_D, BAND, METAL, WHITE

W, H, FPS = 1080, 1920, 12
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
FRAMES = os.path.join(BUILD, "frames")
VOICE = json.load(open(os.path.join(BUILD, "voices.json")))

SCENES = [("intro", 0, 4), ("wake", 4, 10), ("prep", 10, 16.5), ("village", 16.5, 23), ("klasse", 23, 29.5),
          ("ramen", 29.5, 35.5), ("wald", 35.5, 44), ("katze", 44, 51), ("nacht", 51, 58)]
TOTAL = 58.0

VILLAGERS = [dict(hair=(80, 60, 50), style="bun", top=(150, 110, 140), eye=(40, 40, 40)),
             dict(hair=(60, 60, 64), style="short", top=(110, 130, 150), eye=(40, 40, 40), skin=(220, 175, 140)),
             dict(hair=(170, 160, 150), style="bald", top=(160, 140, 100), eye=(40, 40, 40)),
             dict(hair=(120, 70, 40), style="short", top=(130, 150, 110), eye=(40, 40, 40))]


def lerp(a, b, f):
    return a + (b - a) * max(0.0, min(1.0, f))


def ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def talk(lid, T):
    v = VOICE[lid]
    i = int((T - v["start"]) * FPS)
    return v["env"][i] if 0 <= i < len(v["env"]) else 0.0


def speaking(lid, T):
    v = VOICE[lid]
    return v["start"] <= T < v["start"] + v["dur"]


def shake(c, T, walk=0.0, amt=2.5, run=0.0):
    r = random.Random(int(T * FPS) * 13 + 5)
    c.ox = r.uniform(-amt, amt) + math.sin(T * 2 * math.pi * 0.9) * 10 * walk + math.sin(T * 2 * math.pi * 1.8) * 16 * run
    c.oy = r.uniform(-amt, amt) - abs(math.sin(T * 2 * math.pi * 0.9)) * 18 * walk - abs(math.sin(T * 2 * math.pi * 1.8)) * 34 * run


def time_sign(c, txt):
    pts = [(36, 58), (318, 46), (326, 168), (42, 178)]
    c.poly(pts, (236, 226, 200), "tsign", world=False, misreg=2)
    c.circle(92, 112, 34, (250, 246, 236), "tclock", world=False)
    c.line([(92, 112), (92, 88)], "th1", lw=4, world=False)
    c.line([(92, 112), (110, 120)], "th2", lw=4, world=False)
    c.text(txt, 220, 108, 62, fill=(60, 48, 44), outline=(236, 226, 200), ow=1)


def blink(c, op):
    if op >= 1:
        return
    lid = Image.new("L", (W, H), 255)
    if op > 0.02:
        ry = op * 1150
        ImageDraw.Draw(lid).ellipse((-500, 960 - ry, W + 500, 960 + ry), fill=0)
    c.img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), (30, 24, 24)).split(), lid)))


def speed_lines(c, key, n=26, cx=540, cy=900, r0=520, alpha=120, color=(250, 246, 236)):
    rr = c.rng(key)
    for i in range(n):
        a = rr.uniform(0, 2 * math.pi)
        r1 = rr.uniform(r0, r0 + 200)
        c.line([(cx + math.cos(a) * r1, cy + math.sin(a) * r1), (cx + math.cos(a) * 1400, cy + math.sin(a) * 1400)],
               key + str(i), lw=rr.randint(3, 7), color=color, alpha=alpha, world=False, passes=1)


def steam(c, x, y, t, key, n=3, h=220):
    for i in range(n):
        pts = []
        for k in range(8):
            yy = y - k * h / 7
            pts.append((x + (i - 1) * 50 + math.sin(t * 3 + k * 0.9 + i * 2) * 18, yy))
        c.line(pts, key + str(i), lw=5, color=(250, 248, 244), alpha=150, passes=1)


# ================================================================== scenes
def fit(txt, size, width):
    """Largest font size <= size whose text fits into width pixels."""
    from sketch import font
    while size > 20 and font(size).getlength(txt) > width:
        size -= 4
    return size


def s_intro(c, t, T):
    c.rect(-40, -40, W + 80, H + 80, (232, 196, 150), "ibg", line=False)
    c.poly(c.ell(540, 950, 620, 520), (240, 214, 176), "iglow", line=False)
    c.line(c.ell(540, 950, 470, 420, a0=0.4, a1=5.6), "iswirl", lw=10, color=(214, 150, 90), alpha=160)
    for i in range(10):
        r = random.Random(i)
        x = (r.uniform(0, W) + t * 60 * r.uniform(0.5, 1.5)) % W
        y = (r.uniform(0, H) + t * 120 * r.uniform(0.6, 1.2)) % H
        a = t * 2 + i
        pts = [(x + math.cos(a) * 34, y + math.sin(a) * 34), (x + math.cos(a + 2.5) * 14, y + math.sin(a + 2.5) * 14),
               (x - math.cos(a) * 34, y - math.sin(a) * 34), (x + math.cos(a - 2.5) * 14, y + math.sin(a - 2.5) * 14)]
        c.poly(pts, (150, 170, 100), f"leaf{i}")
    pop = lambda k: [1.3, 1.08, 0.98, 1.0][min(3, int(k * FPS))]
    z = pop(t - 0.1) if t >= 0.1 else 0
    if t >= 0.1:
        c.poly([(30, 470), (1050, 440), (1060, 1260), (24, 1290)], (250, 244, 230), "ibrush", misreg=6)
        c.text("POV:", 540, 590, fit("POV:", 190, 600) * z, fill=(222, 132, 58), angle=3)
        c.text("Ein Tag als", 540, 820, fit("Ein Tag als", 150, 900) * z, angle=-2)
        c.text("junger Naruto", 540, 1060, fit("junger Naruto", 170, 960) * z, angle=-2)
    if t >= 2.7:
        z2 = pop(t - 2.7)
        c.poly([(110, 1350), (980, 1320), (990, 1560), (100, 1590)], (222, 132, 58), "ihalbo", misreg=5)
        c.text("… mit Halbo!", 545, 1455, fit("… mit Halbo!", 130, 820) * z2, fill=(252, 246, 236), angle=-3)
    return dict(warm=1.0)


def apartment(c, px, night=False):
    wall = (196, 186, 150) if not night else (120, 110, 110)
    c.rect(-80, -40, W + 900, 1500, wall, "awall", line=False)
    c.rect(-80, 1440, W + 900, 600, (150, 120, 92), "afloor", line=False)
    # poster and window
    c.rect(px + 60, 260, 240, 330, (210, 120, 70), "poster")
    c.poly(c.ell(px + 180, 420, 70, 70), (240, 200, 90), "posterspiral", line=False)
    c.line(c.ell(px + 180, 420, 50, 50, a0=0, a1=5.5), "pspiral", lw=6, color=(160, 70, 40))
    if not night:
        c.rect(px + 400, 230, 560, 560, (230, 225, 210), "wframe")
        c.rect(px + 430, 260, 500, 500, (200, 222, 228), "wglass")
        c.line([(px + 680, 260), (px + 680, 760)], "wbar", lw=8)
        c.glow(px + 680, 500, 380, (255, 232, 180), 90)


def ramen_cup(c, x, y, s, key, tipped=False):
    if tipped:
        c.poly([(x - 80 * s, y), (x + 70 * s, y - 40 * s), (x + 90 * s, y + 40 * s), (x - 60 * s, y + 70 * s)], WHITE, key)
        c.poly([(x - 10 * s, y - 15 * s), (x + 40 * s, y - 28 * s), (x + 55 * s, y + 20 * s), (x + 5 * s, y + 35 * s)],
               (222, 132, 58), key + "lb", line=False)
        return
    c.poly([(x - 60 * s, y - 120 * s), (x + 60 * s, y - 120 * s), (x + 45 * s, y), (x - 45 * s, y)], WHITE, key)
    c.poly([(x - 55 * s, y - 85 * s), (x + 55 * s, y - 85 * s), (x + 50 * s, y - 50 * s), (x - 50 * s, y - 50 * s)],
           (222, 132, 58), key + "lb", line=False)
    c.line([(x + 10 * s, y - 115 * s), (x + 40 * s, y - 220 * s)], key + "st1", lw=5, color=(170, 120, 70))
    c.line([(x + 25 * s, y - 115 * s), (x + 60 * s, y - 210 * s)], key + "st2", lw=5, color=(170, 120, 70))


def s_wake(c, t, T):
    shake(c, T, amt=2)
    turn = ease((t - 0.9) / 0.4) * (1 - ease((t - 2.1) / 0.4))
    px = turn * 560
    apartment(c, px)
    # shelf with the alarm clock (to the left)
    cx = -330 + px
    c.rect(cx - 220, 1000, 440, 40, (130, 96, 70), "shelf")
    ring = 0.7 < t < 1.85
    j = math.sin(t * 70) * 7 if ring else 0
    for sgn in (-1, 1):
        c.circle(cx + j + sgn * 85, 760, 38, (200, 90, 70), f"bell{sgn}")
    c.circle(cx + j, 880, 125, (200, 90, 70), "clockbody")
    c.circle(cx + j, 880, 100, (246, 240, 226), "clockface")
    for i in range(12):
        a = i * math.pi / 6
        c.line([(cx + j + math.cos(a) * 82, 880 + math.sin(a) * 82), (cx + j + math.cos(a) * 92, 880 + math.sin(a) * 92)], f"tk{i}", lw=4)
    c.line([(cx + j, 880), (cx + j, 960)], "minute", lw=7)                   # 6:30
    c.line([(cx + j, 880), (cx + j + 10, 935)], "hour", lw=10)
    if ring:
        for i in range(3):
            a = -math.pi / 2 + (i - 1) * 0.6
            c.line([(cx + math.cos(a) * 170, 860 + math.sin(a) * 170), (cx + math.cos(a) * 220, 860 + math.sin(a) * 220)], f"rl{i}", lw=6)
    # messy table with empty instant-ramen cups
    c.poly([(-40, 1250), (1120, 1230), (1120, 1560), (-40, 1580)], (160, 120, 84), "table")
    c.hatch([(-40, 1480), (1120, 1460), (1120, 1560), (-40, 1580)], "tableh", spacing=14)
    ramen_cup(c, 230 + px * 0.2, 1310, 1.0, "cup1")
    ramen_cup(c, 470 + px * 0.2, 1330, 0.9, "cup2")
    ramen_cup(c, 760 + px * 0.2, 1300, 1.0, "cup3", tipped=True)
    ramen_cup(c, 960 + px * 0.2, 1320, 0.85, "cup4")
    c.poly([(560 + px * 0.2, 1380), (680 + px * 0.2, 1360), (700 + px * 0.2, 1420), (590 + px * 0.2, 1440)], (230, 225, 210), "paper")
    # blanket edge
    c.poly([(-40, 1640), (300, 1600), (700, 1650), (1120, 1610), (1120, 1960), (-40, 1960)], (120, 140, 120), "blanket", world=False)
    # hand smacks the clock, then fist pump
    if 1.4 <= t < 2.3:
        f = ease((t - 1.4) / 0.4) * (1 - ease((t - 1.95) / 0.35))
        pov_arm(c, -1, lerp(150, cx + c.ox + 40, f), lerp(2000, 700 + c.oy, f), "open", ang=-0.1)
    if 2.6 <= t:
        f = ease((t - 2.6) / 0.3)
        pov_arm(c, 1, lerp(900, 790, f), lerp(2100, 1150 - 30 * math.sin(t * 12) * (t < 4.6), f), "fist", ang=-0.15)
    o = [(0, 0.0), (0.25, 0.0), (0.45, 0.5), (0.58, 0.12), (0.85, 1.0)]
    op = 1.0
    for (t0, a0), (t1, a1) in zip(o, o[1:]):
        if t0 <= t < t1:
            op = lerp(a0, a1, (t - t0) / (t1 - t0))
    time_sign(c, "06:30")
    blink(c, op)
    return dict(warm=1.0, light=(0.8, 0.2))


def mirror_naruto(c, T, t, grin=True):
    c.rect(-40, -40, W + 80, H + 80, (186, 196, 186), "bwall", line=False)
    for x in range(0, W, 135):
        c.line([(x, 0), (x, 1500)], f"tile{x}", lw=2, alpha=70, passes=1)
    c.rect(150, 200, 780, 1150, (200, 190, 170), "mframe")
    c.rect(180, 230, 720, 1090, (210, 224, 226), "mglass")
    tk = talk("s2", T)
    anime(c, 540, 700, 1.25, "naruto", expr="grin" if tk < 0.2 else "smile", talk=tk)
    for i, (fx, w) in enumerate(((0.2, 50), (0.33, 20))):
        x = 180 + 720 * fx
        c.poly([(x, 240), (x + w, 240), (x + w - 200, 1310), (x - 200, 1310)], (255, 255, 255), f"gl{i}", line=False, alpha=50)
    c.rect(130, 1380, 820, 200, (236, 234, 228), "sink")


def s_prep(c, t, T):
    shake(c, T, amt=2.5)
    if t < 1.6:         # washing the face
        c.rect(-40, -40, W + 80, H + 80, (186, 196, 186), "bwall", line=False)
        c.poly(c.ell(540, 1100, 470, 300), (236, 234, 228), "basin")
        c.poly(c.ell(540, 1080, 380, 220), (200, 214, 214), "basinin")
        c.rect(490, 640, 100, 200, (170, 172, 176), "tap")
        c.line([(540, 840), (540 + math.sin(t * 30) * 4, 1050)], "water", lw=22, color=(170, 200, 220), alpha=200)
        up = ease((t - 0.5) / 0.4) * (1 - ease((t - 1.2) / 0.3))
        y = lerp(1500, 1000, up)
        pov_arm(c, -1, 420, y, "open", ang=0.35)
        pov_arm(c, 1, 660, y, "open", ang=-0.35)
        if 0.8 < t < 1.5:
            rr = random.Random(int(t * FPS))
            for i in range(14):
                x, yy = rr.uniform(80, 1000), rr.uniform(100, 1700)
                c.poly(c.ell(x, yy, rr.uniform(12, 30), rr.uniform(16, 38)), (190, 216, 232), f"drop{i}", alpha=150, world=False)
    elif t < 3.2:       # orange jumpsuit on
        k = (t - 1.6) / 1.6
        c.rect(-40, -40, W + 80, H + 80, (196, 186, 150), "awall2", line=False)
        z = lerp(0.8, 2.6, ease(k / 0.75))
        c.zoom, c.zc = z, (540, 900)
        c.poly([(260, 520), (820, 520), (900, 640), (860, 1500), (220, 1500), (180, 640)], ORANGE, "jacket")
        c.poly([(400, 520), (680, 520), (620, 640), (460, 640)], WHITE, "jcollar")
        c.line([(540, 640), (540, 1500)], "zip", lw=6)
        c.poly([(300, 760), (420, 760), (420, 820), (300, 820)], ORANGE_D, "pocket", line=False)
        c.zoom = 1.0
        if k < 0.75:
            pov_arm(c, -1, 300, 1000, "fist", ang=0.5)
            pov_arm(c, 1, 780, 1000, "fist", ang=-0.5)
        else:
            c.overlay(ORANGE, (1 - (k - 0.75) / 0.25) * 255)
    elif t < 4.6:       # tying the headband
        k = (t - 3.2) / 1.4
        c.rect(-40, -40, W + 80, H + 80, (196, 186, 150), "awall3", line=False)
        y = lerp(900, -300, ease((k - 0.5) / 0.4))
        c.poly([(150, y - 40), (930, y - 40), (930, y + 40), (150, y + 40)], BAND, "hb")
        c.poly([(400, y - 80), (680, y - 80), (680, y + 80), (400, y + 80)], METAL, "hbplate")
        leaf_mark(c, 540, y, 2.2, "hbleaf")
        pov_arm(c, -1, 200, y + 120, "fist", ang=0.9)
        pov_arm(c, 1, 880, y + 120, "fist", ang=-0.9)
    else:               # quick look in the mirror
        mirror_naruto(c, T, t)
        if t > 5.4:
            r = 30 * abs(math.sin(t * 8))
            c.poly([(760, 520 - r), (770, 510), (760 + r, 520), (770, 530), (760, 520 + r), (750, 530), (760 - r, 520), (750, 510)],
                   (255, 246, 200), "sparkle")
    time_sign(c, "07:00")
    return dict(warm=1.0, light=(0.5, 0.1))


def village_street(c, reverse=False):
    sky = (200, 214, 214)
    c.rect(-80, -80, W + 160, 900, sky, "sky", line=False)
    # Hokage cliff far away
    c.poly([(-80, 640), (120, 380), (380, 330), (700, 340), (980, 380), (1160, 640)], (170, 146, 118), "cliff")
    for i in range(4):
        x = 200 + i * 220
        c.poly(c.ell(x, 470, 60, 70), (184, 160, 130), f"face{i}")
    # road
    c.poly([(-80, 1960), (1160, 1960), (640, 780), (440, 780)], (190, 168, 132), "road")
    houses = [(-1, (214, 190, 150), (170, 80, 60)), (1, (200, 180, 160), (110, 120, 110))]
    for sgn, col, roof in houses:
        for d in range(3):
            f = 1 / (1 + d * 0.9)
            xi = 540 + sgn * 420 * f
            xo = 540 + sgn * 900 * f
            top = 900 - 620 * f
            c.poly([(xi, top + 120 * f), (xo, top), (xo, 900 + 700 * f), (xi, 900 + 300 * f)], col, f"house{sgn}{d}")
            c.poly([(xi, top + 120 * f), (xo, top), (xo + sgn * 60 * f, top - 70 * f), (xi + sgn * 20 * f, top + 60 * f)], roof, f"roof{sgn}{d}")
            c.rect(min(xi, xo) + abs(xo - xi) * 0.35, top + 260 * f, abs(xo - xi) * 0.25, 180 * f, (120, 100, 80), f"door{sgn}{d}")
            if d == 1:
                c.poly(c.ell((xi + xo) / 2, top - 90 * f, 70 * f, 60 * f), (150, 160, 170), f"tank{sgn}")


def s_village(c, t, T):
    turned = t >= 3.55
    if not turned:
        shake(c, T, walk=1.0)
        c.zoom, c.zc = 1 + t * 0.05, (540, 900)
        village_street(c)
        # villagers stare coldly
        for i, (x, y, s, sgn) in enumerate(((230, 980, 0.62, 1), (870, 1000, 0.6, -1), (120, 1250, 0.9, 1), (960, 1280, 0.85, -1))):
            if i >= 2 and t < 1.0:
                continue
            anime(c, x, y, s, VILLAGERS[i], expr="cold", look=sgn * 0.6, key=f"vil{i}")
        c.zoom = 1.0
        if t > 3.3:   # whip-pan around
            speed_lines(c, "whip", r0=300, alpha=170)
    else:
        shake(c, T, amt=2.5)
        village_street(c)
        anime(c, 540, 820, 1.05, "iruka", expr="smile", talk=talk("s3a", T),
              arms=("wave", "down"), t=t)
        if t < 3.75:
            speed_lines(c, "whip2", r0=300, alpha=150)
        if speaking("s3b", T) or t > 5.0:
            f = ease((t - 4.9) / 0.3)
            pov_arm(c, 1, lerp(950, 820, f), lerp(2100, 1250, f), "open", ang=-0.2 + math.sin(t * 10) * 0.25)
    time_sign(c, "08:00")
    return dict(warm=0.9, light=(0.3, 0.05))


def s_klasse(c, t, T):
    shake(c, T, amt=2)
    pan = -ease((t - 2.0) / 0.4) * 220
    c.ox += pan
    c.rect(-80, -40, W + 400, 1500, (198, 184, 156), "cwall", line=False)
    c.rect(-40, 200, 800, 420, (70, 92, 80), "board")
    c.rect(-40, 620, 800, 26, (150, 110, 80), "chalk")
    c.rect(880, 200, 420, 560, (226, 220, 200), "cwin")
    c.rect(905, 225, 370, 510, (214, 226, 220), "cwing")
    c.glow(1080, 480, 420, (255, 236, 190), 80)
    c.rect(-80, 1400, W + 400, 600, (160, 126, 96), "cfloor", line=False)
    # Sakura greets, Sasuke sits coolly at the side
    anime(c, 360, 860, 1.0, "sakura", expr="smile" if not speaking("s4b", T) else "flat",
          talk=talk("s4a", T), arms=("down", "wave" if t < 2.0 else "down"), t=t)
    anime(c, 920, 900, 0.95, "sasuke", expr="cool", talk=talk("s4c", T), arms=("cross", "cross"), look=0.8 if t < 4.5 else -0.3)
    c.poly([(640, 1300), (1300, 1280), (1300, 1500), (640, 1520)], (150, 110, 80), "desk")
    c.hatch([(640, 1440), (1300, 1420), (1300, 1500), (640, 1520)], "deskh")
    c.ox -= pan
    if t >= 2.1:
        f = ease((t - 2.1) / 0.3)
        jab = math.sin(t * 14) * 15 if speaking("s4b", T) else 0
        pov_arm(c, 1, lerp(980, 560 + jab, f), lerp(2100, 1330, f), "point", ang=0.5)
    time_sign(c, "09:00")
    return dict(warm=1.0, light=(0.95, 0.2))


def bowl(c, x, y, s, key, full=True, t=0.0):
    c.poly([(x - 190 * s, y), (x + 190 * s, y), (x + 130 * s, y + 120 * s), (x - 130 * s, y + 120 * s)], (200, 90, 70), key + "body")
    c.ellipse(x, y, 190 * s, 46 * s, (236, 220, 180) if full else (210, 190, 160), key + "soup")
    if full:
        for i in range(5):
            c.line(c.ell(x - 30 * s + i * 14 * s, y, 90 * s, 18 * s, a0=0.2, a1=2.8), key + f"nd{i}", lw=4, color=(220, 190, 110), passes=1)
        c.circle(x + 80 * s, y - 6 * s, 30 * s, (250, 244, 230), key + "fish")
        c.line(c.ell(x + 80 * s, y - 6 * s, 14 * s, 14 * s, a0=0, a1=5), key + "fishs", lw=3, color=(220, 120, 140))
        c.ellipse(x - 80 * s, y - 4 * s, 34 * s, 22 * s, (250, 240, 220), key + "egg")
        c.circle(x - 80 * s, y - 4 * s, 12 * s, (240, 180, 70), key + "yolk", line=False)
        c.poly([(x - 10 * s, y - 40 * s), (x + 30 * s, y - 40 * s), (x + 25 * s, y + 10 * s), (x - 15 * s, y + 10 * s)], (60, 80, 60), key + "nori")
        steam(c, x, y - 40 * s, t, key + "st", h=240 * s)


def s_ramen(c, t, T):
    shake(c, T, amt=2)
    c.rect(-40, -40, W + 80, H + 80, (170, 140, 108), "rbg", line=False)
    c.rect(-40, 360, W + 80, 900, (200, 176, 140), "kitchen", line=False)
    c.glow(540, 500, 520, (255, 220, 160), 90)
    tk = talk("s5b", T)
    anime(c, 540, 700, 0.85, "teuchi", expr="happy", talk=tk, arms=("down", "down"))
    anime(c, 150, 930, 0.8, "sakura", expr="happy" if t > 4 else "smile", look=0.4, key="sak5")
    anime(c, 930, 930, 0.8, "sasuke", expr="cool", look=-0.5, key="sas5")
    # noren curtains
    for i in range(6):
        x = -20 + i * 186
        c.poly([(x, -40), (x + 176, -40), (x + 176, 300 + (i % 2) * 10), (x, 300)], (232, 222, 196), f"noren{i}")
    c.rect(-40, 1180, W + 80, 120, (176, 128, 84), "counter")
    c.rect(-40, 1300, W + 80, 700, (150, 104, 66), "counterfront")
    c.hatch([(-40, 1300), (1120, 1300), (1120, 1420), (-40, 1420)], "ch")
    # stack of empty bowls grows
    stack = 2 + (1 if t > 3.5 else 0)
    for i in range(stack):
        c.poly(c.ell(140, 1170 - i * 46, 110, 30), (200, 90, 70), f"emp{i}")
    new = t >= 5.0
    if t < 2.6 or new:
        yy = 1220 if not new else lerp(900, 1220, ease((t - 5.0) / 0.35))
        bowl(c, 560, yy, 1.1, "bowl", t=t)
        slurp = 0.5 + 0.5 * math.sin(t * 9)
        if not new:
            pov_arm(c, 1, 760, lerp(1150, 980, slurp), "fist", ang=-0.5, item="chopsticks")
        pov_arm(c, -1, 280, 1320, "fist", ang=0.3)
    else:
        f = ease((t - 2.6) / 0.35) * (1 - ease((t - 4.6) / 0.35))
        bx, by = 560, lerp(1220, 1000, f)
        bowl(c, bx, by, 1.0, "emptybowl", full=False)
        pov_arm(c, -1, bx - 200, by + 140, "fist", ang=0.6)
        pov_arm(c, 1, bx + 200, by + 140, "fist", ang=-0.6)
    time_sign(c, "12:00")
    return dict(warm=1.15, light=(0.5, 0.25))


def forest_bg(c, depth=0.0, key="fo"):
    c.rect(-80, -80, W + 160, H + 160, (150, 168, 130), key + "bg", line=False)
    c.glow(700, 300, 500, (255, 236, 180), 90)
    for i in range(5):
        x = (i * 260 + 60 + depth * (i - 2) * 140) % (W + 300) - 150
        w = 90 + (i % 3) * 30
        c.poly([(x - w / 2, -60), (x + w / 2, -60), (x + w / 2 + 20, 1500), (x - w / 2 - 20, 1500)], (110, 92, 70), key + f"tr{i}")
        c.hatch([(x + 10, -60), (x + w / 2, -60), (x + w / 2 + 20, 1500), (x + 10, 1500)], key + f"trh{i}", spacing=14)
    for i in range(6):
        c.poly(c.ell(80 + i * 190, 120 + (i % 2) * 60, 170, 110), (120, 148, 100), key + f"canopy{i}")
    c.rect(-80, 1450, W + 160, 600, (130, 150, 100), key + "ground", line=False)


def s_wald(c, t, T):
    if t < 1.7:      # kunai throw at a target
        shake(c, T, amt=2)
        forest_bg(c)
        tx, ty = 560, 760
        for r, col in ((110, (230, 220, 190)), (75, (190, 80, 70)), (40, (230, 220, 190)), (15, (190, 80, 70))):
            c.circle(tx, ty, r, col, f"tgt{r}")
        anime(c, 150, 1000, 0.75, "sasuke", expr="cool", look=0.6, key="sas6", arms=("down", "down"))
        anime(c, 940, 1000, 0.75, "sakura", expr="smile", look=-0.6, key="sak6", arms=("down", "up") if t > 1.25 else ("down", "down"))
        if t < 0.85:
            wind = ease((t - 0.3) / 0.45)
            pov_arm(c, 1, lerp(820, 940, wind), lerp(1300, 1500, wind), "fist", ang=lerp(-0.3, 0.4, wind), item="kunai")
        else:
            f = ease((t - 0.85) / 0.35)
            if f < 1:
                kx, ky = lerp(760, tx, f), lerp(1150, ty, f)
                s = lerp(1.0, 0.35, f)
                c.poly([(kx, ky - 90 * s), (kx + 14 * s, ky), (kx, ky + 40 * s), (kx - 14 * s, ky)], (110, 112, 120), "flyk", world=False)
            else:
                c.poly([(tx - 6, ty), (tx + 34, ty - 50), (tx + 46, ty - 40), (tx + 6, ty + 10)], (60, 60, 66), "stuck")
                c.circle(tx + 52, ty - 56, 12, (60, 60, 66), "stuckr")
            pov_arm(c, 1, lerp(940, 700, ease((t - 0.85) / 0.2)), lerp(1500, 1200, ease((t - 0.85) / 0.2)), "open", ang=-0.4)
    elif t < 3.6:    # running across branches
        k = t - 1.7
        shake(c, T, run=1.0)
        forest_bg(c, depth=k * 3, key="fr")
        sc = 1 + (k * 2.2 % 1) * 2
        c.poly([(540 - 120 * sc, 1960), (540 + 120 * sc, 1960), (540 + 40 * sc, 1300), (540 - 40 * sc, 1300)], (120, 96, 70), "branch")
        c.poly([(540 - 400, 1960), (540 + 400, 1960), (600, 1250), (480, 1250)], (130, 104, 76), "branch2")
        c.hatch([(540 - 400, 1960), (540, 1960), (540, 1250), (480, 1250)], "brh", spacing=16)
        anime(c, 420, 900 - abs(math.sin(k * 6)) * 80, 0.45, "sasuke", expr="cool", key="sasrun", arms=("down", "down"))
        anime(c, 700, 950 - abs(math.sin(k * 6 + 1)) * 80, 0.42, "sakura", expr="smile", key="sakrun", arms=("down", "down"))
        speed_lines(c, "run", r0=420, alpha=110)
        for i in range(6):
            r = random.Random(int(t * FPS) + i)
            c.poly(c.ell(r.uniform(0, W), r.uniform(0, H), 26, 12, rot=r.uniform(0, 3)), (150, 170, 100), f"fl{i}", world=False)
    else:            # Kakashi turns up late
        shake(c, T, amt=2)
        forest_bg(c, key="fk")
        c.poly([(-80, 1300), (1160, 1260), (1160, 1520), (-80, 1560)], (120, 96, 70), "kbranch")
        anime(c, 130, 960, 0.8, "sasuke", expr="cool", look=0.5, key="sas6b", arms=("cross", "cross"))
        anime(c, 950, 960, 0.8, "sakura", expr="frown" if t > 5 else "smile", look=-0.5, key="sak6b", arms=("down", "down"))
        if t >= 3.95:
            anime(c, 540, 760, 0.95, "kakashi", expr="bored", arms=("down", "book"), t=t)
        if 3.7 <= t < 4.4:
            p = (t - 3.7) / 0.7
            for i in range(9):
                a = i * 0.7
                r = 120 + 180 * p
                c.circle(540 + math.cos(a) * r * 0.8, 780 + math.sin(a) * r * 0.6, 110 * (1 - p * 0.5), (220, 216, 210),
                         f"smoke{i}", alpha=int(240 * (1 - p)))
        if speaking("s6b", T):
            f = ease((T - VOICE["s6b"]["start"]) / 0.25)
            pov_arm(c, 1, lerp(980, 700, f), lerp(2100, 1150, f), "point", ang=-0.45 + math.sin(t * 14) * 0.08)
    time_sign(c, "14:00")
    return dict(warm=0.9, light=(0.65, 0.1))


def alley(c, k):
    c.rect(-80, -80, W + 160, H + 160, (210, 196, 170), "abg", line=False)
    c.poly([(-80, 1960), (1160, 1960), (620, 860), (460, 860)], (176, 160, 136), "aground")
    for sgn, col in ((-1, (190, 170, 140)), (1, (170, 150, 130))):
        c.poly([(540 + sgn * 640, -80), (540 + sgn * 80, 500), (540 + sgn * 80, 880), (540 + sgn * 640, 1960)], col, f"awall{sgn}")
        for d in range(4):
            f = ((d + k * 1.6) % 4) / 4
            x = 540 + sgn * lerp(90, 620, f ** 1.6)
            c.line([(x, lerp(500, -80, f ** 1.6)), (x, lerp(880, 1960, f ** 1.6))], f"seam{sgn}{d}", lw=3, alpha=120)
    c.line([(80, 300), (1000, 380)], "laundry", lw=3)
    for i, col in enumerate(((200, 120, 110), (120, 150, 190), (220, 210, 160))):
        x = 220 + i * 260
        c.poly([(x, 312 + i * 20), (x + 120, 322 + i * 20), (x + 110, 480 + i * 20), (x + 10, 470 + i * 20)], col, f"cloth{i}")


def s_katze(c, t, T):
    if t < 3.9:
        shake(c, T, run=1.0)
        alley(c, t)
        ph = t * 12
        cx = 540 + math.sin(t * 2.4) * 200
        sc = lerp(0.45, 0.9, t / 3.9)
        cy = lerp(1060, 1300, t / 3.9)
        if t < 2.4:
            c.poly([(760, 1180), (900, 1170), (910, 1300), (770, 1310)], (170, 130, 90), "crate")
        else:
            c.poly([(780, 1260), (930, 1210), (980, 1330), (820, 1380)], (170, 130, 90), "crate2")
            if t < 2.8:
                c.line([(700, 1150), (660, 1100)], "bang1", lw=6); c.line([(1000, 1150), (1050, 1100)], "bang2", lw=6)
        cat(c, cx, cy, sc, phase=ph)
        if t > 2.8:
            f = ease((t - 2.8) / 0.4)
            pov_arm(c, -1, lerp(150, 380, f), lerp(2050, 1250, f), "open", ang=0.2)
            pov_arm(c, 1, lerp(930, 700, f), lerp(2050, 1250, f), "open", ang=-0.2)
        speed_lines(c, "chase", r0=520, alpha=90)
    else:
        dive = t < 4.1
        shake(c, T, amt=10 if t < 4.5 else 4)
        alley(c, 3.9)
        if dive:
            c.overlay((240, 230, 210), 120)
        cat(c, 540, 900, 1.6, face=True)
        pov_arm(c, -1, 230, 1150, "open", ang=0.6)
        pov_arm(c, 1, 850, 1150, "open", ang=-0.6)
        if 4.75 <= t < 5.6:   # scratch!
            for i in range(3):
                x0 = 200 + i * 120
                c.line([(x0, 600 + i * 40), (x0 + 520, 1400 + i * 40)], f"scr{i}", lw=16, color=(200, 70, 60), alpha=200, world=False)
        if 4.0 <= t < 4.4:
            speed_lines(c, "grab", r0=380, alpha=170)
    time_sign(c, "17:00")
    return dict(warm=1.1, light=(0.2, 0.15))


def s_nacht(c, t, T):
    shake(c, T, amt=1.5)
    c.rect(-40, -40, W + 80, H + 80, (92, 80, 84), "nwall", line=False)
    # window with the Hokage rock in evening light
    x0, y0, x1, y1 = 110, 260, 970, 1220
    c.rect(x0 - 30, y0 - 30, x1 - x0 + 60, y1 - y0 + 60, (150, 130, 110), "nframe")
    sky = Image.new("RGBA", (x1 - x0, y1 - y0))
    a = Image.linear_gradient("L").resize(sky.size)
    top, bot = Image.new("RGBA", sky.size, (110, 96, 140, 255)), Image.new("RGBA", sky.size, (236, 160, 110, 255))
    c.img.paste(Image.composite(bot, top, a), (int(x0 + c.ox), int(y0 + c.oy)))
    c.poly([(x0, 800), (x0 + 60, 560), (x0 + 250, 470), (x1 - 250, 460), (x1 - 60, 540), (x1, 800)], (170, 120, 96), "rock")
    for i, hs in enumerate(("spike", "bun", "short", "spike")):
        fx = x0 + 150 + i * 190
        c.poly(c.ell(fx, 620, 66, 80), (196, 140, 110), f"hf{i}")
        c.line([(fx - 24, 600), (fx - 8, 600)], f"hfe1{i}", lw=4); c.line([(fx + 8, 600), (fx + 24, 600)], f"hfe2{i}", lw=4)
        c.line([(fx - 14, 650), (fx + 14, 650)], f"hfm{i}", lw=4)
        if hs == "spike":
            c.poly([(fx - 60, 570), (fx - 40, 510), (fx - 10, 545), (fx + 15, 500), (fx + 40, 545), (fx + 62, 520), (fx + 62, 580)],
                   (180, 128, 100), f"hfh{i}")
    for i in range(8):
        hx = x0 + i * 115
        c.poly([(hx, y1), (hx, 900 + (i % 3) * 40), (hx + 50, 860 + (i % 3) * 40), (hx + 105, 900 + (i % 3) * 40), (hx + 105, y1)],
               (70, 60, 72), f"roofs{i}")
        if i % 2 == 0:
            c.rect(hx + 35, 1000 + (i % 3) * 30, 34, 34, (250, 210, 130), f"lw{i}", line=False)
    c.line([(540, y0), (540, y1)], "nbar", lw=10, color=(150, 130, 110), passes=1)
    c.rect(x0 - 60, y1 + 20, x1 - x0 + 120, 70, (130, 112, 96), "sill")
    c.glow(540, 700, 520, (250, 180, 120), 60)
    # lamp on the right
    c.rect(930, 1350, 40, 300, (120, 110, 100), "lampst")
    c.poly([(860, 1360), (1040, 1360), (1000, 1230), (900, 1230)], (240, 210, 150), "shade")
    lamp_on = t < 5.45
    if lamp_on:
        c.glow(950, 1300, 300, (255, 220, 150), 110)
    pov_arm(c, -1, 330, 1400, "fist", ang=0.2)
    if t < 4.9:
        pov_arm(c, 1, 760, 1420, "fist", ang=-0.2)
    else:
        f = ease((t - 4.9) / 0.45)
        pov_arm(c, 1, lerp(760, 960, f), lerp(1420, 1240, f), "point", ang=lerp(-0.2, -0.05, f))
    time_sign(c, "20:30")
    dark = 0.0
    if not lamp_on:
        c.overlay((10, 8, 16), 170)
        dark = ease((t - 5.6) / 0.6)
    return dict(warm=0.7, light=(0.85, 0.65), dark=dark)


FN = dict(intro=s_intro, wake=s_wake, prep=s_prep, village=s_village, klasse=s_klasse, ramen=s_ramen,
          wald=s_wald, katze=s_katze, nacht=s_nacht)


def render(i):
    T = i / FPS
    name, a, b = next((s for s in SCENES if s[1] <= T < s[2]), SCENES[-1])
    c = Canvas(W, H, i)
    grade = FN[name](c, T - a, T) or {}
    c.finish(**grade).save(os.path.join(FRAMES, f"{i:05d}.png"), compress_level=1)


def main():
    os.makedirs(FRAMES, exist_ok=True)
    idx = [int(x) for x in sys.argv[1:]] or list(range(int(TOTAL * FPS)))
    with Pool() as p:
        for k, _ in enumerate(p.imap_unordered(render, idx, chunksize=3)):
            if k % 100 == 0:
                print(k, "/", len(idx), flush=True)


if __name__ == "__main__":
    main()
