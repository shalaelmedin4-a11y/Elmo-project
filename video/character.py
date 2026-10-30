"""The hero: short round boy, big oval head, dot eyes, green beanie,
orange puffy jacket. Drawn as a cut-out sprite so scenes can move/rotate it."""
import math
from paper import sprite_canvas

SKIN = (255, 212, 168)
CHEEK = (246, 150, 150)
JACKET = (255, 128, 20)
JACKET_D = (214, 92, 8)
BEANIE = (40, 170, 70)
BEANIE_D = (24, 128, 50)
PANTS = (44, 62, 120)
BOOT = (90, 52, 30)
INK = (25, 20, 25)
WHITE = (250, 250, 245)
SW, SH = 600, 900


def _arm(c, shoulder, a1, a2, key, sleeve=JACKET, tint=None):
    L = 100
    x0, y0 = shoulder
    x1 = x0 + math.sin(math.radians(a1)) * L
    y1 = y0 + math.cos(math.radians(a1)) * L
    x2 = x1 + math.sin(math.radians(a2)) * L
    y2 = y1 + math.cos(math.radians(a2)) * L
    c.thick_line((x0, y0), (x1, y1), 62, sleeve, key + "u")
    c.circle(x1, y1, 31, sleeve, key + "e", shadow=False)
    c.thick_line((x1, y1), (x2, y2), 56, sleeve, key + "l")
    c.circle(x2, y2, 30, tint or SKIN, key + "h")
    return x2, y2


