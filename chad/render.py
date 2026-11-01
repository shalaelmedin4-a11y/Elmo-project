"""POV: Ein Tag als Chad – draws every frame (12 fps) with Pillow + numpy."""
import json, math, os, random, sys
from multiprocessing import Pool
from PIL import Image, ImageDraw
from paper import Canvas, INK
from chars import chad, person, pov_arm, open_hand, SKIN, HOODIE, WHITE

W, H, FPS = 1080, 1920, 12
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
FRAMES = os.path.join(BUILD, "frames")
VOICE = json.load(open(os.path.join(BUILD, "voices.json")))

SCENES = [("intro", 0, 4), ("wake", 4, 9), ("mirror", 9, 14), ("montage", 14, 18), ("bus", 18, 24),
          ("hall", 24, 30), ("lecture", 30, 35), ("home", 35, 41), ("field", 41, 50)]
TOTAL = 50.0

# characters
SKINS = [(247, 205, 170), (205, 145, 105), (240, 190, 150), (160, 105, 75), (250, 215, 185)]


def lerp(a, b, f):
    return a + (b - a) * max(0.0, min(1.0, f))


def ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def talk(lid, T):
    v = VOICE[lid]
    i = int((T - v["start"]) * FPS)
    return v["env"][i] if 0 <= i < len(v["env"]) else 0.0


def shake(c, T, walk=0.0, amt=3.0):
    r = random.Random(int(T * FPS) * 7 + 1)
    c.ox = r.uniform(-amt, amt) + math.sin(T * 2 * math.pi * 0.9) * 9 * walk
    c.oy = r.uniform(-amt, amt) + abs(math.sin(T * 2 * math.pi * 0.9)) * -18 * walk
    return c.ox, c.oy


def time_sign(c, txt):
    pts = [(40, 64), (330, 52), (338, 172), (46, 182)]
    c.shape(pts, (255, 246, 214), "tsign", amt=3, world=False)
    c.circle(188, 66, 11, (220, 60, 60), "tpin", world=False, ol=4)
    c.text(txt, 190, 120, 76, angle=1.5)


def reflection(c, T, cx, cy, s, mask_pts, alpha=1.0, tint=None, **kw):
    """Chad seen in glass: drawn on its own layer and clipped to the glass shape."""
    layer = Canvas(W, H, c.frame, transparent=True)
    layer.ox, layer.oy, layer.zoom, layer.zc = c.ox, c.oy, c.zoom, c.zc
    chad(layer, cx, cy, s, **kw)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(c.T(mask_pts), fill=int(255 * alpha))
    a = layer.img.getchannel("A")
    from PIL import ImageChops
    layer.img.putalpha(ImageChops.multiply(a, m))
    c.img.alpha_composite(layer.img)
    if tint:
        tl = Image.new("RGBA", (W, H), tint)
        tm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(tm).polygon(c.T(mask_pts), fill=tint[3])
        tl.putalpha(tm)
        c.img.alpha_composite(tl)


def glare(c, x0, y0, x1, y1, key):
    for i, (fx, w) in enumerate(((0.15, 60), (0.3, 25))):
        x = x0 + (x1 - x0) * fx
        c.shape([(x, y0 + 10), (x + w, y0 + 10), (x + w - 160, y1 - 10), (x - 160, y1 - 10)],
                (255, 255, 255), key + str(i), ol=0, shadow=False, alpha=70)


def sparkle(c, x, y, r, t, key, col=(255, 240, 120)):
    k = 0.6 + 0.4 * abs(math.sin(t * 9))
    c.star(x, y, r * k, col, key, rot=t * 2, ol=4)
    c.star(x + r * 0.9, y - r * 0.8, r * 0.4 * k, (255, 255, 255), key + "b", ol=3)


