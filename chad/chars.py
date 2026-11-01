"""Characters: Chad (only ever seen in reflections), the other people, and
Chad's own POV hands."""
import math
from paper import INK

SKIN = (247, 200, 158)
SKIN_SH = (222, 160, 118)
HOODIE = (150, 205, 245)
HOODIE_D = (105, 170, 225)
HAIR = (246, 200, 70)
HAIR_D = (210, 150, 40)
HAIR_L = (255, 232, 140)
WHITE = (252, 250, 245)


def rot(pts, ang, ox, oy, s=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(ox + (x * ca - y * sa) * s, oy + (x * sa + y * ca) * s) for x, y in pts]


# --------------------------------------------------------------------- Chad
def chad(c, cx, cy, s=1.0, wink=0.0, talk=0.0, key="chad"):
    """Head and shoulders. (cx, cy) is the centre of the face, s=1 -> face ~360 px wide."""
    P = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    # hoodie
    c.shape(P([(-360, 640), (-330, 360), (-200, 270), (200, 270), (330, 360), (360, 640)]), HOODIE, key + "hood")
    c.ellipse(cx, cy + 275 * s, 190 * s, 62 * s, HOODIE_D, key + "hoodin")
    c.shape(P([(-80, 120), (80, 120), (85, 290), (-85, 290)]), SKIN_SH, key + "neck")
    for k, x in (("l", -60), ("r", 60)):
        c.stroke(P([(x, 300), (x - 6 * (x > 0) + 3, 430)]), 10 * s, WHITE)
        c.circle(cx + (x - 2) * s, cy + 440 * s, 11 * s, WHITE, key + "tip" + k, ol=4)
    # ears
    for k, x in (("l", -178), ("r", 178)):
        c.ellipse(cx + x * s, cy + 5 * s, 32 * s, 52 * s, SKIN, key + "ear" + k)
    # head with a huge square jaw and high cheekbones
    c.shape(P([(-160, -210), (160, -210), (175, -100), (182, 10), (172, 120), (150, 175), (78, 228),
               (-78, 228), (-150, 175), (-172, 120), (-182, 10), (-175, -100)]), SKIN, key + "head", amt=1.2)
    for sgn in (-1, 1):
        c.stroke(P([(sgn * 160, 30), (sgn * 118, 80), (sgn * 92, 110)]), 9 * s, SKIN_SH)       # cheekbone
        c.stroke(P([(sgn * 150, 150), (sgn * 100, 190)]), 7 * s, SKIN_SH)                      # jaw angle
    c.stroke(P([(-40, 205), (0, 214), (40, 205)]), 6 * s, SKIN_SH)                             # chin
    # hunter eyes: narrow, straight upper lid, low brows
    for sgn, k in ((-1, "l"), (1, "r")):
        ex = sgn * 75
        closed = wink > 0.5 and sgn == 1
        if closed:
            c.stroke(P([(ex - 42, -30), (ex, -20), (ex + 42, -30)]), 8 * s)
        else:
            eye = [(ex - 45, -34), (ex + 45, -38), (ex + 38, -24), (ex, -16), (ex - 38, -24)]
            c.shape(P(eye), WHITE, key + "eye" + k, amt=0.5, ol=4, shadow=False)
            c.ellipse(cx + (ex + 2) * s, cy - 28 * s, 13 * s, 11 * s, (70, 140, 210), key + "iris" + k, ol=0, shadow=False)
            c.circle(cx + (ex + 2) * s, cy - 28 * s, 5.5 * s, INK, key + "pup" + k, ol=0, shadow=False)
            c.stroke(P([(ex - 48, -34), (ex + 48, -40)]), 8 * s)
        by = -66 + (10 if closed else 0)
        c.stroke(P([(ex - 58 * (sgn < 0) - 40 * (sgn > 0), by - 6 * (sgn < 0)),
                    (ex + 40 * (sgn < 0) + 58 * (sgn > 0), by + 4 * (sgn < 0) - 10 * (sgn > 0) + 4)]), 17 * s, HAIR_D)
    # nose
    c.stroke(P([(4, -18), (16, 52), (-6, 62)]), 6 * s, SKIN_SH)
    # mouth: confident smirk / talking
    if talk > 0.15:
        c.ellipse(cx + 4 * s, cy + 128 * s, 34 * s, (8 + 22 * talk) * s, (120, 40, 50), key + "mopen", ol=5, shadow=False)
    else:
        c.stroke(P([(-46, 126), (0, 130), (40, 122), (56, 108)]), 7 * s)
    # golden swoop hair
    c.shape(P([(-188, -40), (-205, -180), (-150, -290), (-30, -340), (110, -330), (200, -270), (238, -190),
               (205, -140), (150, -170), (90, -150), (10, -158), (-70, -150), (-140, -120), (-165, -70)]),
            HAIR, key + "hair", amt=1.5)
    c.shape(P([(-120, -270), (0, -318), (130, -300), (60, -280), (-40, -250)]), HAIR_L, key + "hairhl", amt=1, ol=0, shadow=False)
    for pts in ([(-160, -120), (-110, -230), (-10, -290)], [(-60, -160), (20, -250), (140, -280)],
                [(70, -160), (150, -230), (215, -200)]):
        c.stroke(P(pts), 7 * s, HAIR_D)


