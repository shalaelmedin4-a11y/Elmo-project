"""Render all frames of the video as PNGs (12 fps, paper cut-out style)."""
import json, math, os, random, sys
from multiprocessing import Pool
from PIL import Image
from paper import Canvas
from character import boy, SKIN, JACKET, INK, WHITE
from script_data import FPS_ANIM, W, H

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
FRAMES = os.path.join(BUILD, "frames")
TL = json.load(open(os.path.join(BUILD, "timeline.json")))

BOY_C = (300, 450)  # sprite centre


def lerp(a, b, f):
    return a + (b - a) * max(0.0, min(1.0, f))


def ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def to_screen(px, py, cx, cy, s, angle=0.0, sx=1.0, sy=1.0):
    """Sprite point -> screen point for a sprite pasted with paste_sprite."""
    dx, dy = (px - BOY_C[0]) * s * sx, (py - BOY_C[1]) * s * sy
    a = math.radians(angle)
    return cx + dx * math.cos(a) + dy * math.sin(a), cy - dx * math.sin(a) + dy * math.cos(a)


def put_boy(c, s, cx, cy, angle=0.0, sx=1.0, sy=1.0, **pose):
    spr = boy(c.frame, **pose)
    if s != 1:
        spr = spr.resize((int(spr.width * s), int(spr.height * s)), Image.BICUBIC)
    c.paste_sprite(spr, cx, cy, angle, sx, sy)


# ---------------------------------------------------------------- scenery
def town(c, x, y, w, h, night=False):
    sky = (28, 34, 82) if night else (255, 196, 170)
    t = Canvas(w, h, c.frame, bg=sky)
    t.shadow = (5, 6)
    t.boil = c.boil
    if night:
        for i in range(14):
            r = random.Random(i)
            t.star(r.uniform(0, w), r.uniform(0, h * 0.45), 9, (255, 245, 180), f"st{i}", shadow=False)
        t.circle(w * 0.78, h * 0.18, 34, (250, 245, 210), "moon")
    else:
        t.circle(w * 0.25, h * 0.42, 50, (255, 236, 160), "sun", shadow=False)
    m = (90, 90, 150) if night else (178, 168, 210)
    t.tri([(-60, h * 0.62), (w * 0.3, h * 0.2), (w * 0.7, h * 0.62)], m, "mt1")
    t.tri([(w * 0.35, h * 0.62), (w * 0.75, h * 0.26), (w + 80, h * 0.62)], m, "mt2")
    t.tri([(w * 0.22, h * 0.31), (w * 0.3, h * 0.2), (w * 0.38, h * 0.31)], (245, 245, 255), "mts1")
    t.tri([(w * 0.67, h * 0.36), (w * 0.75, h * 0.26), (w * 0.83, h * 0.36)], (245, 245, 255), "mts2")
    snow = (220, 228, 250) if night else (252, 252, 255)
    t.rect(-20, h * 0.66, w + 40, h * 0.4, snow, "ground", amt=6)
    houses = [(0.08, 0.13, (160, 82, 45)), (0.4, 0.16, (120, 62, 40)), (0.72, 0.14, (176, 104, 60))]
    for i, (fx, fw, col) in enumerate(houses):
        hx, hw, hb = fx * w, fw * w, h * 0.78
        hh = hw * 0.75
        t.rect(hx, hb - hh, hw, hh, col, f"h{i}")
        t.tri([(hx - 12, hb - hh + 4), (hx + hw / 2, hb - hh - hw * 0.55), (hx + hw + 12, hb - hh + 4)], (90, 40, 40), f"r{i}")
        t.tri([(hx - 16, hb - hh - 4), (hx + hw / 2, hb - hh - hw * 0.6), (hx + hw + 16, hb - hh - 4)], (255, 255, 255), f"rs{i}", shadow=False)
        win = (255, 215, 90) if night else (120, 190, 230)
        t.rect(hx + hw * 0.3, hb - hh * 0.65, hw * 0.4, hh * 0.35, win, f"w{i}", shadow=False)
    for i, fx in enumerate((0.3, 0.6, 0.92, 0.0)):
        px, base = fx * w, h * 0.86
        for k in range(3):
            ww = 55 - k * 13
            yy = base - k * 34
            t.tri([(px - ww, yy), (px, yy - 60), (px + ww, yy)], (30, 105, 60), f"p{i}{k}")
            t.tri([(px - ww * 0.4, yy - 36), (px, yy - 60), (px + ww * 0.4, yy - 36)], (255, 255, 255), f"ps{i}{k}", shadow=False)
    for i in range(22):
        r = random.Random(100 + i)
        sx = (r.uniform(0, w) + math.sin(c.frame * 0.3 + i) * 10) % w
        sy = (r.uniform(0, h) + c.frame * r.uniform(5, 9)) % h
        t.circle(sx, sy, r.uniform(4, 7), (255, 255, 255), f"sf{i}", shadow=False)
    c.img.paste(t.img, (int(x), int(y)))