# ====================================================================== scenes
def s_intro(c, t, T):
    c.rect(-20, -20, W + 40, H + 40, (160, 212, 245), "ibg", ol=0, shadow=False)
    for i in range(22):
        r = random.Random(i)
        x, y = r.uniform(40, W - 40), r.uniform(60, H - 60)
        k = 0.5 + 0.5 * math.sin(t * 5 + i)
        c.star(x, y, 14 + 22 * k, (255, 255, 255) if i % 3 else (255, 235, 120), f"gl{i}", ol=4)
    # sign that slams in
    if t < 1.0:
        ts, kind = 0.0, "pov"
    elif t < 2.5:
        ts, kind = 1.0, "tag"
    else:
        ts, kind = 2.5, "halbo"
    k = t - ts
    z = [1.4, 1.12, 0.97, 1.0][min(3, int(k * FPS))]
    cx, cy = 540, 650
    w, h, col = dict(pov=(560, 300, WHITE), tag=(900, 470, WHITE), halbo=(820, 280, (226, 44, 54)))[kind]
    pts = [(cx - w / 2 * z, cy - h / 2 * z), (cx + w / 2 * z, cy - h / 2 * z),
           (cx + w / 2 * z, cy + h / 2 * z), (cx - w / 2 * z, cy + h / 2 * z)]
    c.poly(c.jag(pts, "sign" + kind, amt=9, step=26), col, world=False)
    if kind == "pov":
        c.text("POV:", cx, cy, int(200 * z), angle=-3)
    elif kind == "tag":
        c.text("EIN TAG", cx, cy - 95 * z, int(150 * z), angle=-2)
        c.text("ALS CHAD", cx, cy + 95 * z, int(150 * z), angle=-2)
    else:
        c.text("mit Halbo!", cx, cy, int(140 * z), fill=WHITE, angle=-4)
        for i in range(6):
            a = i * math.pi / 3 + t * 2
            sparkle(c, cx + math.cos(a) * 470, cy + math.sin(a) * 200, 34, t + i, f"hs{i}")
    # Chad pops up from below and winks
    if t >= 1.0:
        y = lerp(2350, 1360, ease((t - 1.0) / 0.45))
        wink = 1.0 if 3.0 <= t < 3.55 else 0.0
        tk = max(talk("intro1", T), talk("intro2", T), talk("intro3", T))
        chad(c, 540, y, 0.85, wink=wink, talk=tk)
        if 3.0 <= t < 3.7:
            sparkle(c, 640, y - 60, 40, t, "winkspark")


def bedroom(c, pan):
    c.rect(-60, -20, W + 700, H + 40, (250, 226, 182), "bwall", ol=0, shadow=False)
    x0 = 160 + pan
    c.rect(x0 - 30, 300, 640, 640, (255, 255, 255), "winf")
    c.rect(x0, 330, 580, 580, (150, 210, 250), "winsky", ol=4)
    c.circle(x0 + 400, 520, 90, (255, 225, 80), "sun")
    c.ellipse(x0 + 170, 700, 120, 40, WHITE, "cloud", ol=4)
    c.rect(x0 + 275, 330, 30, 580, (255, 255, 255), "winbar", ol=4)
    c.rect(x0 - 70, 270, 120, 720, (240, 120, 120), "curtL")
    c.rect(x0 + 550, 270, 120, 720, (240, 120, 120), "curtR")
    # sun beams
    for i in range(3):
        bx = x0 + 120 + i * 150
        c.shape([(bx, 920), (bx + 90, 920), (bx + 420, 1650), (bx + 200, 1650)], (255, 240, 150), f"beam{i}",
                ol=0, shadow=False, alpha=80)


def alarm_clock(c, x, y, ringing, t, pressed):
    j = math.sin(t * 60) * 8 if ringing else 0
    x += j
    for sx in (-1, 1):
        c.circle(x + sx * 105, y - 120, 46, (250, 205, 40), f"bell{sx}")
    c.rect(x - 22, y - 168 + (12 if pressed else 0), 44, 26, (90, 90, 100), "btn")
    c.rrect(x - 160, y - 130, 320, 220, 40, (230, 60, 60), "clock")
    c.rrect(x - 120, y - 90, 240, 120, 18, (30, 30, 36), "disp", ol=5)
    c.text("07:00", x + c.ox, y - 30 + c.oy, 78, fill=(120, 255, 140))
    if ringing:
        for i in range(4):
            a = -math.pi / 2 + (i - 1.5) * 0.5
            c.stroke([(x + math.cos(a) * 200, y - 70 + math.sin(a) * 170),
                      (x + math.cos(a) * 250, y - 70 + math.sin(a) * 215)], 9)


def s_wake(c, t, T):
    shake(c, T, amt=2)
    pan = -lerp(0, 520, ease((t - 1.0) / 0.45))
    bedroom(c, pan)
    sx = 1250 + pan
    c.rect(sx - 200, 1180, 400, 500, (170, 110, 70), "stand")
    c.rect(sx - 170, 1260, 340, 110, (150, 95, 60), "drawer")
    c.circle(sx, 1315, 16, (240, 200, 90), "knob", ol=4)
    pressed = t >= 1.75
    alarm_clock(c, sx, 1080, 0.15 < t < 1.75, t, pressed)
    # duvet in the foreground
    c.shape([(-40, 1560), (200, 1480), (520, 1530), (800, 1470), (1120, 1520), (1120, 1960), (-40, 1960)],
            (80, 140, 225), "duvet", amt=4, world=False)
    for i in range(5):
        c.circle(120 + i * 220, 1720 + (i % 2) * 70, 40, (255, 255, 255), f"dot{i}", world=False, ol=4)
    # the hand slaps the alarm
    if 1.35 <= t < 2.6:
        if t < 1.75:
            f = ease((t - 1.35) / 0.4)
        else:
            f = 1 - ease((t - 2.1) / 0.5)
        hx, hy = lerp(980, sx + c.ox, f), lerp(2050, 960 + c.oy + (14 if pressed and t < 2.0 else 0), f)
        pov_arm(c, 1, hx, hy, "open" if t < 1.75 else "open", ang=0.15)
    if t < 1.0:
        time_sign(c, "07:00")
    # waking-up blink
    o = [(0, 0.0), (0.25, 0.0), (0.45, 0.55), (0.6, 0.15), (0.95, 1.0)]
    op = 1.0
    for (t0, a0), (t1, a1) in zip(o, o[1:]):
        if t0 <= t < t1:
            op = lerp(a0, a1, (t - t0) / (t1 - t0))
    if op < 1:
        lid = Image.new("L", (W, H), 255)
        if op > 0.02:
            ry = op * 1150
            ImageDraw.Draw(lid).ellipse((-500, 960 - ry, W + 500, 960 + ry), fill=0)
        c.img.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (W, H), INK).split(), lid)))


