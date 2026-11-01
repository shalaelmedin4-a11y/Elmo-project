"""Original cartoon characters and set pieces (paper cut-out style)."""
import math

from paper import INK

SKIN = (247, 202, 160)
SKIN2 = (226, 170, 128)
CAMO = (104, 150, 62)
CAMO_D = (62, 98, 40)
CAMO_L = (168, 180, 88)
HELM = (74, 124, 52)
HELM_D = (52, 92, 38)
BOOT = (34, 30, 34)
WHITE = (250, 246, 236)
GREY_FOOD = (160, 158, 156)
KHAKI = (205, 170, 98)
OLIVE = (98, 104, 56)
WOOD = (176, 116, 64)
WOOD_D = (128, 80, 44)
PINE = (36, 112, 72)
PINE_D = (24, 84, 56)
FLAG_GREEN = (60, 170, 80)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(t, a=0.0, b=1.0):
    return max(a, min(b, t))


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(t):
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- characters

def face(c, cx, cy, eyes="dot", mouth="smile", look=0):
    ex = 18
    ey = cy
    if eyes == "dot":
        for sx in (-1, 1):
            c.ell(cx + sx * ex + look, ey, 5.5, 6.5, INK, ol=None, n=12)
    elif eyes == "wide":
        for sx in (-1, 1):
            c.ell(cx + sx * ex + look, ey, 10, 11, WHITE, w=3, n=16)
            c.ell(cx + sx * ex + look * 1.5, ey, 4, 4.5, INK, ol=None, n=10)
    elif eyes == "x":
        for sx in (-1, 1):
            x = cx + sx * ex
            c.line([(x - 7, ey - 7), (x + 7, ey + 7)], 4)
            c.line([(x - 7, ey + 7), (x + 7, ey - 7)], 4)
    elif eyes == "happy":
        for sx in (-1, 1):
            c.arc(cx + sx * ex, ey + 4, 8, 8, 200, 340, 4)
    elif eyes == "tired":
        for sx in (-1, 1):
            c.line([(cx + sx * ex - 9, ey), (cx + sx * ex + 9, ey)], 4)
            c.arc(cx + sx * ex, ey - 1, 9, 6, 20, 160, 3)
    elif eyes == "closed":
        for sx in (-1, 1):
            c.arc(cx + sx * ex, ey - 3, 8, 6, 20, 160, 4)
    my = cy + 24
    if mouth == "smile":
        c.arc(cx, my - 8, 13, 10, 20, 160, 4)
    elif mouth == "grin":
        c.ell(cx, my, 15, 9, (150, 40, 50), w=3, a0=0, a1=180, n=12)
    elif mouth == "o":
        c.ell(cx, my, 7, 8, (120, 30, 40), w=3, n=12)
    elif mouth == "open":
        c.ell(cx, my + 2, 13, 13, (120, 30, 40), w=3, n=16)
    elif mouth == "flat":
        c.line([(cx - 10, my), (cx + 10, my)], 4)
    elif mouth == "wavy":
        c.line([(cx - 14, my), (cx - 7, my - 4), (cx, my), (cx + 7, my - 4), (cx + 14, my)], 4)
    elif mouth == "tongue":
        c.ell(cx, my, 13, 10, (120, 30, 40), w=3, n=14)
        c.ell(cx + 4, my + 10, 7, 9, (235, 110, 120), w=3, n=12)


def helmet(c, x, y, big=False, branches=False, sway=0):
    s = 1.2 if big else 1.0
    c.push(x, y, s, 0)
    if branches:
        for i, (bx, ang) in enumerate(((-40, -35), (-8, -8), (26, 20), (52, 45))):
            c.push(bx, -36, 1, ang + sway)
            c.line([(0, 0), (0, -62)], 6, (96, 66, 36))
            for k in range(3):
                c.ell((-1) ** k * 12, -22 - k * 16, 13, 7, (82, 168, 70), w=3, n=10)
            c.pop()
    c.ell(0, 0, 66, 54, HELM, a0=180, a1=360, n=24)
    c.ell(-22, -28, 12, 7, HELM_D, ol=None, n=10)
    c.ell(20, -16, 10, 6, HELM_D, ol=None, n=10)
    c.rrect(-78, -6, 78, 10, 7, HELM_D)
    c.pop()


