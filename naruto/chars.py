"""Sketchy anime characters, Naruto's POV hands, and the runaway cat."""
import math
from sketch import INK

SKIN = (246, 214, 182)
SKIN_SH = (222, 178, 145)
ORANGE = (222, 132, 58)
ORANGE_D = (180, 100, 45)
BAND = (60, 72, 104)
METAL = (196, 200, 206)
WHITE = (250, 246, 238)

CAST = {
    "naruto":  dict(hair=(242, 202, 92), style="naruto", top=ORANGE, eye=(70, 140, 210), band="forehead", whiskers=True),
    "sasuke":  dict(hair=(44, 48, 72), style="sasuke", top=(52, 70, 120), eye=(40, 36, 44), band="forehead", collar=True),
    "sakura":  dict(hair=(236, 160, 176), style="sakura", top=(196, 72, 78), eye=(80, 160, 110), band="hair"),
    "iruka":   dict(hair=(92, 60, 40), style="iruka", top=(104, 122, 82), eye=(50, 40, 36), band="forehead", scar=True,
                    skin=(226, 180, 140)),
    "kakashi": dict(hair=(214, 214, 218), style="kakashi", top=(104, 122, 82), eye=(50, 46, 50), band="slant", mask=True),
    "teuchi":  dict(hair=(250, 250, 248), style="bandana", top=(246, 244, 238), eye=(50, 40, 36)),
}


def P(cx, cy, s, pts):
    return [(cx + x * s, cy + y * s) for x, y in pts]


def leaf_mark(c, x, y, s, key):
    c.line(c.ell(x, y + 2 * s, 14 * s, 12 * s, a0=-0.5, a1=4.6), key + "sp", lw=3)
    c.line([(x + 6 * s, y - 10 * s), (x + 18 * s, y - 20 * s), (x + 20 * s, y - 2 * s)], key + "tip", lw=3)


def headband(c, cx, cy, s, key, slant=0.0):
    pts = [(-132, -62 + slant * 40), (132, -62 - slant * 40), (128, -22 - slant * 40), (-128, -22 + slant * 40)]
    c.poly(P(cx, cy, s, pts), BAND, key + "band")
    c.poly(P(cx, cy, s, [(-58, -70 + slant * 18), (58, -70 - slant * 18), (56, -16 - slant * 18), (-56, -16 + slant * 18)]),
           METAL, key + "plate")
    leaf_mark(c, cx, cy - 44 * s, s, key)


