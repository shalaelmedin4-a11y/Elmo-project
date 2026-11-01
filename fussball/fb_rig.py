"""Anime-style character rig for 'Ein Tag als Profifußballer' (original, no club logos).

Clean outlines, two-tone cel shading (light from the upper left), realistic body
proportions (~7.5 heads). Front view and side (profile, facing right) view.
Local units: feet at y=0, top of the hair at about y=-810.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cartoon"))

import numpy as np  # noqa: E402

import cast  # noqa: E402  (lip-sync level lives in cast.SPEAK)

LINE = (66, 48, 46)
LINE_PX = 3.0                      # outline thickness on screen (px)
SKIN, SKIN_S = (234, 198, 170), (208, 162, 138)
HAIR, HAIR_S, HAIR_H = (150, 117, 70), (110, 82, 48), (198, 166, 110)
EYE_G = (76, 138, 96)
KIT_Y, KIT_Y_S = (222, 186, 76), (188, 150, 54)
KIT_B, KIT_B_S = (40, 40, 46), (26, 26, 30)
WHITE = (246, 244, 238)


def shade(col, k=0.82):
    return tuple(int(v * k) for v in col)


OUTFITS = {
    "kit": dict(shirt=KIT_Y, shirt_s=KIT_Y_S, trim=KIT_B, shorts=KIT_B, socks=KIT_Y, boots=(30, 30, 34), number=True),
    "train": dict(shirt=(46, 48, 56), shirt_s=(32, 34, 40), trim=KIT_Y, shorts=(46, 48, 56), socks=(46, 48, 56),
                  boots=(30, 30, 34)),
    "home": dict(shirt=(170, 176, 182), shirt_s=(140, 146, 152), trim=(150, 156, 162), shorts=(70, 76, 92),
                 socks=WHITE, boots=WHITE, long_pants=True),
    "sleep": dict(shirt=(236, 234, 228), shirt_s=(206, 204, 198), trim=(220, 218, 212), shorts=(90, 96, 120),
                  socks=SKIN, boots=SKIN),
    "hoodie": dict(shirt=(48, 50, 58), shirt_s=(34, 36, 42), trim=(70, 72, 80), shorts=(60, 64, 76), socks=WHITE,
                   boots=WHITE, long_pants=True, hood=True),
    "bare": dict(shirt=SKIN, shirt_s=SKIN_S, trim=SKIN_S, shorts=(40, 60, 90), socks=SKIN, boots=SKIN, bare=True),
}


class Rig:
    """Draws one character. c = paper.Ctx (boil should be 0 for the clean look)."""

    def __init__(self, c, hair=HAIR, hair_s=HAIR_S, hair_h=HAIR_H, skin=SKIN, skin_s=SKIN_S, eye=EYE_G,
                 hero=True, number="3", outfit="kit", style=0):
        self.c, self.hair, self.hair_s, self.hair_h = c, hair, hair_s, hair_h
        self.skin, self.skin_s, self.eye, self.hero = skin, skin_s, eye, hero
        self.number, self.style = number, style
        self.o = dict(OUTFITS[outfit])

    # ------------------------------------------------------------ helpers
    def begin(self, x, y, s, rot=0, flip=False):
        c = self.c
        c.push(x, y, s, rot, flip)
        c.wmul = LINE_PX * 2 / max(1e-6, c.scale())     # constant on-screen line width (SS=2)

    def end(self):
        self.c.pop()
        self.c.wmul = 1.0

    def poly(self, pts, col, ol=True):
        self.c.poly(pts, col, ol=LINE if ol else None, w=1)

    def ell(self, cx, cy, rx, ry, col, ol=True, n=26, a0=0, a1=360):
        self.c.ell(cx, cy, rx, ry, col, ol=LINE if ol else None, w=1, n=n, a0=a0, a1=a1)

    def line(self, pts, w, col=LINE):
        self.c.line(pts, w, col)

    def limb(self, p1, p2, w1, w2, col, col_s, ol=True):
        """Tapered limb with a cel-shaded right side."""
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        pts = [(x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x2 + nx * w2 / 2, y2 + ny * w2 / 2),
               (x2 - nx * w2 / 2, y2 - ny * w2 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2)]
        self.poly(pts, col, ol)
        sgn = 1 if nx > 0 else -1                       # shade the side facing right (away from the light)
        sh = [(x1 + sgn * nx * w1 * .12, y1 + sgn * ny * w1 * .12), (x2 + sgn * nx * w2 * .12, y2 + sgn * ny * w2 * .12),
              (x2 + sgn * nx * w2 / 2, y2 + sgn * ny * w2 / 2), (x1 + sgn * nx * w1 / 2, y1 + sgn * ny * w1 / 2)]
        self.poly(sh, col_s, ol=False)
        self.ell(x1, y1, w1 / 2 - .5, w1 / 2 - .5, col, ol=False, n=14)

    @staticmethod
    def ik(sx, sy, tx, ty, l1, l2, side):
        dx, dy = tx - sx, ty - sy
        d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 0.5))
        th = math.atan2(dy, dx)
        al = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
        best = None
        for sg in (1, -1):
            ex, ey = sx + l1 * math.cos(th + sg * al), sy + l1 * math.sin(th + sg * al)
            score = side * ex + 0.25 * ey
            if best is None or score > best[0]:
                best = (score, ex, ey)
        return (best[1], best[2]), (sx + d * math.cos(th), sy + d * math.sin(th))

    # ------------------------------------------------------------ FRONT VIEW
    def front(self, x, y, s, t=0.0, hands=((-120, -420), (120, -420)), held=(None, None), legs=(0, 0),
              eyes="open", mouth="smile", look=(0, 0), brows="calm", head_rot=0, lean=0, headphones=False,
              show_legs=True, blink=True, sweat=False, flip=False):
        c, o = self.c, self.o
        self.begin(x, y, s, lean, flip)
        if show_legs:
            for i, side in enumerate((-1, 1)):
                hip = (side * 42, -400)
                ang = math.radians(legs[i] * side)
                knee = (hip[0] + math.sin(ang) * 185 + side * 6, hip[1] + math.cos(ang) * 185)
                ank = (knee[0] + side * 4, knee[1] + 180)
                lc, lcs = (o["shorts"], shade(o["shorts"])) if o.get("long_pants") else (self.skin, self.skin_s)
                self.limb(hip, knee, 66, 48, lc, lcs)
                self.limb(knee, ank, 46, 32, o["socks"] if not o.get("long_pants") else lc,
                          shade(o["socks"]) if not o.get("long_pants") else lcs)
                if not o.get("long_pants"):
                    self.limb((knee[0], knee[1] + 50), ank, 44, 32, o["socks"], shade(o["socks"]))
                    self.line([(knee[0] - 21, knee[1] + 70), (knee[0] + 21, knee[1] + 70)], 5, o["trim"])
                self.ell(ank[0] + side * 12, ank[1] + 14, 36, 17, o["boots"], n=18)
        # torso
        sh = o["shirt"]
        if not o.get("bare"):
            self.poly([(-68, -440), (68, -440), (84, -300), (8, -296), (0, -330), (-8, -296), (-84, -300)], o["shorts"])
            self.poly([(14, -440), (68, -440), (84, -300), (40, -298)], shade(o["shorts"]), ol=False)
        torso = [(-94, -652), (94, -652), (100, -600), (76, -470), (78, -420), (-78, -420), (-76, -470), (-100, -600)]
        self.poly(torso, sh)
        self.poly([(30, -650), (94, -652), (100, -600), (76, -470), (78, -422), (40, -422), (50, -560)], o["shirt_s"], ol=False)
        if o.get("bare"):
            self.line([(-40, -560), (-6, -548)], 3, self.skin_s)
            self.line([(40, -560), (6, -548)], 3, self.skin_s)
            self.line([(0, -540), (0, -440)], 3, self.skin_s)
        else:
            self.poly([(-26, -652), (26, -652), (14, -626), (-14, -626)], o["trim"])            # collar
            for sx in (-1, 1):
                self.line([(sx * 96, -630), (sx * 78, -440)], 6, o["trim"])                       # side stripes
            if o.get("number"):
                c.text(0, -560, self.number, 70, fill=KIT_B)
            if o.get("hood"):
                self.poly([(-50, -660), (50, -660), (36, -630), (-36, -630)], shade(sh, .7))
                self.line([(-14, -630), (-16, -560)], 3, WHITE)
                self.line([(14, -630), (16, -560)], 3, WHITE)
        # neck + head
        self.limb((0, -700), (0, -652), 40, 44, self.skin, self.skin_s)
        self.poly([(-20, -700), (20, -700), (16, -684), (-16, -686)], self.skin_s, ol=False)   # chin shadow
        c.push(0, -748, 1, head_rot)
        self.head_front(t, eyes, mouth, look, brows, blink, headphones, sweat)
        c.pop()
        # arms in front
        for i, side in enumerate((-1, 1)):
            sx, sy = side * 92, -630
            (ex, ey), (hx, hy) = self.ik(sx, sy, hands[i][0], hands[i][1], 150, 140, side)
            arm_col = self.skin if o.get("bare") else sh
            self.limb((sx, sy), (ex, ey), 46, 38, arm_col, shade(arm_col))
            if not o.get("bare") and not o.get("hood"):          # short sleeves: skin forearm
                mx, my = sx + (ex - sx) * .45, sy + (ey - sy) * .45
                self.limb((mx, my), (ex, ey), 36, 34, self.skin, self.skin_s)
                self.limb((sx, sy), (mx, my), 50, 46, arm_col, shade(arm_col))
                self.limb((ex, ey), (hx, hy), 34, 28, self.skin, self.skin_s)
            else:
                self.limb((ex, ey), (hx, hy), 36, 30, arm_col, shade(arm_col))
            self.ell(hx, hy + 6, 18, 22, self.skin, n=16)
            if held[i]:
                held[i](self, hx, hy)
        self.end()

    def head_front(self, t, eyes, mouth, look, brows, blink, headphones, sweat):
        """Head centred at (0,0) in head space: chin at y=+56, top of hair at y=-62."""
        sk, sks = self.skin, self.skin_s
        if self.hero:
            mouth = hero_mouth(mouth)
        do_blink = blink and eyes == "open" and (int(t * 12) % 47) in (45, 46)
        # back hair / ears
        self.poly(self.hair_back(), self.hair_s)
        for sx in (-1, 1):
            self.ell(sx * 40, 6, 7, 12, sk, n=14)
        face = [(-40, -18), (-40, 10), (-34, 32), (-20, 48), (0, 56), (20, 48), (34, 32), (40, 10), (40, -18)]
        face = [(-40, -30)] + face + [(40, -30)]
        self.poly(face, sk)
        self.poly([(14, 40), (34, 30), (40, 8), (40, -24), (30, -10), (26, 20)], sks, ol=False)      # cheek shade
        self.poly([(-38, -26), (38, -26), (36, -14), (20, -8), (4, -14), (-12, -8), (-30, -12)], sks, ol=False)  # fringe shadow
        # eyes
        for sx in (-1, 1):
            ex, ey = sx * 16, 4
            if eyes in ("closed",) or do_blink:
                self.line([(ex - 10, ey + 2), (ex, ey + 4), (ex + 10, ey + 2)], 3)
            elif eyes == "happy":
                self.line([(ex - 10, ey + 3), (ex, ey - 4), (ex + 10, ey + 3)], 3)
            else:
                h = {"half": 5, "wide": 11, "open": 9}.get(eyes, 9)
                self.poly([(ex - 11, ey), (ex - 4, ey - h * .8), (ex + 8, ey - h * .7), (ex + 12, ey), (ex + 4, ey + h * .55),
                           (ex - 6, ey + h * .5)], WHITE, ol=False)
                ix, iy = ex + look[0] * 3, ey + look[1] * 2 - 1
                self.ell(ix, iy, 6, min(8, h * .9), self.eye, ol=False, n=18)
                self.ell(ix, iy - 3, 6, 3, shade(self.eye, .6), ol=False, n=12, a0=180, a1=360)
                self.ell(ix, iy + .5, 2.8, 3.6, (30, 36, 34), ol=False, n=10)
                self.ell(ix - 2, iy - 3, 1.6, 1.6, WHITE, ol=False, n=8)
                self.ell(ix + 2.2, iy + 2.5, .9, .9, WHITE, ol=False, n=6)
                self.line([(ex - 12, ey + 1), (ex - 5, ey - h * .85), (ex + 8, ey - h * .75), (ex + 13, ey - 1)], 3.2)
                if eyes == "half":
                    self.poly([(ex - 12, ey - 9), (ex + 13, ey - 9), (ex + 13, ey - 2), (ex - 12, ey - 1)], sk, ol=False)
                    self.line([(ex - 12, ey - 1), (ex + 13, ey - 2)], 3)
            by = -13 if brows != "up" else -17
            tilt = {"focused": 3, "sad": -3}.get(brows, 0)     # inner end lower when focused
            inner, outer = (ex - sx * 11, by + tilt), (ex + sx * 12, by - 2)
            self.poly([inner, outer, (outer[0], outer[1] + 3), (inner[0], inner[1] + 4.5)], self.hair_s)
        # nose
        self.line([(3, 14), (5, 24), (1, 27)], 2.4, shade(sks, .85))
        # mouth
        my = 38
        if mouth == "smile":
            self.line([(-9, my - 1), (0, my + 2), (9, my - 1)], 2.6)
        elif mouth == "grin":
            self.poly([(-12, my - 3), (12, my - 3), (7, my + 6), (-7, my + 6)], WHITE)
        elif mouth == "o":
            self.ell(0, my + 1, 4, 5, (120, 56, 56), n=12)
        elif mouth == "open":
            self.ell(0, my + 2, 7, 6, (120, 56, 56), n=14)
        elif mouth == "shout":
            self.poly([(-12, my - 4), (12, my - 4), (8, my + 12), (-8, my + 12)], (120, 56, 56))
            self.poly([(-10, my - 3), (10, my - 3), (9, my), (-9, my)], WHITE, ol=False)
        elif mouth == "yawn":
            self.ell(0, my + 3, 7, 10, (120, 56, 56), n=14)
        elif mouth == "chew":
            self.line([(-7, my + (1 if int(t * 6) % 2 else -1)), (7, my)], 2.6)
        else:
            self.line([(-7, my), (7, my)], 2.6)
        if sweat:
            self.c.poly([(30, -24), (35, -14), (30, -10), (25, -14)], (170, 215, 240), ol=LINE, w=1)
        # hair on top
        for pts, col in self.hair_front():
            self.poly(pts, col)
        if headphones:
            self.c.arc(0, -10, 50, 60, 180, 360, 9, (40, 40, 46))
            for sx in (-1, 1):
                self.c.rrect(sx * 44 - 10, -6, sx * 44 + 10, 26, 8, (54, 54, 60), ol=LINE, w=1)

    def hair_back(self):
        return [(-44, 6), (-48, -30), (-34, -58), (0, -66), (34, -58), (48, -30), (44, 6), (38, -16), (-38, -16)]

    def hair_front(self):
        h, hs, hh = self.hair, self.hair_s, self.hair_h
        if self.style == 1:   # teammate: short buzz cut
            return [([(-42, -14), (-40, -44), (-20, -60), (20, -60), (40, -44), (42, -14), (30, -30), (-30, -30)], h)]
        out = []
        cap = [(-44, -4), (-47, -30), (-36, -54), (-10, -66), (18, -64), (40, -50), (46, -24), (44, -4), (36, -24),
               (-36, -24)]
        out.append((cap, h))
        # fringe: separate locks swept to the right, different lengths
        for x0, ln, sw in ((-40, 24, 10), (-26, 30, 12), (-10, 26, 12), (6, 30, 12), (22, 22, 10), (34, 16, 8)):
            out.append(([(x0 - 2, -40), (x0 + 16, -40), (x0 + sw + 6, -30 + ln * .3), (x0 + sw, -26 + ln * .55),
                         (x0 + 4, -32)], h))
        # spiky texture on top
        for pts in ([(-34, -50), (-30, -74), (-14, -60)], [(-14, -62), (-4, -80), (8, -64)], [(6, -64), (24, -76), (26, -56)],
                    [(26, -58), (44, -62), (40, -44)]):
            out.append((pts, h))
        out.append(([(36, -52), (46, -26), (44, -6), (38, -22), (36, -40)], hs))
        out.append(([(-26, -54), (-8, -60), (14, -56), (10, -50), (-8, -53), (-22, -48)], hh))
        out.append(([(-4, -36), (8, -38), (14, -30), (6, -32)], hh))
        return out

    # ------------------------------------------------------------ SIDE VIEW (facing right)
    def side(self, x, y, s, t=0.0, thighs=(0, 0), knees=(0, 0), arms=(0, 0), elbows=(70, 70), lean=0,
             eyes="open", mouth="flat", brows="focused", head_rot=0, flip=False, ball_foot=None):
        """thighs/knees/arms/elbows: (near, far) angles in degrees. thigh 0 = straight down, + = forward."""
        o, c = self.o, self.c
        self.begin(x, y, s, 0, flip)
        hip = (0, -400)
        c.push(hip[0], hip[1], 1, lean)
        torso_top = (8, -255)

        def leg(th, kn, near):
            a = math.radians(th)
            knee = (math.sin(a) * 185, math.cos(a) * 185)
            b = math.radians(th - kn)
            ank = (knee[0] + math.sin(b) * 180, knee[1] + math.cos(b) * 180)
            k = 1.0 if near else 0.8
            sk_c = shade(self.skin, k)
            self.limb((0, 0), knee, 64, 46, sk_c, shade(sk_c))
            self.limb((knee[0] + math.sin(b) * 40, knee[1] + math.cos(b) * 40), ank, 44, 32, shade(o["socks"], k),
                      shade(o["socks"], k * .82))
            foot = (ank[0] + math.cos(b) * 26, ank[1] - math.sin(b) * 26 + 10)
            self.limb(ank, foot, 34, 26, shade(o["boots"], k), shade(o["boots"], k * .8))
            return foot

        def arm_(an, el, near):
            sh = (torso_top[0], torso_top[1] + 14)
            a = math.radians(an)
            elb = (sh[0] + math.sin(a) * 150, sh[1] + math.cos(a) * 150)
            b = math.radians(an + el)
            hand = (elb[0] + math.sin(b) * 135, elb[1] + math.cos(b) * 135)
            k = 1.0 if near else 0.8
            self.limb(sh, elb, 44, 36, shade(o["shirt"], k), shade(o["shirt_s"], k))
            self.limb(elb, hand, 34, 28, shade(self.skin, k), shade(self.skin_s, k))
            self.ell(hand[0], hand[1], 15, 15, shade(self.skin, k), n=12)

        arm_(arms[1], elbows[1], False)
        leg(thighs[1], knees[1], False)
        # shorts + torso
        self.poly([(-46, -30), (44, -30), (60, 60), (-40, 70)], o["shorts"])
        self.poly([(-50, -255), (56, -255), (54, -40), (-46, -30)], o["shirt"])
        self.poly([(-50, -255), (-10, -255), (-14, -34), (-46, -30)], o["shirt_s"], ol=False)
        if o.get("number"):
            c.text(-26, -150, self.number, 54, fill=KIT_B)
        self.line([(-46, -40), (54, -40)], 6, o["trim"])
        foot = leg(thighs[0], knees[0], True)
        if ball_foot is not None:
            ball_foot[0], ball_foot[1] = foot
        # neck + head
        self.limb((10, -255), (16, -300), 36, 34, self.skin, self.skin_s)
        c.push(18, -348, 1, head_rot)
        self.head_side(t, eyes, mouth, brows)
        c.pop()
        arm_(arms[0], elbows[0], True)
        c.pop()
        self.end()

    def head_side(self, t, eyes, mouth, brows):
        sk, sks = self.skin, self.skin_s
        if self.hero:
            mouth = hero_mouth(mouth)
        self.poly([(-40, 10), (-46, -30), (-30, -58), (0, -66), (30, -58), (40, -30)], self.hair_s)
        prof = [(-34, 0), (-36, -26), (-20, -48), (10, -52), (30, -36), (36, -14), (34, 0), (44, 14), (36, 20), (38, 30),
                (36, 36), (34, 46), (14, 54), (-8, 46), (-24, 28)]
        self.poly(prof, sk)
        self.poly([(-34, 0), (-24, 28), (-8, 46), (2, 40), (-14, 22), (-20, -6)], sks, ol=False)
        self.ell(-8, 6, 8, 12, sk, n=14)
        self.ell(-8, 6, 4, 7, sks, ol=False, n=10)
        if eyes in ("closed",):
            self.line([(16, 4), (28, 6)], 3)
        else:
            self.poly([(18, -2), (30, -4), (31, 8), (20, 8)], WHITE, ol=False)
            self.ell(26, 3, 4, 6, self.eye, ol=False, n=12)
            self.ell(27, 3, 2, 3, (30, 36, 34), ol=False, n=8)
            self.line([(16, -3), (32, -5)], 3)
        tilt = 3 if brows == "focused" else 0
        self.poly([(14, -12 + tilt), (34, -16), (34, -12), (14, -8 + tilt)], HAIR_S, ol=False)
        my = 38
        if mouth in ("open", "shout", "o", "yawn"):
            self.poly([(28, my - 6), (37, my - 5), (36, my + 6), (28, my + 4)], (120, 56, 56))
        else:
            self.line([(28, my - 2), (37, my - 3)], 2.6)
        cap = [(-40, 4), (-48, -30), (-34, -58), (-4, -68), (26, -64), (40, -46), (44, -28), (34, -30), (28, -22),
               (20, -30), (10, -26), (-2, -34), (-16, -26), (-24, -10), (-30, 2)]
        self.poly(cap, self.hair)
        for tf in ([(-36, -52), (-48, -72), (-20, -62)], [(-12, -64), (-6, -84), (8, -66)], [(8, -64), (30, -80), (30, -58)]):
            self.poly(tf, self.hair)
        self.poly([(-18, -50), (4, -58), (22, -52), (6, -46)], self.hair_h)


def hero_mouth(default):
    lvl, f = cast.SPEAK
    if lvl > 0.5:
        return "open" if f % 3 else "o"
    if lvl > 0.15:
        return "o" if f % 2 else "open"
    return default


# ---------------------------------------------------------------- poses
def run_pose(t, rate=1.6, amp=1.0):
    p = t * rate * 2 * math.pi
    th = 42 * amp * math.sin(p)
    kn_n = 25 + 60 * amp * max(0.0, -math.sin(p + .6))
    kn_f = 25 + 45 * amp * max(0.0, math.sin(p + .6))
    return dict(thighs=(th, -th), knees=(kn_n, kn_f), arms=(-38 * amp * math.sin(p), 38 * amp * math.sin(p)),
                elbows=(85, 85), lean=8 * amp)


def kick_pose(p):
    """p 0..1: wind-up -> strike (0.55) -> follow-through."""
    if p < 0.5:
        k = p / 0.5
        th, kn = -10 - 35 * k, 20 + 70 * k
    else:
        k = min(1, (p - 0.5) / 0.5)
        th, kn = -45 + 125 * k, 90 - 90 * k
    return dict(thighs=(th, 6), knees=(kn, 20), arms=(-50, 40), elbows=(60, 60), lean=-6 + 10 * p)