def bathroom(c):
    c.rect(-30, -30, W + 60, H + 60, (200, 236, 226), "tiles", ol=0, shadow=False)
    for x in range(0, W + 1, 120):
        c.stroke([(x, -30), (x, H + 30)], 4, (170, 210, 200))
    for y in range(0, H + 1, 120):
        c.stroke([(-30, y), (W + 30, y)], 4, (170, 210, 200))


MIRROR = (110, 230, 970, 1440)


def mirror(c, T, s=1.15, extra=None, **kw):
    x0, y0, x1, y1 = MIRROR
    c.rrect(x0 - 34, y0 - 34, x1 - x0 + 68, y1 - y0 + 68, 40, (205, 205, 218), "mframe")
    c.rect(x0, y0, x1 - x0, y1 - y0, (200, 228, 238), "glass", ol=4, shadow=False)
    glass = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    reflection(c, T, 540, 800, s, glass, **kw)
    if extra:
        extra()
    glare(c, x0, y0, x1, y1, "mglare")
    # sink
    c.rrect(160, 1500, 760, 210, 60, (250, 250, 252), "sink")
    c.rrect(480, 1430, 120, 90, 20, (190, 195, 205), "tap")


def s_mirror(c, T, t):
    shake(c, T, amt=2)
    bathroom(c)

    def chin():
        if 1.2 <= t < 2.2:
            sparkle(c, 540 + 30, 800 + 228 * 1.15, 46, t, "chin")
    mirror(c, T, extra=chin, talk=talk("s2", T))
    if t >= 1.6:
        f = ease((t - 1.6) / 0.35)
        pov_arm(c, 1, lerp(900, 820, f), lerp(2100, 1430, f), "thumb", ang=-0.1)
    time_sign(c, "07:02")


def s_montage(c, t, T):
    shake(c, T, amt=3)
    cut = min(4, int(t / 0.8))
    k = (t - cut * 0.8) / 0.8
    c.zoom = [1.12, 1.04, 1.0][min(2, int(k * 0.8 * FPS))]
    if cut == 0:          # brushing teeth
        bathroom(c)

        def foam():
            bx = 540 + math.sin(t * 40) * 40
            for i in range(7):
                c.circle(bx - 60 + i * 20, 800 + 130 * 1.15 + (i % 2) * 14, 20, WHITE, f"foam{i}", ol=3)
            c.capsule((bx + 30, 945), (bx + 330, 1010), 16, (90, 200, 255), "brush")
        mirror(c, T, extra=foam)
        pov_arm(c, 1, 770 + math.sin(t * 40) * 40, 1560, "fist", ang=-0.6)
    elif cut == 1:        # hoodie on
        bedroom(c, 0)
        y = lerp(-200, -1500, ease(k * 1.3))
        c.shape([(-60, y), (W + 60, y), (W + 60, y + 1500), (540, y + 1620), (-60, y + 1500)], HOODIE, "hoodie",
                world=False, amt=6)
        c.rect(-60, y + 1430, W + 120, 70, (105, 170, 225), "hem", world=False)
        pov_arm(c, -1, 300, lerp(800, 1300, k), "open", ang=-0.2)
        pov_arm(c, 1, 780, lerp(800, 1300, k), "open", ang=0.2)
    elif cut == 2:        # hair swipe
        bathroom(c)

        def swipe():
            hx = lerp(240, 860, ease(k * 1.4))
            open_hand(c, hx, 520, 1.0, SKIN, 1, "swipe", ang=1.3)
            for i in range(3):
                sparkle(c, hx - 120 - i * 110, 470 + i * 25, 26 - i * 5, t + i, f"hs{i}")
        mirror(c, T, extra=swipe)
    elif cut == 3:        # grab the backpack
        c.rect(-30, -30, W + 60, H + 60, (250, 226, 182), "bwall2", ol=0, shadow=False)
        c.rect(-30, 1500, W + 60, 500, (190, 140, 100), "floor", ol=0, shadow=False)
        lift = ease((k - 0.5) / 0.4) * 300
        c.rrect(300, 760 - lift, 480, 620, 90, (250, 140, 40), "bag")
        c.rrect(370, 1040 - lift, 340, 260, 40, (225, 115, 25), "pocket")
        c.capsule((420, 760 - lift), (660, 760 - lift), 26, (90, 60, 40), "strap")
        hx, hy = lerp(820, 560, ease(k / 0.5)), lerp(1900, 760 - lift + 40, ease(k / 0.5))
        pov_arm(c, 1, hx, hy, "fist" if k > 0.5 else "open", ang=-0.2)
    else:                 # out the door
        c.rect(-30, -30, W + 60, H + 60, (255, 250, 230), "light", ol=0, shadow=False)
        c.rect(-30, 1400, W + 60, 600, (170, 210, 150), "lawn", ol=0, shadow=False)
        f = ease(k * 1.2)
        c.shape([(80, 100), (80 + 460 * (1 - f), 100 + 90 * f), (80 + 460 * (1 - f), 1800 - 90 * f), (80, 1800)],
                (140, 90, 55), "door", world=False)
        c.shape([(1000, 100), (1000 - 460 * (1 - f), 100 + 90 * f), (1000 - 460 * (1 - f), 1800 - 90 * f), (1000, 1800)],
                (140, 90, 55), "door2", world=False)
    c.zoom = 1.0
    time_sign(c, "07:05")