def anime(c, cx, cy, s, who, expr="smile", talk=0.0, arms=("down", "down"), t=0.0, key=None, look=0.0, body=True):
    """(cx, cy) = centre of the face; s=1 -> head ~260 px wide."""
    cfg = who if isinstance(who, dict) else CAST[who]
    k = key or (who if isinstance(who, str) else "villager")
    skin = cfg.get("skin", SKIN)
    hair, top = cfg["hair"], cfg["top"]
    hair_d = tuple(max(0, v - 40) for v in hair)
    st = cfg["style"]
    Q = lambda pts: P(cx, cy, s, pts)
    # --- hair behind the head
    if st == "sasuke":
        c.poly(Q([(-120, -60), (-150, -150), (-90, -175), (-40, -230), (20, -190), (90, -235), (120, -160), (175, -170),
                  (150, -80), (130, 20)]), hair, k + "hb")
    if st == "sakura":
        c.poly(Q([(-140, -90), (140, -90), (150, 140), (90, 120), (-90, 120), (-150, 140)]), hair, k + "hb")
    if st == "iruka":
        c.poly(Q([(-10, -170), (20, -250), (70, -270), (55, -215), (110, -240), (60, -160)]), hair, k + "pony")
    # --- body
    hands = []
    if body:
        for side, arm in zip((-1, 1), arms):
            sh = (side * 150, 250)
            if arm == "down":
                end = (side * 185, 520)
            elif arm == "wave":
                end = (side * 240 + math.sin(t * 12) * 30, -40)
            elif arm == "point":
                end = (side * 60, 200)
            elif arm == "cross":
                end = (-side * 90, 330)
            elif arm == "book":
                end = (side * 70, 300)
            elif arm == "bowl":
                end = (side * 80, 360)
            elif arm == "up":
                end = (side * 200, -120)
            else:
                end = (side * 185, 520)
            if arm != "cross":
                c.capsule(Q([sh])[0], Q([end])[0], 44 * s, top, k + f"arm{side}")
            hands.append((arm, side, end, sh))
        c.poly(Q([(-180, 620), (-175, 300), (-115, 200), (115, 200), (175, 300), (180, 620)]), top, k + "torso")
        if who in ("iruka", "kakashi"):  # green flak vest
            c.poly(Q([(-150, 620), (-140, 290), (-60, 210), (-30, 620)]), (92, 110, 72), k + "vestL")
            c.poly(Q([(150, 620), (140, 290), (60, 210), (30, 620)]), (92, 110, 72), k + "vestR")
            c.line(Q([(-120, 400), (-60, 400)]), k + "pk1"); c.line(Q([(60, 400), (120, 400)]), k + "pk2")
        if who == "naruto":  # white collar of the jumpsuit
            c.poly(Q([(-80, 200), (80, 200), (60, 260), (-60, 260)]), WHITE, k + "collar")
        if cfg.get("collar"):
            c.poly(Q([(-90, 150), (90, 150), (110, 230), (-110, 230)]), top, k + "hcollar")
        for arm, side, end, sh in hands:
            if arm == "cross":
                c.capsule(Q([(-side * 120, 330 + side * 15)])[0], Q([(side * 120, 330 + side * 15)])[0], 46 * s, top, k + f"cr{side}")
        c.poly(Q([(-42, 120), (42, 120), (46, 205), (-46, 205)]), skin, k + "neck")
        c.hatch(Q([(-42, 160), (42, 160), (46, 205), (-46, 205)]), k + "nh", spacing=10)
    # --- head
    for e, x in (("l", -118), ("r", 118)):
        c.ellipse(cx + x * s, cy + 5 * s, 22 * s, 34 * s, skin, k + "ear" + e)
    head = Q([(-125, -40), (-120, -110), (-80, -150), (0, -165), (80, -150), (120, -110), (125, -40), (118, 40),
              (80, 105), (25, 148), (0, 152), (-25, 148), (-80, 105), (-118, 40)])
    c.poly(head, skin, k + "head")
    if cfg.get("whiskers"):
        for sgn in (-1, 1):
            for i in range(3):
                c.line(Q([(sgn * 62, 32 + i * 18), (sgn * 102, 26 + i * 22)]), k + f"wh{sgn}{i}", lw=3)
    if cfg.get("scar"):
        c.line(Q([(-70, 18), (-20, 12), (20, 12), (70, 18)]), k + "scar", lw=4, color=(170, 110, 90))
    # --- eyes
    ec = cfg["eye"]
    for sgn in (-1, 1):
        ex, ey = sgn * 50 + look * 10, -5
        if cfg.get("band") == "slant" and sgn == -1:
            continue
        if expr in ("happy", "grin_closed"):
            c.line(Q([(ex - 24, ey + 6), (ex, ey - 12), (ex + 24, ey + 6)]), k + f"eh{sgn}", lw=5)
            continue
        half = expr in ("cool", "bored")
        cold = expr in ("cold",)
        top_y = ey - (6 if half else 22 if not cold else 12)
        c.poly(Q([(ex - 28, top_y + 4), (ex + 28, top_y), (ex + 26, ey + 18), (ex - 26, ey + 20)]), WHITE, k + f"ew{sgn}",
               line=False, misreg=0)
        c.circle(cx + (ex + look * 6) * s, cy + (ey + 4) * s, 15 * s, ec, k + f"ei{sgn}", line=False, misreg=0)
        c.circle(cx + (ex + look * 6) * s, cy + (ey + 4) * s, 6 * s, (30, 26, 30), k + f"ep{sgn}", line=False, misreg=0)
        c.circle(cx + (ex + look * 6 - 5) * s, cy + (ey - 2) * s, 4 * s, (255, 255, 255), k + f"eg{sgn}", line=False, misreg=0)
        c.line(Q([(ex - 32, top_y + 6), (ex, top_y - 2), (ex + 32, top_y + 2)]), k + f"lash{sgn}", lw=6)
        if half:
            c.poly(Q([(ex - 30, top_y - 16), (ex + 30, top_y - 18), (ex + 28, top_y + 3), (ex - 30, top_y + 6)]), skin,
                   k + f"lid{sgn}", line=False, misreg=0)
            c.line(Q([(ex - 30, top_y + 4), (ex + 30, top_y + 2)]), k + f"lidl{sgn}", lw=5)
        # brows
        tilt = 10 if cold else (-4 if expr == "grin" else 0)
        c.line(Q([(ex - 30 * sgn, ey - 44 - tilt * 0), (ex + 28 * sgn, ey - 40 + tilt)]) if sgn > 0 else
               Q([(ex + 30, ey - 40 + tilt), (ex - 28, ey - 44)]), k + f"br{sgn}", lw=6, color=hair_d)
    c.line(Q([(2, 10), (8, 42), (-4, 46)]), k + "nose", lw=3, color=SKIN_SH)
    # --- mouth / mask
    my = 88
    if cfg.get("mask"):
        c.poly(Q([(-122, 10), (122, 10), (118, 40), (80, 105), (0, 155), (-80, 105), (-118, 40)]), (52, 60, 88), k + "mask")
        c.line(Q([(0, 60), (4, 120)]), k + "maskl", lw=3, alpha=120)
    elif talk > 0.18 or expr in ("grin", "shout"):
        o = 18 + 30 * max(talk, 0.7 if expr == "grin" else 0)
        c.poly(c.ell(cx, cy + (my - 8) * s, 48 * s, o * s, a0=0, a1=math.pi), (150, 60, 60), k + "mo")
        if expr == "grin":
            c.poly(Q([(-44, my - 8), (44, my - 8), (40, my + 6), (-40, my + 6)]), WHITE, k + "teeth", line=False, misreg=0)
    elif expr in ("cold", "cool", "bored", "flat"):
        c.line(Q([(-24, my), (24, my - 2)]), k + "mf", lw=5)
    elif expr == "frown":
        c.line(c.ell(cx, cy + (my + 14) * s, 26 * s, 12 * s, a0=math.pi + 0.3, a1=2 * math.pi - 0.3), k + "mfr", lw=5)
    else:
        c.line(c.ell(cx, cy + (my - 14) * s, 30 * s, 16 * s, a0=0.3, a1=math.pi - 0.3), k + "ms", lw=5)
    # --- hair in front
    if st == "naruto":
        spikes = [(-135, 10), (-175, -60), (-130, -90), (-190, -160), (-110, -170), (-130, -250), (-50, -200), (-20, -290),
                  (30, -205), (110, -270), (100, -180), (190, -190), (130, -100), (185, -60), (132, 10), (110, -60),
                  (70, -40), (60, -95), (20, -55), (-10, -100), (-40, -50), (-80, -95), (-90, -40)]
        c.poly(Q(spikes), hair, k + "hair")
        c.hatch(Q([(-130, -90), (-190, -160), (-110, -170), (-90, -120)]), k + "hh", spacing=12, alpha=60)
    elif st == "sasuke":
        c.poly(Q([(-130, 60), (-140, -90), (-90, -160), (10, -175), (110, -150), (140, -80), (130, 60), (100, -40),
                  (60, -70), (20, -30), (-20, -75), (-70, -45), (-100, -80)]), hair, k + "hair")
    elif st == "sakura":
        c.poly(Q([(-140, 60), (-140, -100), (-70, -160), (40, -168), (130, -120), (140, 60), (110, -40), (60, -80),
                  (10, -60), (-30, -90), (-90, -50), (-110, -60)]), hair, k + "hair")
    elif st == "iruka":
        c.poly(Q([(-128, -40), (-110, -140), (0, -170), (110, -140), (128, -40), (60, -90), (0, -80), (-60, -95)]), hair, k + "hair")
    elif st == "kakashi":
        c.poly(Q([(-128, -20), (-160, -130), (-110, -150), (-140, -260), (-40, -190), (-30, -300), (40, -200),
                  (90, -290), (100, -170), (190, -230), (140, -110), (128, -20), (60, -80), (-40, -70)]), hair, k + "hair")
    elif st == "bandana":
        c.poly(Q([(-130, -40), (-125, -140), (0, -175), (125, -140), (130, -40), (0, -60)]), hair, k + "hair")
    elif st == "short":
        c.poly(Q([(-128, -30), (-118, -130), (-40, -170), (60, -168), (122, -125), (128, -30), (60, -90), (-40, -95)]), hair, k + "hair")
    elif st == "bun":
        c.circle(cx, cy - 180 * s, 50 * s, hair, k + "bun")
        c.poly(Q([(-128, -20), (-118, -130), (0, -170), (118, -130), (128, -20), (40, -110), (-40, -110)]), hair, k + "hair")
    elif st == "bald":
        c.poly(Q([(-126, 0), (-120, -60), (-100, -30)]), hair, k + "hl")
        c.poly(Q([(126, 0), (120, -60), (100, -30)]), hair, k + "hr")
    band = cfg.get("band")
    if band == "forehead":
        headband(c, cx, cy, s, k)
    elif band == "slant":
        headband(c, cx, cy + 25 * s, s, k, slant=0.35)
        c.poly(Q([(-122, -50), (-10, -80), (-6, 40), (-122, 30)]), BAND, k + "eyecover")
    elif band == "hair":
        c.poly(Q([(-120, -120), (120, -120), (115, -95), (-115, -95)]), BAND, k + "hband")
    # --- hands
    for arm, side, end, sh in hands:
        if arm in ("down", "cross"):
            continue
        hx, hy = Q([end])[0]
        c.circle(hx, hy, 34 * s, skin, k + f"hd{side}")
        if arm == "point":
            c.capsule((hx, hy), (hx - side * 10 * s, hy - 70 * s), 11 * s, skin, k + f"fi{side}")
        if arm == "book":
            c.poly([(hx - 70 * s, hy - 110 * s), (hx + 70 * s, hy - 110 * s), (hx + 70 * s, hy - 10 * s), (hx - 70 * s, hy - 10 * s)],
                   (220, 140, 70), k + "book")


