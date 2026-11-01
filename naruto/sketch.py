"""Rough anime-sketch drawing kit: flat muted fills slightly off-register from
loose, doubled pencil/ink lines that re-draw ("boil") every few frames, plus
paper texture, warm soft light and vignette as a final grade."""
import math, os, random, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
INK = (58, 46, 44)
MARKER = os.path.join(HERE, "fonts", "PermanentMarker-Regular.ttf")
_fonts, _tex = {}, {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(MARKER, size)
    return _fonts[size]


def texture(w, h, seed):
    key = (w, h, seed)
    if key not in _tex:
        r = np.random.default_rng(seed)
        def blob(div, amp):
            a = r.normal(0, 1, (h // div + 2, w // div + 2)).astype(np.float32)
            return np.asarray(Image.fromarray(np.clip(128 + a * 40, 0, 255).astype(np.uint8))
                              .resize((w, h), Image.BICUBIC), np.float32) / 128 - 1
        t = 1 + blob(90, 1) * 0.05 + blob(18, 1) * 0.035 + r.normal(0, 1, (h, w)).astype(np.float32) * 0.025
        _tex[key] = t[..., None]
    return _tex[key]


class Canvas:
    def __init__(self, w, h, frame, bg=(240, 230, 210)):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), tuple(bg) + (255,))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.frame = frame
        self.boil = frame // 2          # lines re-drawn 6x per second
        self.ox = self.oy = 0.0
        self.zoom, self.zc = 1.0, (w / 2, h / 2)
        self.lw = 4

    def T(self, pts):
        zx, zy = self.zc
        return [((x - zx) * self.zoom + zx + self.ox, (y - zy) * self.zoom + zy + self.oy) for x, y in pts]

    def rng(self, key):
        return random.Random(zlib.crc32(f"{key}|{self.boil}".encode()))

    # -------------------------------------------------------------- geometry
    def ell(self, cx, cy, rx, ry, n=None, rot=0.0, a0=0.0, a1=2 * math.pi):
        n = n or max(18, int((abs(rx) + abs(ry)) / 6))
        full = abs(a1 - a0 - 2 * math.pi) < 1e-6
        cr, sr = math.cos(rot), math.sin(rot)
        out = []
        for i in range(n if full else n + 1):
            a = a0 + (a1 - a0) * i / n
            x, y = math.cos(a) * rx, math.sin(a) * ry
            out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
        return out

    def rect_pts(self, x, y, w, h):
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

    def capsule_pts(self, p0, p1, r):
        (x0, y0), (x1, y1) = p0, p1
        a = math.atan2(y1 - y0, x1 - x0)
        pts = [(x0 + math.cos(a - math.pi / 2 - math.pi * i / 8) * r, y0 + math.sin(a - math.pi / 2 - math.pi * i / 8) * r) for i in range(9)]
        pts += [(x1 + math.cos(a + math.pi / 2 - math.pi * i / 8) * r, y1 + math.sin(a + math.pi / 2 - math.pi * i / 8) * r) for i in range(9)]
        return pts

    # -------------------------------------------------------------- drawing
    def sketch_line(self, pts, key, closed=False, lw=None, color=INK, alpha=230, passes=2, wob=2.6, world=True):
        if world:
            pts = self.T(pts)
        lw = (lw or self.lw) * (self.zoom if world else 1)
        if closed:
            pts = list(pts) + [pts[0]]
        r = self.rng(key)
        for p in range(passes):
            q = []
            # each pass starts/ends a little off like a quick pencil stroke
            for i, (x, y) in enumerate(pts):
                q.append((x + r.uniform(-wob, wob), y + r.uniform(-wob, wob)))
            if len(q) >= 2 and not closed:
                (x0, y0), (x1, y1) = q[0], q[1]
                ext = r.uniform(2, 9)
                d = math.hypot(x1 - x0, y1 - y0) or 1
                q[0] = (x0 - (x1 - x0) / d * ext, y0 - (y1 - y0) / d * ext)
            w = max(1, int(lw * (1.0 if p == 0 else 0.55)))
            a = alpha if p == 0 else int(alpha * 0.6)
            self.d.line(q, fill=tuple(color) + (a,), width=w, joint="curve")

    def poly(self, pts, color, key="", line=True, lw=None, alpha=255, world=True, misreg=3.0):
        if len(pts) < 3:
            return
        P = self.T(pts) if world else list(pts)
        r = self.rng(key + "f")
        dx, dy = r.uniform(-misreg, misreg), r.uniform(-misreg, misreg)
        self.d.polygon([(x + dx, y + dy) for x, y in P], fill=tuple(color[:3]) + (alpha,))
        if line:
            self.sketch_line(P, key, closed=True, lw=lw, world=False, alpha=int(230 * alpha / 255))

    def rect(self, x, y, w, h, color, key="", **kw):
        self.poly(self.rect_pts(x, y, w, h), color, key, **kw)

    def ellipse(self, cx, cy, rx, ry, color, key="", rot=0.0, **kw):
        self.poly(self.ell(cx, cy, rx, ry, rot=rot), color, key, **kw)

    def circle(self, cx, cy, r, color, key="", **kw):
        self.ellipse(cx, cy, r, r, color, key, **kw)

    def capsule(self, p0, p1, r, color, key="", **kw):
        self.poly(self.capsule_pts(p0, p1, r), color, key, **kw)

    def line(self, pts, key="", lw=None, color=INK, alpha=230, world=True, passes=2):
        self.sketch_line(pts, key, lw=lw, color=color, alpha=alpha, world=world, passes=passes)

    def hatch(self, pts, key, spacing=16, color=INK, alpha=70, world=True, ang=0.8):
        """Loose diagonal hatching inside a polygon (shadows)."""
        P = self.T(pts) if world else pts
        xs = [p[0] for p in P]; ys = [p[1] for p in P]
        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
        if x1 <= x0 or y1 <= y0:
            return
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in P], fill=255)
        lay = Image.new("RGBA", m.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        r = self.rng(key)
        span = (x1 - x0) + (y1 - y0)
        for k in range(-span, span, spacing):
            j = r.uniform(-3, 3)
            d.line([(k + j, 0), (k + j + (y1 - y0) * ang, y1 - y0)], fill=tuple(color) + (alpha,), width=2)
        lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", m.size, 0), m))
        self.img.alpha_composite(lay, (x0, y0))

    def text(self, txt, cx, cy, size, fill=(250, 245, 235), outline=INK, angle=0.0, ow=6):
        f = font(int(size))
        bb = f.getbbox(txt, stroke_width=ow)
        tw, th = bb[2] - bb[0] + 30, bb[3] - bb[1] + 30
        tmp = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((15 - bb[0], 15 - bb[1]), txt, font=f, fill=tuple(fill) + (255,),
                                 stroke_width=ow, stroke_fill=tuple(outline) + (255,))
        if angle:
            tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))

    def overlay(self, color, alpha):
        self.img.alpha_composite(Image.new("RGBA", (self.w, self.h), tuple(color) + (int(max(0, min(255, alpha))),)))

    def glow(self, cx, cy, r, color, alpha):
        lay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(color) + (int(alpha),))
        self.img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r / 3)))

    # -------------------------------------------------------------- final grade
    def finish(self, warm=1.0, light=(0.2, 0.15), desat=0.28, dark=0.0):
        a = np.asarray(self.img.convert("RGB"), np.float32)
        a *= texture(self.w, self.h, 3 + (self.boil % 3))
        g = a.mean(axis=2, keepdims=True)
        a = a * (1 - desat) + g * desat                        # muted colours
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        lx, ly = light[0] * self.w, light[1] * self.h
        dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2) / math.hypot(self.w, self.h)
        warmth = np.clip(1 - dist * 1.3, 0, 1)[..., None]
        a = a * (1 + warmth * 0.10 * warm) + warmth * np.array([22, 12, -6], np.float32) * warm   # soft warm light
        vx, vy = (xx / self.w - 0.5), (yy / self.h - 0.5)
        vig = 1 - (vx ** 2 + vy ** 2) * 0.55
        a *= vig[..., None] * (1 - dark)
        a = a * 0.94 + 10                                       # lift blacks, nothing harsh
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