def bus_interior(c, f_walk):
    vx, vy = 540, 760
    c.rect(-40, -40, W + 80, H + 80, (230, 230, 225), "busbg", ol=0, shadow=False)
    # floor, ceiling, side walls in one-point perspective
    c.shape([(-60, H + 40), (W + 60, H + 40), (vx + 150, vy + 250), (vx - 150, vy + 250)], (120, 125, 135), "bfloor")
    c.shape([(-60, -40), (W + 60, -40), (vx + 150, vy - 230), (vx - 150, vy - 230)], (245, 245, 240), "bceil")
    for sgn in (-1, 1):
        c.shape([(540 + sgn * 600, -40), (vx + sgn * 150, vy - 230), (vx + sgn * 150, vy + 250), (540 + sgn * 600, H + 40)],
                (250, 205, 70), f"bwall{sgn}")
        c.shape([(540 + sgn * 600, 300), (vx + sgn * 150, vy - 150), (vx + sgn * 150, vy + 20), (540 + sgn * 600, 900)],
                (170, 220, 250), f"bwin{sgn}", ol=5)
    c.rect(vx - 150, vy - 230, 300, 480, (200, 200, 200), "bback")
    c.rect(vx - 110, vy - 180, 220, 200, (170, 220, 250), "bbackwin", ol=5)
    c.stroke([(80, 150), (vx - 120, vy - 200)], 12, (180, 180, 190))
    c.stroke([(1000, 150), (vx + 120, vy - 200)], 12, (180, 180, 190))


BUS_ROWS = [  # (depth at t=0, side, people)
    (2.9, -1, [dict(skin=SKINS[1], hair=(30, 25, 25), top=(90, 160, 90), style="curly")]),
    (2.9, 1, [dict(skin=SKINS[0], hair=(120, 80, 50), top=(200, 90, 90), style="bald", beard=True)]),
    (2.1, 1, [dict(skin=SKINS[2], hair=(60, 40, 30), top=(240, 130, 180), style="long", girl="whisper"),
              dict(skin=SKINS[4], hair=(230, 180, 90), top=(150, 120, 230), style="ponytail", girl="listen")]),
    (2.1, -1, [dict(skin=SKINS[3], hair=(20, 20, 20), top=(80, 100, 180), style="buzz")]),
    (1.5, -1, [dict(skin=SKINS[4], hair=(200, 120, 60), top=(240, 200, 80), style="bun", glasses=True)]),
]