def window_frame(c, x, y, w, h, col=(250, 250, 250), night=False):
    c.rect(x - 24, y - 24, w + 48, h + 48, col, "winframe")
    town(c, x, y, w, h, night)
    c.thick_line((x + w / 2, y), (x + w / 2, y + h), 16, col, "winbar1")
    c.thick_line((x, y + h / 2), (x + w, y + h / 2), 16, col, "winbar2")
    c.rect(x - 40, y + h + 10, w + 80, 30, col, "sill")


def tiles(c, col, line, y1):
    c.rect(-10, -10, W + 20, y1 + 10, col, "tiles", amt=2, shadow=False)
    for i in range(0, W + 1, 135):
        c.thick_line((i, 0), (i, y1), 5, line, f"tv{i}", shadow=False)
    for j in range(0, y1 + 1, 135):
        c.thick_line((0, j), (W, j), 5, line, f"th{j}", shadow=False)


def subtitle(c, scene, t):
    segs = scene["segments"]
    for i, g in enumerate(segs):
        nxt = segs[i + 1]["start"] if i + 1 < len(segs) else 99
        end = g["end"] + 0.5
        if nxt - g["end"] < 0.7:
            end = nxt
        if g["start"] - 0.05 <= t < end:
            c.text(g["text"], W / 2, 1640, 70, sw=9)
            return


def seg(scene, i):
    return scene["segments"][i]["start"], scene["segments"][i]["end"]


# ---------------------------------------------------------------- scenes
EXP_PIECES = [(random.Random(i).uniform(-1, 1), random.Random(i + 50).uniform(-1.2, 0.3),
               random.Random(i + 99).choice([(225, 40, 40), (250, 210, 50), (30, 30, 30), (200, 200, 200)]),
               random.Random(i + 7).uniform(14, 34)) for i in range(30)]


def alarm_clock(c, cx, cy, s, key, ring=0.0, digits="6:30"):
    sh = math.sin(c.frame * 2.7) * 9 * ring
    cx += sh
    for k, dx in (("L", -0.75), ("R", 0.75)):
        c.circle(cx + dx * 120 * s, cy - 105 * s - abs(sh), 52 * s, (250, 205, 40), key + "bell" + k)
    c.thick_line((cx, cy - 150 * s), (cx + sh * 2, cy - 120 * s), 14 * s, (60, 60, 60), key + "ham")
    c.rect(cx - 150 * s, cy - 95 * s, 300 * s, 200 * s, (225, 40, 40), key + "body", amt=4)
    c.rect(cx - 115 * s, cy - 55 * s, 230 * s, 115 * s, (20, 20, 25), key + "disp", amt=3)
    c.text(digits, cx, cy + 2 * s, int(84 * s), fill=(90, 255, 120), stroke=(20, 60, 30), sw=2)
    c.rect(cx - 130 * s, cy + 100 * s, 40 * s, 30 * s, (60, 60, 60), key + "fl")
    c.rect(cx + 90 * s, cy + 100 * s, 40 * s, 30 * s, (60, 60, 60), key + "fr")


def bedroom(c, night_dark=False):
    c.rect(-10, -10, W + 20, 1420, (40, 44, 92), "wall", shadow=False)
    for i in range(0, W, 90):
        c.thick_line((i + 45, 0), (i + 45, 1400), 14, (48, 54, 105), f"stripe{i}", shadow=False)
    c.rect(-10, 1400, W + 20, 600, (82, 58, 70), "floor", shadow=False)
    window_frame(c, 560, 230, 380, 420, col=(200, 200, 215), night=True)