def soldier(c, x, y, s=1.0, rot=0, flip=False, hero=False, legs=(0, 0), arms=(18, 18), eyes="dot",
            mouth="smile", look=0, branches=False, sway=0, held=None, hand_r=None):
    """Short round soldier. Origin = between the feet. arms = outward raise in degrees."""
    c.push(x, y, s, rot, flip)
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        c.push(side * 20, -64, 1, ang)
        c.rect(-13, -4, 13, 46, CAMO_D)
        c.ell(side * 6, 52, 23, 12, BOOT, n=16)
        c.pop()
    c.ell(0, -116, 60, 58, CAMO)
    c.ell(-26, -138, 15, 9, CAMO_D, ol=None, n=10)
    c.ell(24, -100, 13, 8, CAMO_L, ol=None, n=10)
    c.ell(18, -150, 10, 6, CAMO_D, ol=None, n=10)
    c.ell(-20, -92, 11, 7, CAMO_L, ol=None, n=10)
    c.rect(-50, -80, 50, -70, (70, 60, 40), w=3)
    for side, a in ((-1, arms[0]), (1, arms[1])):
        c.push(side * 50, -146, 1, -side * a)
        c.rrect(-11, -4, 11, 60, 10, CAMO)
        c.ell(0, 66, 14, 14, SKIN, n=14)
        if side == 1 and held:
            held(c)
        if side == 1 and hand_r == "thumb":
            c.rrect(-5, 50, 7, 82, 5, SKIN, w=3)
        c.pop()
    c.ell(0, -222, 54, 62, SKIN)
    c.ell(-52, -218, 8, 12, SKIN2, n=10)
    c.ell(52, -218, 8, 12, SKIN2, n=10)
    face(c, 0, -215, eyes, mouth, look)
    helmet(c, 0, -242, big=hero, branches=branches, sway=sway)
    c.pop()


def sleeper(c, x, y, s=1.0, hero=False, blanket=(150, 70, 70), eyes="closed", mouth="flat", awake=False):
    """Soldier lying in a bed seen from the front: head on pillow, blanket over body."""
    c.push(x, y, s, 0)
    c.rrect(-120, -40, -30, 10, 18, WHITE, w=4)          # pillow
    c.push(-78, -40, 0.82, -78 if not awake else -12)
    c.ell(0, 0, 54, 62, SKIN)
    face(c, 0, 6, eyes, mouth)
    if hero:
        helmet(c, 0, -20, big=True)
    else:
        c.ell(0, -30, 50, 34, (120, 82, 50), a0=180, a1=360, n=16, w=4)
    c.pop()
    c.rrect(-60, -34, 150, 18, 14, blanket)
    c.line([(-40, -20), (130, -20)], 3, (110, 50, 50))
    c.pop()


def instructor(c, x, y, s=1.0, flip=False, arm=20, arm_l=15, mouth="shout", whistle=False, legs=(0, 0)):
    """Tall angry drill instructor with a big moustache and a campaign hat."""
    c.push(x, y, s, 0, flip)
    for side, ang in ((-1, legs[0]), (1, legs[1])):
        c.push(side * 22, -150, 1, ang)
        c.rect(-15, 0, 15, 140, OLIVE)
        c.ell(side * 8, 146, 28, 13, BOOT, n=16)
        c.pop()
    c.rrect(-58, -330, 58, -140, 30, KHAKI)
    c.line([(0, -320), (0, -150)], 3, (160, 128, 70))
    c.rect(-58, -170, 58, -150, (90, 66, 40), w=3)
    for side, a in ((-1, arm_l), (1, arm)):
        c.push(side * 56, -315, 1, -side * a)
        c.rrect(-13, -4, 13, 130, 12, KHAKI)
        c.ell(0, 136, 16, 16, SKIN, n=14)
        if whistle and side == 1:
            pass
        c.pop()
    c.ell(0, -400, 46, 58, SKIN)
    c.line([(-34, -432), (-8, -418)], 8)
    c.line([(34, -432), (8, -418)], 8)
    for sx in (-1, 1):
        c.ell(sx * 18, -410, 5, 5, INK, ol=None, n=10)
    c.ell(0, -390, 12, 14, SKIN2, n=12)
    if mouth == "shout":
        c.ell(0, -352, 20, 15, (120, 30, 40), w=4, n=16)
    elif mouth == "whistle":
        c.ell(0, -355, 7, 7, (120, 30, 40), w=3, n=10)
    else:
        c.line([(-12, -352), (12, -352)], 5)
    # moustache
    c.poly([(0, -376), (-26, -380), (-52, -364), (-40, -360), (-20, -366), (0, -366),
            (20, -366), (40, -360), (52, -364), (26, -380)], (40, 32, 30), w=3)
    if whistle:
        c.ell(10, -352, 14, 9, (200, 205, 215), w=4, n=14)
        c.rect(22, -357, 40, -348, (200, 205, 215), w=3)
    # campaign hat
    c.ell(0, -448, 88, 14, (150, 108, 60))
    c.poly([(-42, -448), (-30, -490), (-10, -500), (0, -486), (10, -500), (30, -490), (42, -448)], (170, 124, 70))
    c.rect(-42, -462, 42, -450, (90, 60, 34), w=3)
    c.pop()