def s_bus(c, t, T):
    if t < 3.4:
        shake(c, T, walk=1.0)
        bus_interior(c, t)
        travel = t * 0.32
        rows = sorted(BUS_ROWS, key=lambda r: -(r[0] - travel))
        for d0, side, people in rows:
            d = d0 - travel
            if d < 0.95:
                continue
            f = 1 / d
            sx = 540 + side * 330 * f
            top = 760 + 150 * f
            look = d < 2.3        # turns around once Chad gets close
            for i, p in enumerate(people):
                off = (i - (len(people) - 1) / 2) * 400 * f * (1 if side > 0 else -1)
                px = sx + off + side * 60 * f
                expr = "surprised" if look else "smile"
                arms = ("down", "down")
                if p.get("girl") == "whisper":
                    expr, arms = ("whisper", ("down", "mouth")) if int(t * 2) % 2 == 0 else ("smile", ("down", "mouth"))
                elif p.get("girl") == "listen":
                    expr = "smile"
                person(c, px, top - 80 * f, 1.2 * f, p["skin"], p["hair"], p["top"], style=p["style"], expr=expr,
                       glasses=p.get("glasses", False), beard=p.get("beard", False), arms=arms, key=f"bp{d0}{side}{i}", t=t)
            sw = 520 * f * (1.6 if len(people) > 1 else 1)
            c.rrect(sx + side * 60 * f - sw / 2, top + 110 * f, sw, 520 * f, 40 * f, (60, 110, 200), f"seat{d0}{side}")
        c.stroke([(380, 0), (380, 1000)], 14, (200, 200, 205))
        c.stroke([(700, 0), (700, 1000)], 14, (200, 200, 205))
    else:
        # sitting at the window: city rushes by, Chad's reflection in the glass
        shake(c, T, amt=2.5)
        c.rect(-40, -40, W + 80, H + 80, (250, 205, 70), "bwall", ol=0, shadow=False)
        x0, y0, x1, y1 = 90, 330, 990, 1330
        c.rrect(x0 - 40, y0 - 40, x1 - x0 + 80, y1 - y0 + 80, 50, (170, 170, 180), "wframe")
        c.rect(x0, y0, x1 - x0, y1 - y0, (150, 205, 245), "wsky", ol=4, shadow=False)
        scroll = (t - 3.4) * 900
        for i in range(8):
            bx = x0 + ((i * 260 - scroll) % 2080) - 300
            bh = 280 + (i * 97 % 300)
            col = [(240, 150, 120), (150, 170, 220), (240, 220, 140), (180, 150, 210)][i % 4]
            if bx < x1 and bx + 220 > x0:
                bl, br = max(x0, bx), min(x1, bx + 220)
                c.rect(bl, y1 - bh, br - bl, bh, col, f"bld{i}", ol=4, shadow=False)
                for wy in range(int(y1 - bh + 40), int(y1 - 40), 90):
                    for wx in (bx + 40, bx + 130):
                        if bl < wx < br - 50:
                            c.rect(wx, wy, 50, 50, (255, 250, 200), f"bw{i}{wy}{wx}", ol=3, shadow=False)
        glass = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        reflection(c, T, 560, 760, 1.0, glass, alpha=0.55, tint=(200, 230, 255, 40), talk=talk("s4", T))
        glare(c, x0, y0, x1, y1, "bglare")
        c.rect(-40, 1450, W + 80, 520, (60, 110, 200), "seatfront", world=False)
    time_sign(c, "07:30")


def s_hall(c, t, T):
    shake(c, T, amt=2.5)
    vx, vy = 540, 780
    c.rect(-40, -40, W + 80, H + 80, (235, 235, 240), "hbg", ol=0, shadow=False)
    c.shape([(-60, H + 40), (W + 60, H + 40), (vx + 170, vy + 260), (vx - 170, vy + 260)], (200, 190, 175), "hfloor")
    c.shape([(-60, -40), (W + 60, -40), (vx + 170, vy - 260), (vx - 170, vy - 260)], (250, 250, 245), "hceil")
    for sgn, col in ((-1, (90, 150, 220)), (1, (240, 110, 90))):
        c.shape([(540 + sgn * 600, -40), (vx + sgn * 170, vy - 260), (vx + sgn * 170, vy + 260), (540 + sgn * 600, H + 40)],
                (225, 225, 230), f"hw{sgn}")
        for i in range(5):
            d0, d1 = 1 + i * 0.6, 1 + (i + 1) * 0.6
            xa, xb = vx + sgn * 530 / d0, vx + sgn * 530 / d1
            c.shape([(xa, vy - 520 / d0), (xb, vy - 520 / d1), (xb, vy + 620 / d1), (xa, vy + 620 / d0)],
                    col, f"lock{sgn}{i}", ol=5)
            for k in range(3):
                yy = vy - 400 / d0 + k * 40 / d0
                c.stroke([(xa + sgn * -20 / d0, yy), (xa + sgn * -120 / d0, yy)], 5, INK)
    c.rect(vx - 170, vy - 260, 340, 520, (240, 240, 245), "hend")
    c.rect(vx - 70, vy - 120, 140, 380, (150, 100, 70), "hdoor")
    # the two friends walk up
    f = ease(t / 2.4)
    s = lerp(0.5, 1.05, f)
    walk = math.sin(t * 9) * 12 * (1 - f)
    raised = t >= 2.9
    clap = 3.5 <= t < 3.9
    person(c, lerp(470, 330, f), lerp(800, 760, f) + walk, s, SKINS[3], (25, 20, 20), (60, 170, 110), style="buzz",
           expr="happy_closed" if clap else "smile", talk=talk("s5a", T), arms=("down", "highfive" if raised else "down"),
           key="frA", t=t)
    person(c, lerp(610, 790, f), lerp(810, 780, f) - walk, s * 0.95, SKINS[0], (230, 170, 80), (250, 150, 60),
           style="curly", expr="smile", arms=("down", "down"), key="frB", t=t)
    if raised:
        k = ease((t - 2.95) / 0.5)
        hx, hy = lerp(900, 560, k), lerp(2100, 820, k)
        pov_arm(c, 1, hx, hy, "open", ang=-0.25)
    if clap:
        for i in range(8):
            a = i * math.pi / 4
            c.stroke([(560 + math.cos(a) * 170, 640 + math.sin(a) * 170),
                      (560 + math.cos(a) * 240, 640 + math.sin(a) * 240)], 10, (255, 220, 60))
    time_sign(c, "08:00")