def bed(c, x0=330):
    c.rect(x0 - 40, 820, 60, 560, (130, 76, 44), "headboard")
    c.rect(x0, 1180, 1100 - x0, 200, (150, 90, 52), "bedframe")
    c.rect(x0, 1100, 1100 - x0, 110, (240, 240, 250), "mattress")


def scene_alarm(c, sc, t):
    bedroom(c)
    bed(c)
    t_exp, t_jump, t_land = 1.2, 1.3, 1.85
    # boy lying in bed before the jump
    if t < t_jump:
        c.ellipse(470, 1070, 120, 60, (250, 250, 255), "pillow")
        put_boy(c, 0.62, 560, 1060, angle=90, eyes="closed" if t < 0.5 else "wide", mouth="small")
        c.rect(560, 1040, 540, 170, (70, 140, 220), "blanket")
        for i in range(4):
            c.thick_line((640 + i * 110, 1045), (640 + i * 110, 1205), 18, (250, 205, 40), f"bst{i}", shadow=False)
        if t < 0.45:
            for i in range(3):
                c.text("z", 500 + i * 55, 900 - i * 60 - (c.frame % 4) * 6, 50 + i * 15, fill=(220, 220, 255), sw=4)
    else:
        c.rect(560, 1060, 540, 150, (70, 140, 220), "blanket2")
    # nightstand + clock
    c.rect(20, 1130, 260, 260, (150, 96, 58), "stand")
    c.rect(40, 1200, 220, 60, (120, 72, 40), "drawer")
    if t < t_exp:
        ring = 1.0 if t > 0.25 else 0.0
        alarm_clock(c, 150, 1010, 0.82, "clk", ring)
        if ring:
            c.text("RIIING!", 430, 760 + (c.frame % 2) * 12, 92, fill=(255, 230, 60), sw=8, angle=8 * ((c.frame % 2) * 2 - 1))
            for i in range(5):
                a = -math.pi / 2 + (i - 2) * 0.45
                r0, r1 = 210, 260 + (c.frame % 2) * 30
                c.thick_line((150 + math.cos(a) * r0, 950 + math.sin(a) * r0),
                             (150 + math.cos(a) * r1, 950 + math.sin(a) * r1), 10, (255, 255, 255), f"rl{i}", shadow=False)
    else:
        te = t - t_exp
        for i, (vx, vy, col, size) in enumerate(EXP_PIECES):
            x = 150 + vx * 900 * te
            y = 1010 + vy * 1500 * te + 2200 * te * te
            y = min(y, 1440 + (i % 5) * 60)
            c.star(x, y, size, col, f"pc{i}", points=3, inner=0.6, rot=te * 8 * vx if y < 1440 else vx)
        if te < 0.5:
            c.text("KA-BUMM!", 380, 820, 120, fill=(255, 120, 40), sw=10, angle=-10)
        if te < 0.17:
            c.overlay((255, 250, 220), 220 * (1 - te / 0.17))
    # the jump
    if t >= t_jump:
        f = ease((t - t_jump) / (t_land - t_jump))
        x = lerp(560, 640, f)
        y = lerp(1060, 1050, f) - math.sin(f * math.pi) * 520
        ang = lerp(90, -360 if f < 1 else 0, f) if f < 1 else 0
        landed = t >= t_land
        squash = 1.0
        if landed and t - t_land < 0.25:
            squash = 0.85
        put_boy(c, 0.78, x, y + (1 - squash) * 200, angle=ang if not landed else 0, sy=squash,
                eyes="dot", mouth="flat" if landed else "open", mouth_open=0.6, brows=landed,
                arm_l=(0, 0) if landed else (150, 160), arm_r=(150, -160) if landed else (-150, -160))