def bubble(c, x, y, txt, size=46, shout=True, tail=(-40, 70)):
    n = 18
    pts = []
    tw = len(txt) * size * 0.36 + 50
    th = size * 0.9 + 30
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1.18 if (shout and k % 2) else 1.0
        pts.append((x + math.cos(a) * tw * r, y + math.sin(a) * th * r))
    c.poly([(x - 20, y + th * .7), (x + tail[0], y + tail[1] + th * .4), (x + 20, y + th * .7)], WHITE, w=4)
    c.poly(pts, WHITE, w=5)
    c.text(x, y + 2, txt, size, fill=(200, 30, 40) if shout else INK)


def zzz(c, x, y, t, s=1.0):
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        c.text(x + 30 * ph * s + k * 6, y - 120 * ph * s, "Z", (26 + 14 * ph) * s,
               fill=(240, 240, 255), stroke=3, stroke_fill=INK)


def stars_ring(c, x, y, t, r=60):
    for k in range(4):
        a = t * 5 + k * math.pi / 2
        px, py = x + math.cos(a) * r, y + math.sin(a) * r * .35
        star(c, px, py, 16, (255, 220, 60))


def star(c, x, y, r, col, pts_n=5, w=4):
    pts = []
    for k in range(pts_n * 2):
        a = math.pi * k / pts_n - math.pi / 2
        rr = r if k % 2 == 0 else r * .45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, col, w=w)


def burst(c, x, y, r, col=(255, 210, 60), n=10):
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n
        rr = r if k % 2 == 0 else r * .55
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * .8))
    c.poly(pts, col, w=6)


def puff(c, x, y, r, col=(235, 230, 220)):
    for dx, dy, rr in ((0, 0, 1), (-r * .7, r * .2, .7), (r * .7, r * .25, .75)):
        c.ell(x + dx, y + dy, r * rr, r * rr * .8, col, w=4, n=14)


def sweat(c, x, y):
    c.poly([(x, y - 18), (x + 9, y), (x, y + 8), (x - 9, y)], (140, 210, 250), w=3)


# ---------------------------------------------------------------- set pieces

def sky(c, cols, top=-1000, bottom=1300):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, top + 5, cols[0], ol=None, jit=False)
    n = len(cols)
    h = (bottom - top) / n
    for i, col in enumerate(cols):
        y0 = top + i * h
        pts = [(-400, y0 - 2)] + [(x, y0 + h + 10 * math.sin(x / 90 + i * 1.7)) for x in range(-400, 1560, 60)] + [(1500, y0 - 2)]
        c.poly(pts, col, ol=None, jit=False)
    c.layer = "mid"


def hills(c, y, amp, col, phase=0, ol=INK, bottom=3000):
    pts = [(-300, bottom)] + [(x, y - amp * (0.6 + 0.4 * math.sin(x / 210 + phase)) * abs(math.sin(x / 330 + phase)))
                               for x in range(-300, 1400, 40)] + [(1400, bottom)]
    c.poly(pts, col, ol=ol, w=5)