def boy(frame, arm_l=(20, 10), arm_r=(-20, -10), eyes="dot", mouth="small", face=None,
        cream=0.0, mask=False, frozen=0.0, legs=True, wind=0.0, brows=False, look=(0, 0),
        mouth_open=0.0, arms_front=True, arms=True):
    """Arm angles in degrees, 0 = hanging down, positive = swing toward +x."""
    c = sprite_canvas(SW, SH, frame)
    c.shadow = (8, 10)

    def mix(col, amt=frozen, to=(150, 200, 255)):
        return tuple(int(a + (b - a) * amt) for a, b in zip(col, to))

    skin = mix(SKIN)
    jacket = mix(JACKET, frozen * 0.12)
    jacket_d = mix(JACKET_D, frozen * 0.12)

    # jacket flaps blowing in the wind (behind the body)
    if wind:
        for i, dy in enumerate((520, 600)):
            w = wind * (60 + 25 * math.sin(frame * 1.7 + i))
            c.tri([(160, dy - 40), (160 - w * 2.2, dy - 10 + 18 * math.sin(frame + i)), (170, dy + 50)], jacket_d, f"flap{i}")

    if legs:
        c.rect(225, 650, 62, 160, PANTS, "legL")
        c.rect(313, 650, 62, 160, PANTS, "legR")
        c.ellipse(250, 815, 58, 30, BOOT, "bootL")
        c.ellipse(350, 815, 58, 30, BOOT, "bootR")

    if arms and not arms_front:
        _arm(c, (175, 490), *arm_l, "armL", jacket)
        _arm(c, (425, 490), *arm_r, "armR", jacket)

    # puffy jacket body with quilting
    c.ellipse(300, 565, 158, 150, jacket, "body", amt=0.025)
    for i, yy in enumerate((500, 565, 630)):
        half = math.sqrt(max(0, 150 ** 2 - (yy - 565) ** 2)) * 158 / 150 - 12
        c.thick_line((300 - half, yy), (300 + half, yy), 7, jacket_d, f"quilt{i}", shadow=False)
    c.thick_line((300, 430), (300, 712), 8, jacket_d, "zip", shadow=False)
    c.ellipse(300, 425, 95, 34, jacket_d, "collar")

    if arms and arms_front:
        hl = _arm(c, (172, 495), *arm_l, "armL", jacket, skin)
        hr = _arm(c, (428, 495), *arm_r, "armR", jacket, skin)

    # head
    hx, hy = 300, 275
    c.ellipse(hx, hy, 175, 140, skin, "head", amt=0.018)
    ex, ey = look
    if mask:
        c.ellipse(hx, hy + 12, 150, 112, (90, 200, 110), "mask", amt=0.03)
        c.ellipse(hx, hy + 12, 150, 112, (60, 175, 90), "mask2", amt=0.03, shadow=False, alpha=60)
    if cream > 0:
        n = int(cream * 26)
        for i in range(n):
            a = i * 2.39996
            rr = 10 + (i * 37 % 75)
            px = hx + math.cos(a) * rr * 1.25
            py = hy + 15 + math.sin(a) * rr * 0.8
            size = 34 + (i * 13 % 20) + cream * 8
            c.circle(px, py, size, WHITE, f"cream{i}")
        if cream > 0.95:
            c.ellipse(hx, hy + 12, 160, 118, WHITE, "creamfull", amt=0.05)

    # eyes
    lx, rx_, eyy = hx - 58 + ex, hx + 58 + ex, hy + 5 + ey
    if eyes == "dot":
        c.circle(lx, eyy, 11, INK, "eyeL", shadow=False)
        c.circle(rx_, eyy, 11, INK, "eyeR", shadow=False)
    elif eyes == "wide":
        for k, x in (("L", lx), ("R", rx_)):
            c.circle(x, eyy, 30, WHITE, "ew" + k)
            c.circle(x, eyy - 4, 9, INK, "ep" + k, shadow=False)
    elif eyes == "x":
        for k, x in (("L", lx), ("R", rx_)):
            c.thick_line((x - 14, eyy - 14), (x + 14, eyy + 14), 8, INK, "x1" + k, shadow=False)
            c.thick_line((x - 14, eyy + 14), (x + 14, eyy - 14), 8, INK, "x2" + k, shadow=False)
    elif eyes == "closed":
        for k, x in (("L", lx), ("R", rx_)):
            c.thick_line((x - 15, eyy), (x + 15, eyy), 7, INK, "cl" + k, shadow=False)
    elif eyes == "squint":
        for k, x in (("L", lx), ("R", rx_)):
            c.thick_line((x - 16, eyy + 4), (x + 16, eyy - 2), 8, INK, "sq" + k, shadow=False)
    if brows:
        c.thick_line((lx - 22, eyy - 34), (lx + 18, eyy - 24), 8, INK, "brL", shadow=False)
        c.thick_line((rx_ - 18, eyy - 24), (rx_ + 22, eyy - 34), 8, INK, "brR", shadow=False)

    if not mask and cream < 0.95:
        c.circle(hx - 105, hy + 45, 20, mix(CHEEK), "chkL", shadow=False, alpha=170)
        c.circle(hx + 105, hy + 45, 20, mix(CHEEK), "chkR", shadow=False, alpha=170)
    my = hy + 62
    if mouth == "small" and cream < 0.95:
        c.ellipse(hx, my, 13, 6, INK, "mouth", shadow=False)
    elif mouth == "flat":
        c.thick_line((hx - 18, my), (hx + 18, my), 6, INK, "mflat", shadow=False)
    elif mouth == "smile":
        c.poly(c.ellipse_pts(hx, my - 6, 26, 18, "msm", a0=0.15, a1=math.pi - 0.15), INK, shadow=False)
    elif mouth == "smirk":
        c.thick_line((hx - 16, my + 2), (hx + 20, my - 8), 6, INK, "msk", shadow=False)
    elif mouth == "open":
        o = 10 + 50 * mouth_open
        c.ellipse(hx, my + o * 0.3, 18 + 18 * mouth_open, o, (120, 20, 30), "mopen", shadow=False)
        c.ellipse(hx, my + o * 0.8, 12 + 10 * mouth_open, o * 0.35, (230, 90, 100), "tongue", shadow=False)
    elif mouth == "chew":
        c.ellipse(hx, my, 22, 12 + 6 * mouth_open, INK, "mchew", shadow=False)

    # beanie
    c.poly(c.ellipse_pts(hx, hy - 55, 172, 135, "bdome", a0=math.pi, a1=2 * math.pi), BEANIE)
    for i in range(-3, 4):
        c.thick_line((hx + i * 42, hy - 70), (hx + i * 36, hy - 165 + abs(i) ** 2 * 6), 6, BEANIE_D, f"rib{i}", shadow=False)
    c.rect(hx - 180, hy - 85, 360, 52, BEANIE_D, "band", amt=4)
    c.circle(hx + 8 + wind * 30 * math.sin(frame), hy - 200, 36, BEANIE, "pom", amt=0.12)
    if frozen > 0.5:
        for i, x in enumerate((-120, -60, 10, 80, 140)):
            c.tri([(hx + x - 12, hy - 34), (hx + x + 12, hy - 34), (hx + x + 2, hy - 34 + 30 + (i % 2) * 18)], (200, 235, 255), f"ice{i}")
    return c.img