def s_lecture(c, t, T):
    shake(c, T, amt=2)
    c.rect(-40, -40, W + 80, H + 80, (215, 185, 145), "lwall", ol=0, shadow=False)
    c.rect(90, 180, 900, 470, (40, 90, 70), "board")
    c.rect(90, 650, 900, 30, (160, 120, 80), "chalkrail")
    # students in the back rows
    clapping = t >= 2.3
    for row, (yy, s) in enumerate(((1000, 0.42), (1120, 0.5))):
        for i in range(4):
            x = 120 + i * 280 + row * 140
            if 360 < x < 720 and row == 1:
                continue
            person(c, x, yy, s, SKINS[(i + row) % 5], [(40, 30, 20), (200, 140, 60), (20, 20, 20), (150, 80, 40)][i],
                   [(120, 160, 230), (230, 120, 140), (130, 200, 140), (240, 200, 90)][(i + row) % 4],
                   style=["short", "long", "curly", "buzz"][(i + row) % 4], expr="happy_closed" if clapping else "smile",
                   arms=("clap", "clap") if clapping else ("down", "down"), key=f"st{row}{i}", t=t + i)
        c.rect(-40, yy + 150 * s * 2, W + 80, 120, (150, 105, 70), f"row{row}")
    # the lecturer
    hand_it = 1.1 <= t < 1.8
    person(c, 540, 820, 1.1, SKINS[0], (170, 90, 50), (60, 160, 160), style="bun", glasses=True,
           expr="smile", arms=("down", "thumb" if t >= 2.0 else ("hold" if hand_it else "down")), key="doz", t=t)
    # desk + Chad's hands
    c.shape([(-60, 1420), (W + 60, 1380), (W + 60, H + 40), (-60, H + 40)], (190, 135, 85), "desk", world=False)
    if t >= 1.1:
        k = ease((t - 1.1) / 0.6)
        px, py = lerp(560, 540, k), lerp(1150, 1560, k)
        ang = lerp(-0.3, 0.06, k)
        sc = lerp(0.6, 1.0, k)
        pts = [(-260, -330), (260, -330), (260, 330), (-260, 330)]
        ca, sa = math.cos(ang), math.sin(ang)
        pp = [(px + (x * ca - y * sa) * sc, py + (x * sa + y * ca) * sc * 0.55) for x, y in pts]
        c.shape(pp, (252, 252, 248), "test", world=False)
        for i in range(5):
            y = -230 + i * 70
            a = (px + (-200 * ca - y * sa) * sc, py + (-200 * sa + y * ca) * sc * 0.55)
            b = (px + (60 * ca - y * sa) * sc, py + (60 * sa + y * ca) * sc * 0.55)
            c.stroke([a, b], 6, (170, 170, 190), world=False)
        if t >= 1.3:
            c.text("1+", px + 150 * sc, py + 40 * sc * 0.55, int(190 * sc), fill=(225, 40, 40), angle=-8)
    pov_arm(c, -1, 230, 1700, "fist", ang=0.4)
    pov_arm(c, 1, 870, 1720, "fist", ang=-0.4)
    if t < 1.3:
        time_sign(c, "11:00")


def burger(c, x, y, s=1.0):
    P = lambda pts: [(x + a * s, y + b * s) for a, b in pts]
    c.rrect(x - 190 * s, y + 40 * s, 380 * s, 70 * s, 30 * s, (230, 160, 70), "bunb")
    c.rrect(x - 200 * s, y - 20 * s, 400 * s, 70 * s, 30 * s, (110, 60, 35), "patty")
    c.shape(P([(-200, -20), (200, -20), (170, 30), (120, -5), (60, 40), (0, -5), (-70, 35), (-130, -5), (-190, 25)]),
            (255, 205, 50), "cheese")
    c.shape(P([(-215, -40), (-150, -70), (-80, -40), (0, -72), (80, -40), (150, -70), (215, -40), (200, -10), (-200, -10)]),
            (110, 200, 80), "lettuce")
    c.rrect(x - 185 * s, y - 85 * s, 370 * s, 40 * s, 18 * s, (230, 60, 60), "tomato")
    c.poly(c.ell(x, y - 85 * s, 205 * s, 170 * s, "buntop", a0=math.pi, a1=2 * math.pi), (235, 165, 70))
    for i in range(7):
        c.ellipse(x + (-120 + i * 40) * s, y - (150 + (i % 3) * 30) * s, 11 * s, 6 * s, WHITE, f"ses{i}", ol=2, shadow=False)