# --------------------------------------------------------------------- people
def person(c, cx, cy, s, skin, hair, top, style="short", expr="smile", glasses=False, talk=0.0,
           arms=("down", "down"), key="p", t=0.0, beard=False, shirt2=None, body=True):
    """Generic cartoon person, head+torso. (cx, cy) = head centre, s=1 -> head ~240 px wide."""
    P = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    hair_d = tuple(max(0, v - 45) for v in hair)
    if style == "long":
        c.shape(P([(-140, -80), (140, -80), (165, 260), (-165, 260)]), hair, key + "hairback")
    if style == "bun":
        c.circle(cx, cy - 170 * s, 62 * s, hair, key + "bun")
    if style == "ponytail":
        c.shape(P([(110, -90), (210, 40), (180, 230), (120, 60)]), hair, key + "pony")
    # arms behind the body first
    hands = []
    if body:
        for side, arm in zip((-1, 1), arms):
            sx, sy = side * 165, 260
            if arm == "down":
                end = (side * 205, 520)
            elif arm in ("wave", "highfive"):
                sw = math.sin(t * 14) * 25 if arm == "wave" else 0
                end = (side * 250 + sw, -60)
            elif arm == "thumb":
                end = (side * 150, 160)
            elif arm == "clap":
                end = (side * (40 + 40 * abs(math.sin(t * 16))), 250)
            elif arm == "mouth":
                end = (side * 70, 110)
            elif arm == "sign":
                end = (side * 150, 60)
            elif arm == "hold":
                end = (side * 70, 330)
            else:
                end = (side * 205, 520)
            c.capsule(P([(sx, sy)])[0], P([end])[0], 48 * s, top, key + "arm" + str(side))
            hands.append((arm, side, end))
        c.shape(P([(-190, 600), (-185, 300), (-120, 200), (120, 200), (185, 300), (190, 600)]), top, key + "torso")
        if shirt2:
            c.shape(P([(-60, 200), (60, 200), (0, 290)]), shirt2, key + "collar", ol=5)
        c.shape(P([(-45, 110), (45, 110), (50, 210), (-50, 210)]), skin, key + "neck")
    for k, x in (("l", -122), ("r", 122)):
        c.ellipse(cx + x * s, cy + 10 * s, 24 * s, 38 * s, skin, key + "ear" + k)
    c.ellipse(cx, cy, 125 * s, 140 * s, skin, key + "head")
    # hair on top
    if style in ("short", "bun", "ponytail", "long"):
        c.shape(P([(-130, -10), (-120, -110), (-50, -160), (60, -160), (125, -105), (132, -10), (100, -75),
                   (20, -95), (-60, -85), (-105, -60)]), hair, key + "hair")
    elif style == "curly":
        for i in range(8):
            a = math.pi + i * math.pi / 7
            c.circle(cx + math.cos(a) * 115 * s, cy - 25 * s + math.sin(a) * 120 * s, 48 * s, hair, key + f"cur{i}")
    elif style == "buzz":
        c.shape(P([(-125, -30), (-110, -115), (0, -148), (110, -115), (125, -30), (0, -90)]), hair, key + "hair")
    elif style == "bald":
        c.shape(P([(-128, 10), (-122, -40), (-100, -20)]), hair, key + "hairl", ol=4)
        c.shape(P([(128, 10), (122, -40), (100, -20)]), hair, key + "hairr", ol=4)
    if beard:
        c.shape(P([(-60, 75), (60, 75), (40, 100), (-40, 100)]), hair_d, key + "stache", ol=4)
    # face
    big = expr in ("surprised",)
    for sgn in (-1, 1):
        ex = sgn * 48
        if expr == "happy_closed" or expr == "cheer":
            c.stroke(P([(ex - 18, -5), (ex, -18), (ex + 18, -5)]), 7 * s)
        elif big:
            c.circle(cx + ex * s, cy - 10 * s, 24 * s, WHITE, key + f"ew{sgn}", ol=4, shadow=False)
            c.circle(cx + ex * s, cy - 10 * s, 9 * s, INK, key + f"ep{sgn}", ol=0, shadow=False)
        else:
            c.ellipse(cx + ex * s, cy - 10 * s, 11 * s, 14 * s, INK, key + f"e{sgn}", ol=0, shadow=False)
        by = -60 if big else -45
        c.stroke(P([(ex - 22, by + 4 * sgn * 0), (ex + 22, by - 3)] if sgn > 0 else [(ex - 22, by - 3), (ex + 22, by)]), 7 * s, hair_d)
        if glasses:
            c.stroke(P([(ex - 34, -32), (ex + 34, -32), (ex + 34, 12), (ex - 34, 12), (ex - 34, -32)]), 6 * s)
    if glasses:
        c.stroke(P([(-14, -22), (14, -22)]), 6 * s)
    c.circle(cx - 78 * s, cy + 35 * s, 18 * s, (245, 150, 150), key + "chk1", ol=0, shadow=False, alpha=150)
    c.circle(cx + 78 * s, cy + 35 * s, 18 * s, (245, 150, 150), key + "chk2", ol=0, shadow=False, alpha=150)
    c.stroke(P([(0, 5), (8, 38), (-4, 42)]), 5 * s, tuple(max(0, v - 50) for v in skin))
    my = 78
    if expr == "surprised":
        c.ellipse(cx, cy + (my + 4) * s, 20 * s, 26 * s, (110, 30, 40), key + "mo", ol=5, shadow=False)
    elif talk > 0.15 or expr == "cheer":
        o = 12 + 26 * (talk if expr != "cheer" else 0.9)
        c.poly(c.ell(cx, cy + my * s, 42 * s, o * s, key + "mt", a0=0, a1=math.pi), (130, 35, 45), ol=5, shadow=False)
    elif expr == "whisper":
        c.ellipse(cx + 10 * s, cy + my * s, 12 * s, 8 * s, (130, 35, 45), key + "mw", ol=4, shadow=False)
    else:
        c.poly(c.ell(cx, cy + (my - 12) * s, 40 * s, 22 * s, key + "ms", a0=0.2, a1=math.pi - 0.2), (130, 35, 45), ol=4, shadow=False)
    # hands in front
    for arm, side, end in hands:
        hx, hy = P([end])[0]
        if arm == "down":
            continue
        if arm == "thumb":
            c.capsule((hx - side * 26 * s, hy - 20 * s), (hx - side * 40 * s, hy - 80 * s), 15 * s, skin)
            c.circle(hx, hy, 36 * s, skin, key + f"h{side}")
            for yy in (-12, 6, 22):
                c.stroke([(hx, hy + yy * s), (hx + side * 30 * s, hy + yy * s)], 4 * s, SKIN_SH)
        else:
            open_hand(c, hx, hy, 0.55 * s, skin, side, key + f"h{side}")