def scene_water(c, sc, t):
    t_splash, t_freeze, t_scream, t_after = 0.6, 0.95, 2.9, 4.2
    freeze = t_freeze <= t < t_scream
    if freeze:
        c.boil = 9999  # the whole world freezes
    tiles(c, (150, 215, 215), (120, 190, 195), 1300)
    c.rect(-10, 1300, W + 20, 700, (95, 140, 170), "bathfloor", shadow=False)
    window_frame(c, 330, 140, 420, 360, col=(255, 255, 255))
    frozen = 0.0
    if t >= t_freeze:
        frozen = 1.0 if t < t_scream else max(0.35, 1 - (t - t_scream) * 0.4)
    pose = dict(eyes="dot", mouth="small", frozen=frozen)
    shake = 0
    if t < t_splash:
        pose.update(arm_l=(20, 40), arm_r=(-20, -40))
    elif t < t_freeze:
        pose.update(arm_l=(150, -150), arm_r=(-150, 150), eyes="closed")
    elif freeze:
        pose.update(arm_l=(150, -150), arm_r=(-150, 150), eyes="dot")
    elif t < t_after:
        pose.update(arm_l=(160, 175), arm_r=(-160, -175), eyes="wide", mouth="open", mouth_open=0.7 + 0.3 * (c.frame % 2))
        shake = 16
    else:
        pose.update(arm_l=(25, 30), arm_r=(-25, -30), eyes="dot", mouth="flat")
        shake = 4
    sx = (random.Random(c.frame).uniform(-1, 1)) * shake
    put_boy(c, 1.2, 540 + sx, 1000, **pose)
    # sink
    c.rect(500, 1050, 80, 90, (190, 195, 205), "tap")
    c.rect(420, 1030, 160, 40, (190, 195, 205), "tap2")
    c.ellipse(540, 1180, 330, 70, (245, 248, 255), "basin")
    c.rect(210, 1180, 660, 160, (245, 248, 255), "basin2")
    c.rect(470, 1340, 140, 300, (230, 233, 245), "pedestal")
    if t_splash <= t < t_freeze + 0.25:
        f = (t - t_splash) / 0.6
        for i in range(16):
            r = random.Random(i)
            a = r.uniform(0, 2 * math.pi)
            d = 120 + f * r.uniform(150, 380)
            c.circle(540 + math.cos(a) * d * 1.2, 780 + math.sin(a) * d, r.uniform(14, 26), (90, 180, 255), f"drop{i}")
        c.text("PLATSCH!", 540, 470, 100, fill=(140, 220, 255), sw=9, angle=6)
    if freeze:
        c.overlay((180, 220, 255), 70)
        c.text("...", 850, 660, 90, fill=(255, 255, 255), sw=6)
    if t_scream <= t < t_after:
        c.text("AAAAAHH!", 540 + sx, 420, 130, fill=(255, 80, 80), sw=10, angle=(c.frame % 2) * 6 - 3)
        for i in range(8):
            a = i * math.pi / 4 + 0.3
            c.thick_line((540 + math.cos(a) * 330, 780 + math.sin(a) * 300),
                         (540 + math.cos(a) * 420, 780 + math.sin(a) * 380), 12, (255, 255, 255), f"sl{i}", shadow=False)
    if t >= t_after:
        for i in range(3):
            yy = 860 + ((t - t_after) * 300 + i * 60) % 200
            c.ellipse(430 + i * 110, yy, 9, 14, (90, 180, 255), f"drip{i}", shadow=False)


BOTTLE_COLS = [(240, 90, 140), (90, 200, 220), (250, 200, 60), (150, 110, 230), (100, 210, 120), (250, 140, 60),
               (230, 230, 240), (240, 110, 110), (120, 160, 250), (255, 170, 200), (80, 190, 170), (200, 120, 200)]