def s_home(c, t, T):
    shake(c, T, walk=1.0 - ease(t / 1.2), amt=2)
    c.zoom = lerp(0.9, 1.0, ease(t / 1.2))
    c.rect(-80, -80, W + 160, H + 160, (255, 222, 175), "hwall", ol=0, shadow=False)
    c.rect(-80, 1350, W + 160, 700, (180, 120, 80), "hfloor2", ol=0, shadow=False)
    c.rect(60, 250, 260, 330, (255, 255, 255), "hwin")
    c.rect(80, 270, 220, 290, (170, 220, 250), "hwinsky", ol=4)
    c.rect(780, 260, 220, 200, (170, 110, 70), "frame")
    c.poly(c.ell(860, 345, 30, 30, "ht1"), (240, 80, 110))
    c.poly(c.ell(920, 345, 30, 30, "ht2"), (240, 80, 110))
    c.shape([(832, 360), (948, 360), (890, 430)], (240, 80, 110), "ht3")
    c.rect(930, 600, 20, 560, (120, 120, 130), "lampstick")
    c.shape([(860, 610), (1020, 610), (980, 480), (900, 480)], (255, 230, 140), "lampshade")
    mom_t = talk("s7a", T)
    chad_line = VOICE["s7b"]["start"] <= T
    person(c, 330, 760, 1.0, SKINS[2], (120, 60, 40), (240, 130, 160), style="bun", expr="happy_closed" if chad_line else "smile",
           talk=mom_t, arms=("down", "down"), key="mom", t=t)
    person(c, 760, 740, 1.02, SKINS[0], (90, 70, 50), (90, 150, 100), style="short", beard=True,
           expr="happy_closed" if chad_line else "smile", arms=("down", "down"), key="dad", t=t)
    c.rect(-60, 1180, W + 120, 80, (170, 105, 60), "table")
    c.rect(-60, 1260, W + 120, 500, (150, 90, 50), "tablefront")
    c.ellipse(470, 1185, 280, 60, (245, 245, 250), "plate")
    burger(c, 470, 1060, 1.05)
    c.shape([(760, 1000), (960, 1000), (930, 1200), (790, 1200)], (230, 40, 40), "friesbox")
    for i in range(7):
        fx = 780 + i * 27
        c.rect(fx, 880 + (i % 3) * 30, 24, 150, (255, 215, 70), f"fry{i}", ol=4, shadow=False)
    c.shape([(760, 1000), (960, 1000), (945, 1080), (775, 1080)], (230, 40, 40), "friesbox2")
    c.zoom = 1.0
    # the front door swings open
    if t < 0.75:
        f = ease(t / 0.75)
        c.shape([(0, 0), (W * (1 - f) + 20, 80 * f), (W * (1 - f) + 20, H - 80 * f), (0, H)], (140, 90, 55), "fdoor",
                world=False)
        c.circle(W * (1 - f) - 80, 1000, 26, (240, 200, 90), "fknob", world=False)
    time_sign(c, "14:00")