def open_hand(c, x, y, s, skin, side=1, key="oh", ang=0.0):
    pts = lambda p: rot(p, ang, x, y, s)
    for i, (fx, L) in enumerate(((-45, 85), (-15, 98), (15, 95), (45, 80))):
        c.capsule(pts([(fx, -60)])[0], pts([(fx, -60 - L)])[0], 15 * s, skin)
    c.capsule(pts([(-side * 40, 0)])[0], pts([(-side * 110, -70)])[0], 16 * s, skin)
    c.poly(c.ell(*pts([(0, -40)])[0], 66 * s, 72 * s, key, rot=ang), skin)


# --------------------------------------------------------------------- POV hands
def pov_arm(c, side, wx, wy, pose="fist", ang=None, s=1.0, key="arm"):
    """One of Chad's own arms coming in from the bottom edge, hand at (wx, wy)."""
    bx = c.w * (0.5 + side * 0.34)
    by = c.h + 120
    if ang is None:
        ang = math.atan2(wy - by, wx - bx) + math.pi / 2     # fingers point away from the elbow
    c.capsule((bx, by), (wx, wy), 82 * s, HOODIE, world=False, shadow=True)
    # cuff
    dx, dy = wx - bx, wy - by
    d = math.hypot(dx, dy) or 1
    cx, cy = wx - dx / d * 60 * s, wy - dy / d * 60 * s
    c.capsule((cx - dx / d * 30 * s, cy - dy / d * 30 * s), (cx, cy), 86 * s, HOODIE_D, world=False, shadow=False)
    hand(c, wx, wy, pose, side, ang, s * 1.15, key)