# ------------------------------------------------------------------ POV hands
def pov_arm(c, side, wx, wy, pose="fist", ang=None, s=1.0, key="arm", item=None):
    bx, by = c.w * (0.5 + side * 0.36), c.h + 140
    if ang is None:
        ang = math.atan2(wy - by, wx - bx) + math.pi / 2
    c.capsule((bx, by), (wx, wy), 84 * s, ORANGE, key + "sl", world=False)
    c.hatch(c.capsule_pts((bx + side * 40, by), (wx + side * 30, wy + 40), 40 * s), key + "slh", spacing=14, world=False)
    dx, dy = wx - bx, wy - by
    d = math.hypot(dx, dy) or 1
    cx, cy = wx - dx / d * 55 * s, wy - dy / d * 55 * s
    c.capsule((cx - dx / d * 25 * s, cy - dy / d * 25 * s), (cx, cy), 86 * s, ORANGE_D, key + "cuff", world=False)
    hand(c, wx, wy, pose, side, ang, s * 1.1, key, item)


def rot(pts, ang, ox, oy, s):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(ox + (x * ca - y * sa) * s, oy + (x * sa + y * ca) * s) for x, y in pts]


def hand(c, x, y, pose, side, ang, s, key="h", item=None):
    R = lambda p: rot(p, ang, x, y, s)
    kw = dict(world=False)
    if item == "kunai":
        c.poly(R([(-10, -100), (10, -100), (14, -170), (0, -260), (-14, -170)]), (110, 112, 120), key + "kb", **kw)
        c.poly(R([(-8, -100), (8, -100), (8, 0), (-8, 0)]), (60, 60, 66), key + "kh", **kw)
        c.line(R([(0, 0), (0, 10)]), key + "kr", world=False)
        c.poly(c.ell(*R([(0, 22)])[0], 16 * s, 16 * s), (60, 60, 66), key + "kring", line=True, world=False)
    if item == "chopsticks":
        c.line(R([(-20, -100), (40, -330)]), key + "cs1", lw=9, color=(170, 120, 70), world=False, passes=1)
        c.line(R([(10, -100), (75, -320)]), key + "cs2", lw=9, color=(170, 120, 70), world=False, passes=1)
    if pose == "open":
        for i, (fx, L) in enumerate(((-45, 85), (-15, 100), (15, 96), (45, 80))):
            c.capsule(R([(fx, -110)])[0], R([(fx, -110 - L)])[0], 17 * s, SKIN, key + f"f{i}", **kw)
        c.capsule(R([(-side * 50, -40)])[0], R([(-side * 115, -120)])[0], 19 * s, SKIN, key + "th", **kw)
        c.poly(c.ell(*R([(0, -75)])[0], 70 * s, 78 * s, rot=ang), SKIN, key + "palm", **kw)
        return
    if pose == "point":   # index finger on the thumb side, never in the middle
        c.capsule(R([(-side * 46, -120)])[0], R([(-side * 58, -270)])[0], 19 * s, SKIN, key + "idx", **kw)
    c.poly(R([(-68, -150), (68, -150), (70, -10), (40, 5), (-40, 5), (-70, -10)]), SKIN, key + "fist", **kw)
    for i in range(3):
        fx = -34 + i * 34
        c.line(R([(fx, -150), (fx, -115)]), key + f"kn{i}", lw=3, color=(190, 140, 110), world=False)
    c.capsule(R([(-side * 62, -70)])[0], R([(-side * 5, -108)])[0], 20 * s, SKIN, key + "thf", **kw)