def scene_cream(c, sc, t):
    tiles(c, (250, 205, 215), (230, 180, 195), 1300)
    c.rect(-10, 1300, W + 20, 700, (150, 110, 150), "bathfloor2", shadow=False)
    c.rect(150, 120, 780, 300, (250, 250, 255), "lightbar")
    for i in range(4):
        c.circle(260 + i * 186, 270, 60, (255, 240, 170), f"bulb{i}")
    t0, t1 = 0.5, 3.4
    cream = ease((t - t0) / (t1 - t0))
    busy = t0 <= t < t1
    flail = (c.frame % 2)
    pose = dict(cream=cream, eyes="dot", mouth="small",
                arm_l=(150, -150) if (busy and flail) else (130, -110),
                arm_r=(-130, 110) if (busy and flail) else (-150, 150))
    if not busy:
        pose.update(arm_l=(20, 30), arm_r=(-20, -30))
    if t > t1 + 0.6:
        pose["eyes"] = "closed" if (c.frame // 3) % 6 == 0 else "dot"
    put_boy(c, 1.15, 540, 1000, **pose)
    # counter with twelve products
    c.rect(-10, 1290, W + 20, 90, (245, 245, 250), "counter")
    for i, col in enumerate(BOTTLE_COLS):
        bx = 55 + i * 88
        hgt = 120 + (i * 53 % 90)
        hop = 0
        tb = t0 + i * (t1 - t0) / 12
        if busy:
            hop = 40 * max(0, math.sin(min(math.pi, (t - tb) * 3 * math.pi))) if t > tb else 0
            hop += 12 * ((c.frame + i) % 2)
        top = 1290 - hgt - hop
        c.rect(bx - 32, top, 64, hgt, col, f"bot{i}", amt=2)
        c.rect(bx - 14, top - 32, 28, 34, (60, 60, 70) if i % 3 else (240, 240, 245), f"cap{i}", amt=2)
        c.rect(bx - 22, top + hgt * 0.35, 44, hgt * 0.3, (255, 255, 255), f"lab{i}", amt=2, shadow=False)
        # cream squirting toward the face
        if busy and t > tb:
            for k in range(3):
                f = ((t - tb) * 2.2 + k / 3) % 1
                x = lerp(bx, 540 + (i - 5.5) * 18, f)
                y = lerp(top - 40, 860, f) - math.sin(f * math.pi) * 260
                c.circle(x, y, 18, (252, 252, 248), f"sq{i}{k}")
    if busy:
        c.text("SPLURT!", 220 + (c.frame % 3) * 300, 560, 64, fill=(255, 255, 255), stroke=(200, 80, 140), sw=7,
               angle=(c.frame % 2) * 10 - 5)


def fried_egg(c, x, y, key, s=1.0):
    c.ellipse(x, y, 100 * s, 32 * s, (255, 254, 245), key + "w", amt=0.08)
    c.ellipse(x + 8 * s, y - 8 * s, 30 * s, 18 * s, (255, 170, 20), key + "y", amt=0.05)


def scene_eggs(c, sc, t):
    c.rect(-10, -10, W + 20, 1200, (255, 214, 110), "kwall", shadow=False)
    for i in range(0, W, 120):
        c.rect(i + 10, 0, 50, 1200, (255, 222, 135), f"kst{i}", shadow=False)
    window_frame(c, 120, 170, 360, 330, col=(255, 255, 255))
    c.rect(600, 140, 380, 240, (180, 110, 70), "cupboard")
    c.rect(615, 155, 170, 210, (200, 130, 85), "cupL")
    c.rect(795, 155, 170, 210, (200, 130, 85), "cupR")
    c.rect(-10, 1200, W + 20, 800, (150, 100, 70), "kfloor", shadow=False)
    t0, t1 = 0.55, sc["dur"] - 0.5
    eaten = int(max(0, min(14, (t - t0) / ((t1 - t0) / 14))))
    phase = ((t - t0) / ((t1 - t0) / 14)) % 1 if t0 <= t < t1 else 0
    chewing = t0 <= t < t1
    pose = dict(eyes="dot", mouth="chew" if chewing else "flat", mouth_open=(c.frame % 2), brows=True)
    if chewing:
        pose.update(arm_r=(60, 30) if phase < 0.45 else (160, -125), arm_l=(30, 60))
    else:
        pose.update(arm_r=(30, 60), arm_l=(30, 60))
    bx, by, s = 360, 960, 1.0
    put_boy(c, s, bx, by, **pose)
    c.rect(-20, 1130, W + 40, 60, (205, 140, 80), "tabletop")
    c.rect(-20, 1190, W + 40, 200, (175, 110, 60), "tablefront")
    # the tower
    c.ellipse(770, 1125, 150, 34, (235, 240, 250), "plate")
    remaining = 14 - eaten
    for i in range(remaining):
        wob = math.sin(c.frame * 0.9 + i * 0.7) * i * 1.6
        fried_egg(c, 770 + wob, 1100 - i * 30, f"egg{i}")
    if chewing and phase >= 0.45 and eaten < 14:
        mx, my = to_screen(380, 344, bx, by, s)
        fried_egg(c, mx + 30, my, "fork", 0.55)
    # counter UI
    fried_egg(c, 770, 600 - 380, "icon", 0.6)
    c.text(f"x {remaining}", 900, 205, 64, fill=(255, 255, 255), sw=7)
    if chewing and c.frame % 4 < 2:
        c.text("MAMPF", 150, 720, 60, fill=(255, 255, 255), stroke=(170, 90, 30), sw=6, angle=8)


def scene_pushup(c, sc, t):
    c.rect(-10, -10, W + 20, 1240, (150, 120, 190), "lwall", shadow=False)
    for i in range(0, W, 100):
        c.thick_line((i, 0), (i, 1230), 10, (160, 132, 200), f"lws{i}", shadow=False)
    c.rect(330, 220, 420, 300, (120, 70, 40), "pframe")
    c.rect(355, 245, 370, 250, (180, 220, 250), "pic")
    c.tri([(380, 480), (520, 300), (660, 480)], (250, 250, 255), "picmt")
    c.rect(80, 760, 920, 300, (210, 70, 70), "couchback")
    c.rect(40, 960, 1000, 200, (190, 55, 60), "couchseat")
    c.rect(40, 900, 110, 260, (175, 50, 55), "armL")
    c.rect(930, 900, 110, 260, (175, 50, 55), "armR")
    c.rect(-10, 1230, W + 20, 800, (170, 120, 80), "lfloor", shadow=False)
    for i in range(0, W, 160):
        c.thick_line((i, 1230), (i - 80, 1960), 6, (150, 100, 65), f"plank{i}", shadow=False)
    c.ellipse(540, 1420, 470, 110, (60, 170, 160), "rug")
    c.ellipse(540, 1420, 400, 85, (80, 195, 180), "rug2", shadow=False)
    floor = 1420
    s = 0.95
    t_down, t_up, t_buckle, t_flat = 1.4, 1.85, 2.35, 2.55
    collapsed = t >= t_flat
    if t < t_down:
        lift = 1.0
    elif t < t_up:
        lift = lerp(1.0, 0.45, (t - t_down) / (t_up - t_down))
    elif t < t_buckle:
        lift = lerp(0.45, 0.95, (t - t_up) / (t_buckle - t_up))
    elif t < t_flat:
        lift = lerp(0.95, 0.0, (t - t_buckle) / (t_flat - t_buckle))
    else:
        lift = 0.0
    tremble = random.Random(c.frame).uniform(-1, 1) * (5 if t < t_buckle else 0)
    angle = lerp(-90, -76, lift)
    arm_len = 170
    cy = floor - 158 - lift * 170 + tremble
    cx = 500
    sh_far = to_screen(428, 470, cx, cy, s, angle)
    sh_near = to_screen(428, 530, cx, cy, s, angle)
    # hands on the floor
    hx = sh_near[0] + 10
    if not collapsed:
        bend = 1 - lift
        for key, sh, col in (("far", sh_far, (220, 100, 15)), ("near", None, None)):
            if sh is None:
                continue
            elbow = (sh[0] + 40 * bend + 20, (sh[1] + floor) / 2)
            c.thick_line(sh, elbow, 56, col, key + "u")
            c.thick_line(elbow, (hx + 40, floor - 15), 52, col, key + "l")
            c.circle(hx + 40, floor - 15, 28, SKIN, key + "h")
    put_boy(c, s, cx, cy, angle=angle, sy=0.86 if collapsed and t - t_flat < 0.3 else 1.0, arms=False,
            eyes="x" if collapsed else "squint", mouth="flat" if not collapsed else "open",
            mouth_open=0.2, brows=not collapsed)
    if not collapsed:
        bend = 1 - lift
        elbow = (sh_near[0] + 40 * bend + 20, (sh_near[1] + floor) / 2)
        c.thick_line(sh_near, elbow, 60, JACKET, "nearu")
        c.thick_line(elbow, (hx, floor - 10), 56, JACKET, "nearl")
        c.circle(hx, floor - 10, 30, SKIN, "nearh")
    else:
        c.thick_line(sh_near, (sh_near[0] + 170, floor - 5), 44, JACKET, "flatarm")
        c.circle(sh_near[0] + 190, floor - 5, 24, SKIN, "flathand")
    if t < t_down and t > 0.3:
        c.text("1 / 100", 540, 620, 90, fill=(255, 255, 255), sw=8)
    elif t_up <= t < t_flat:
        c.text("1 / 100", 540, 620, 90, fill=(120, 255, 120), sw=8)
    if collapsed and t - t_flat < 0.7:
        f = (t - t_flat) / 0.7
        for i in range(6):
            dx = (i - 2.5) * 70 * (0.5 + f)
            c.circle(cx + dx, floor - 30 - f * 50, 30 + 20 * f, (235, 220, 200), f"dust{i}", alpha=int(255 * (1 - f)))
        c.text("PLUMPS!", 540, 900, 110, fill=(255, 220, 80), sw=10, angle=-6)
    if collapsed and t >= t_flat + 0.7:
        # awkward silence: a lone cricket
        if t < seg(sc, 1)[0]:
            c.text("*zirp*", 860, 1100, 52, fill=(220, 255, 200), sw=5)
        for i in range(3):
            a = c.frame * 0.6 + i * 2.1
            c.star(cx + 230 + math.cos(a) * 70, cy - 60 + math.sin(a) * 25, 22, (255, 230, 60), f"dz{i}", points=5, inner=0.45)


SPARK = [(random.Random(i).uniform(120, 960), random.Random(i + 9).uniform(300, 1350), random.Random(i + 33).uniform(0, 1)) for i in range(14)]


def scene_pose(c, sc, t):
    t_pose, t_spark = seg(sc, 0)[0], seg(sc, 1)[0] - 0.2
    c.rect(-10, -10, W + 20, 1460, (60, 40, 110), "pwall", shadow=False)
    if t >= t_pose:
        for i, (r, col) in enumerate(((760, (110, 60, 160)), (560, (170, 80, 170)), (360, (240, 120, 170)))):
            c.circle(360, 860, r + math.sin(c.frame * 0.8 + i) * 12, col, f"spot{i}", shadow=False)
    c.rect(-10, 1450, W + 20, 600, (90, 60, 70), "pfloor", shadow=False)
    # full length mirror
    mx, my, mw, mh = 690, 520, 320, 940
    c.rect(mx - 26, my - 26, mw + 52, mh + 52, (170, 110, 50), "mframe")
    c.rect(mx, my, mw, mh, (190, 225, 245), "glass", shadow=False)
    posed = t >= t_pose
    wind = 1.0 if t >= t_pose + 0.2 else 0.0
    pose = dict(eyes="squint" if posed else "dot", mouth="smirk" if posed else "small", brows=posed, wind=wind,
                arm_l=(-45, 40) if posed else (20, 10), arm_r=(140, 145) if posed else (-20, -10))
    refl = boy(c.frame, **pose).transpose(Image.FLIP_LEFT_RIGHT)
    refl = refl.resize((int(refl.width * 0.62), int(refl.height * 0.62)), Image.BICUBIC)
    glass = c.img.crop((mx, my, mx + mw, my + mh))
    glass.alpha_composite(refl, (mw // 2 - refl.width // 2, mh - refl.height - 10))
    tint = Image.new("RGBA", glass.size, (190, 225, 245, 70))
    glass.alpha_composite(tint)
    c.img.paste(glass, (mx, my))
    c.tri([(mx + 30, my + 60), (mx + 90, my + 60), (mx + 20, my + 200)], (255, 255, 255), "glint", shadow=False, alpha=140)
    put_boy(c, 1.0, 330, 1080, **pose)
    if wind:
        for i in range(7):
            r = random.Random(i)
            y = r.uniform(250, 1350)
            x = (r.uniform(0, W) + c.frame * 140) % (W + 400) - 200
            c.thick_line((x, y), (x + 160, y), 8, (255, 255, 255), f"wind{i}", shadow=False, alpha=180)
    if t >= t_spark:
        for i, (x, y, ph) in enumerate(SPARK):
            p = ((t - t_spark) * 1.6 + ph) % 1
            r = 50 * math.sin(p * math.pi)
            if r > 4:
                c.star(x, y, r, (255, 245, 150) if i % 2 else (255, 255, 255), f"spk{i}", rot=p)
    if seg(sc, 2)[0] - 0.1 <= t:
        c.text("100% PERFEKT", 540, 230, 86, fill=(255, 230, 90), stroke=(120, 40, 120), sw=9, angle=4)


def scene_night(c, sc, t):
    t_reach = seg(sc, 2)[1] - 0.55
    t_off = seg(sc, 2)[1] + 0.1
    c.rect(-10, -10, W + 20, 1420, (24, 26, 60), "nwall", shadow=False)
    for i in range(0, W, 90):
        c.thick_line((i + 45, 0), (i + 45, 1400), 14, (30, 33, 72), f"nstripe{i}", shadow=False)
    c.rect(-10, 1400, W + 20, 600, (52, 38, 50), "nfloor", shadow=False)
    window_frame(c, 560, 230, 380, 420, col=(150, 150, 175), night=True)
    bed(c)
    c.ellipse(470, 1070, 120, 60, (250, 250, 255), "pillow")
    bcx, bcy, s, ang = 560, 1060, 0.62, 90
    put_boy(c, s, bcx, bcy, angle=ang, mask=True, eyes="wide", mouth="small", look=(0, -8))
    c.rect(560, 1040, 540, 170, (70, 140, 220), "blanket")
    for i in range(4):
        c.thick_line((640 + i * 110, 1045), (640 + i * 110, 1205), 18, (250, 205, 40), f"bst{i}", shadow=False)
    # nightstand, new clock (the old one exploded), lamp
    c.rect(20, 1130, 260, 260, (150, 96, 58), "stand")
    c.rect(40, 1200, 220, 60, (120, 72, 40), "drawer")
    alarm_clock(c, 205, 1075, 0.36, "nclk", digits="22:00")
    c.rect(70, 1000, 30, 130, (200, 200, 210), "lampstick")
    c.tri([(10, 1010), (160, 1010), (120, 890), (50, 890)], (250, 220, 120), "lampshade")
    lamp_on = t < t_off
    if t_reach <= t:
        f = ease((t - t_reach) / 0.45)
        shoulder = (590, 1050)
        hand = (lerp(590, 125, f), lerp(1050, 1015, f))
        c.thick_line(shoulder, hand, 40, JACKET, "reach")
        c.circle(hand[0], hand[1], 22, SKIN, "reachh")
    if lamp_on:
        c.overlay((255, 200, 120), 25)
        c.ellipse(85, 1060, 280, 220, (255, 235, 160), "glow", shadow=False, alpha=60)
    else:
        c.overlay((5, 5, 20), 225)
        for k, px in (("L", 242), ("R", 358)):
            ex, ey = to_screen(px, 280 - 3, bcx, bcy, s, ang)
            c.circle(ex, ey, 30 * s, WHITE, "glo" + k, shadow=False)
            c.circle(ex - 7, ey, 10 * s, INK, "glp" + k, shadow=False)
        if t > t_off + 0.15:
            c.text("*klick*", 160, 820, 54, fill=(200, 200, 220), sw=4)


SCENE_FN = dict(alarm=scene_alarm, water=scene_water, cream=scene_cream, eggs=scene_eggs,
                pushup=scene_pushup, pose=scene_pose, night=scene_night)


def render_frame(i):
    t = i / FPS_ANIM
    sc = next((s for s in TL["scenes"] if s["start"] <= t < s["start"] + s["dur"]), TL["scenes"][-1])
    lt = t - sc["start"]
    c = Canvas(W, H, i)
    SCENE_FN[sc["name"]](c, sc, lt)
    c.boil = i // 2
    subtitle(c, sc, lt)
    c.img.convert("RGB").save(os.path.join(FRAMES, f"{i:05d}.png"), compress_level=1)


def main():
    os.makedirs(FRAMES, exist_ok=True)
    n = int(math.ceil(TL["total"] * FPS_ANIM))
    idx = range(n)
    if len(sys.argv) > 1:
        idx = [int(a) for a in sys.argv[1:]]
    with Pool() as p:
        for k, _ in enumerate(p.imap_unordered(render_frame, idx, chunksize=4)):
            if k % 50 == 0:
                print(k, "/", len(idx), flush=True)


if __name__ == "__main__":
    main()