def pine(c, x, y, s=1.0, col=PINE):
    c.push(x, y, s)
    c.rect(-10, -30, 10, 0, WOOD_D, w=4)
    for k, (wd, yy) in enumerate(((60, -30), (48, -75), (34, -115))):
        c.poly([(-wd, yy), (0, yy - 70), (wd, yy)], col if k % 2 == 0 else PINE_D, w=4)
    c.pop()


def tent(c, x, y, s=1.0):
    c.push(x, y, s)
    c.poly([(-110, 0), (0, -130), (110, 0)], (86, 132, 62), w=5)
    c.poly([(-30, 0), (0, -70), (30, 0)], (48, 76, 36), w=4)
    c.line([(0, -130), (0, -155)], 4)
    c.pop()


def barracks_hut(c, x, y, s=1.0):
    c.push(x, y, s)
    c.rect(-150, -150, 150, 0, WOOD)
    for k in range(1, 5):
        c.line([(-150, -k * 30), (150, -k * 30)], 3, WOOD_D)
    c.poly([(-175, -150), (0, -235), (175, -150)], (150, 60, 50), w=5)
    c.rect(-25, -90, 25, 0, WOOD_D, w=4)
    for sx in (-1, 1):
        c.rect(sx * 95 - 28, -115, sx * 95 + 28, -65, (250, 220, 120), w=4)
        c.line([(sx * 95, -115), (sx * 95, -65)], 3)
    c.pop()


def flagpole(c, x, y, t, h=520):
    c.rect(x - 7, y - h, x + 7, y, (190, 190, 200), w=4)
    c.ell(x, y - h - 8, 12, 12, (230, 200, 60), w=4, n=12)
    pts_top, pts_bot = [], []
    for k in range(9):
        px = x + 7 + k * 22
        wv = 10 * math.sin(t * 5 - k * .8) * (k / 8)
        pts_top.append((px, y - h + wv))
        pts_bot.append((px, y - h + 120 + wv))
    c.poly(pts_top + pts_bot[::-1], FLAG_GREEN, w=5)


def cloud(c, x, y, s=1.0):
    c.push(x, y, s)
    for dx, dy, r in ((-60, 10, 45), (0, -15, 60), (60, 8, 48), (20, 20, 50)):
        c.ell(dx, dy, r, r * .8, (255, 255, 252), w=5, n=18)
    c.pop()


def bunk(c, x, floor, w=440, top=True, s=1.25):
    """Metal bunk bed; returns (bottom_mattress_y, top_mattress_y)."""
    col = (110, 120, 140)
    bot_y, top_y = floor - 190 * s, floor - 470 * s
    for sx in (-1, 1):
        c.rect(x + sx * w / 2 - 12, (top_y - 80) if top else bot_y - 80, x + sx * w / 2 + 12, floor, col, w=4)
    c.rect(x - w / 2, bot_y, x + w / 2, bot_y + 40, (220, 214, 200), w=4)
    c.rect(x - w / 2, bot_y + 40, x + w / 2, bot_y + 58, col, w=4)
    if top:
        c.rect(x - w / 2, top_y, x + w / 2, top_y + 40, (220, 214, 200), w=4)
        c.rect(x - w / 2, top_y + 40, x + w / 2, top_y + 58, col, w=4)
        for k in range(4):
            c.line([(x + w / 2 + 2, top_y + 60 + k * 60), (x + w / 2 + 2, top_y + 60 + k * 60)], 2, col)
    return bot_y, top_y


def room(c, wall, floor_col, floor_y=1560):
    c.layer = "bg"
    c.rect(-400, -1000, 1500, floor_y, wall, ol=None, jit=False)
    for k in range(-1, 12):
        c.line([(k * 110, -1000), (k * 110, floor_y)], 3, tuple(max(0, v - 14) for v in wall), jit=False)
    c.layer = "mid"
    c.rect(-400, floor_y, 1500, 3000, floor_col, w=5)
    for k in range(-2, 12):
        c.line([(k * 120 + 40, floor_y), (k * 160 - 120, 3000)], 3, tuple(max(0, v - 25) for v in floor_col))