# ------------------------------------------------------------------ cat
def cat(c, x, y, s, phase=0.0, angry=False, key="cat", face=False):
    fur, fur_d = (176, 120, 72), (140, 90, 52)
    if face:   # close-up: big hissing face
        for sgn in (-1, 1):
            c.poly(P(x, y, s, [(sgn * 60, -120), (sgn * 170, -230), (sgn * 175, -60)]), fur, key + f"ear{sgn}")
        c.ellipse(x, y, 210 * s, 170 * s, fur, key + "head")
        for sgn in (-1, 1):
            c.poly(P(x, y, s, [(sgn * 40, -20), (sgn * 110, -50), (sgn * 120, -5), (sgn * 50, 10)]), (230, 210, 90), key + f"e{sgn}")
            c.line(P(x, y, s, [(sgn * 80, -45), (sgn * 82, 5)]), key + f"pu{sgn}", lw=7)
            for i in range(3):
                c.line(P(x, y, s, [(sgn * 60, 60 + i * 14), (sgn * 220, 30 + i * 30)]), key + f"wh{sgn}{i}", lw=3)
        c.poly(c.ell(x, y + 70 * s, 70 * s, 55 * s, a0=0, a1=math.pi), (150, 60, 70), key + "mouth")
        for sgn in (-1, 1):
            c.poly(P(x, y, s, [(sgn * 40, 70), (sgn * 22, 70), (sgn * 32, 100)]), WHITE, key + f"fang{sgn}")
        c.poly(P(x, y, s, [(150, -150), (190, -170), (185, -130)]), (210, 60, 60), key + "bow")
        return
    hop = abs(math.sin(phase)) * 40 * s
    y -= hop
    c.line(P(x, y, s, [(-110, -10), (-170, -70 + math.sin(phase * 2) * 20), (-190, -120)]), key + "tail", lw=int(14 * s), color=fur_d)
    for i, lx in enumerate((-60, -20, 50, 80)):
        sw = math.sin(phase + i * 1.5) * 25
        c.capsule(P(x, y, s, [(lx, 20)])[0], P(x, y, s, [(lx + sw, 70)])[0], 13 * s, fur_d, key + f"leg{i}")
    c.ellipse(x, y, 115 * s, 55 * s, fur, key + "body")
    c.ellipse(x + 110 * s, y - 50 * s, 55 * s, 48 * s, fur, key + "headc")
    for sgn in (-1, 1):
        c.poly(P(x, y, s, [(110 + sgn * 22, -85), (110 + sgn * 46, -125), (110 + sgn * 50, -75)]), fur, key + f"ear{sgn}")
    c.poly(P(x, y, s, [(140, -100), (165, -115), (160, -88)]), (210, 60, 60), key + "bow")
    c.line(P(x, y, s, [(122, -55), (134, -52)]), key + "eye", lw=5)