def hand(c, x, y, pose, side, ang, s, key="h"):
    P = lambda p: rot(p, ang, x, y, s)
    kw = dict(world=False)
    if pose == "open":
        for i, (fx, L) in enumerate(((-45, 85), (-15, 100), (15, 96), (45, 80))):
            c.capsule(P([(fx, -110)])[0], P([(fx, -110 - L)])[0], 17 * s, SKIN, **kw)
        c.capsule(P([(-side * 50, -40)])[0], P([(-side * 115, -120)])[0], 19 * s, SKIN, **kw)
        c.poly(c.ell(*P([(0, -75)])[0], 70 * s, 78 * s, key + "palm", rot=ang), SKIN, **kw)
        return
    # fist based poses
    if pose == "thumb":
        c.capsule(P([(-side * 52, -120)])[0], P([(-side * 75, -240)])[0], 24 * s, SKIN, **kw)
        c.poly(P(c.rrect_pts(-70, -150, 140, 150, 40, key + "tfist")), SKIN, **kw)
        for yy in (-112, -78, -44):
            c.stroke(P([(side * 5, yy), (side * 66, yy)]), 5 * s, SKIN_SH, world=False)
        return
    if pose == "point":
        c.capsule(P([(-20, -120)])[0], P([(-20, -250)])[0], 18 * s, SKIN, **kw)
    c.poly(P(c.rrect_pts(-68, -150, 136, 150, 46, key + "fist")), SKIN, **kw)
    for i in range(3):
        fx = -34 + i * 34
        c.stroke(P([(fx, -150), (fx, -118)]), 5 * s, SKIN_SH, world=False)
    if pose in ("fist", "hold"):
        c.capsule(P([(-side * 60, -70)])[0], P([(-side * 5, -105)])[0], 20 * s, SKIN, **kw)