def s_field(c, t, T):
    if t < 4.2:
        shake(c, T, amt=2.5)
        c.rect(-40, -40, W + 80, 1000, (150, 210, 250), "fsky", ol=0, shadow=False)
        c.ellipse(220, 260, 140, 50, WHITE, "fc1", ol=4)
        c.ellipse(830, 180, 110, 40, WHITE, "fc2", ol=4)
        c.rect(-40, 900, W + 80, 1100, (110, 190, 90), "grass", ol=0, shadow=False)
        c.rect(-40, 1500, W + 80, 220, (210, 90, 70), "track")
        for y in (1560, 1640):
            c.stroke([(-40, y), (W + 40, y)], 6, WHITE)
        raised = t >= 1.0
        fans = [(150, (205, 145, 105), (30, 25, 25), (240, 120, 170), "long", "heart"),
                (410, (250, 215, 185), (230, 180, 90), (150, 120, 230), "ponytail", "chad"),
                (670, (240, 190, 150), (120, 60, 40), (90, 190, 200), "bun", "chad"),
                (930, (160, 105, 75), (20, 20, 20), (250, 200, 80), "curly", "heart")]
        for i, (x, sk, hr, top, st, sign) in enumerate(fans):
            jump = abs(math.sin(t * 7 + i)) * 25 if raised else 0
            arms = ("sign", "sign") if sign == "chad" else ("down", "highfive") if i == 0 else ("highfive", "down")
            person(c, x, 740 - jump, 0.9, sk, hr, top, style=st, expr="cheer" if raised else "smile",
                   arms=arms, key=f"fan{i}", t=t + i)
            if sign == "heart":
                hx, hy = x + (90 if i == 0 else -90) + math.sin(t * 6 + i) * 15, 430 - jump
                c.poly(c.ell(hx - 40, hy - 20, 48, 48, f"h1{i}"), (255, 90, 140))
                c.poly(c.ell(hx + 40, hy - 20, 48, 48, f"h2{i}"), (255, 90, 140))
                c.shape([(hx - 86, hy), (hx + 86, hy), (hx, hy + 110)], (255, 90, 140), f"h3{i}")
                c.stroke([(hx, hy + 100), (hx, hy + 230)], 12, (150, 100, 60))
        jump = abs(math.sin(t * 7 + 1.5)) * 25 if raised else 0
        sx, sy = 540, 1000 - jump
        if raised:
            c.rect(sx - 260, sy - 110, 520, 220, WHITE, "chadsign")
            c.text("CHAD", sx + c.ox, sy + c.oy, 150, fill=(225, 40, 60), angle=-3)
        else:
            c.rect(sx - 260, sy + 40, 520, 160, (230, 225, 210), "signback")
        # fence in front of them
        c.rect(-40, 1180, W + 80, 26, (150, 150, 160), "rail")
        for x in (10, 280, 790, 1050):   # no post through the CHAD sign
            c.rect(x, 900, 24, 520, (150, 150, 160), f"post{x}")
        mesh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(mesh)
        for k in range(-30, 40):
            x = k * 60
            d.line([(x + c.ox, 1200 + c.oy), (x + 220 + c.ox, 1420 + c.oy)], fill=(70, 70, 80, 120), width=4)
            d.line([(x + c.ox, 1420 + c.oy), (x + 220 + c.ox, 1200 + c.oy)], fill=(70, 70, 80, 120), width=4)
        c.img.alpha_composite(mesh)
        c.rect(-40, 1410, W + 80, 26, (150, 150, 160), "rail2")
        # lazy wave back
        if 2.0 <= t < 3.8:
            k = ease((t - 2.0) / 0.3) * (1 - ease((t - 3.5) / 0.3))
            wave = math.sin(t * 9) * 0.35
            pov_arm(c, 1, lerp(950, 760, k), lerp(2100, 1250, k), "open", ang=wave)
        if t < 1.0:
            time_sign(c, "17:00")
    else:
        shake(c, T, amt=2)
        c.rect(-40, -40, W + 80, H + 80, (190, 90, 70), "brick", ol=0, shadow=False)
        for y in range(0, H, 70):
            c.stroke([(-40, y), (W + 40, y)], 5, (150, 65, 50))
            for x in range(((y // 70) % 2) * 80, W, 160):
                c.stroke([(x, y), (x, y + 70)], 5, (150, 65, 50))
        x0, y0, x1, y1 = 100, 260, 980, 1460
        c.rect(x0 - 40, y0 - 40, x1 - x0 + 80, y1 - y0 + 80, (225, 225, 230), "gwframe")
        c.rect(x0, y0, x1 - x0, y1 - y0, (140, 190, 225), "gwglass", ol=4, shadow=False)
        glass = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        wink = 1.0 if 5.5 <= t < 6.1 else 0.0
        reflection(c, T, 540, 760, 1.05, glass, alpha=0.75, tint=(210, 235, 255, 45), wink=wink, talk=talk("s8b", T))
        glare(c, x0, y0, x1, y1, "gwglare")
        if 5.5 <= t < 6.3:
            sparkle(c, 640, 700, 44, t, "endwink")
        if t > 8.6:
            c.overlay((255, 255, 255), (t - 8.6) / 0.4 * 255)


FN = dict(intro=s_intro, wake=s_wake, mirror=lambda c, t, T: s_mirror(c, T, t), montage=s_montage, bus=s_bus,
          hall=s_hall, lecture=s_lecture, home=s_home, field=s_field)


def render(i):
    T = i / FPS
    name, a, b = next((s for s in SCENES if s[1] <= T < s[2]), SCENES[-1])
    c = Canvas(W, H, i)
    FN[name](c, T - a, T)
    c.img.convert("RGB").save(os.path.join(FRAMES, f"{i:05d}.png"), compress_level=1)


def main():
    os.makedirs(FRAMES, exist_ok=True)
    idx = [int(x) for x in sys.argv[1:]] or list(range(int(TOTAL * FPS)))
    with Pool() as p:
        for k, _ in enumerate(p.imap_unordered(render, idx, chunksize=3)):
            if k % 100 == 0:
                print(k, "/", len(idx), flush=True)


if __name__ == "__main__":
    main()
