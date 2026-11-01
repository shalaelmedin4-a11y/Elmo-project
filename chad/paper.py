"""Paper cut-out drawing kit: flat shapes with thick black outlines, paper
grain, slightly ragged scissor-cut edges that re-cut ("boil") a few times per
second, and a soft drop shadow."""
import math, random, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

INK = (22, 20, 26)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
_grain = {}
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


def grain(w, h):
    if (w, h) not in _grain:
        r = np.random.default_rng(5)
        fine = r.normal(0, 1, (h, w)).astype(np.float32)
        blot = np.asarray(Image.fromarray(np.clip(128 + r.normal(0, 40, (h // 16 + 1, w // 16 + 1)), 0, 255)
                                          .astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) - 128
        fib = np.asarray(Image.fromarray(np.clip(128 + r.normal(0, 40, (h // 2 + 1, w // 24 + 1)), 0, 255)
                                         .astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) - 128
        g = 1 + fine * 0.035 + blot / 128 * 0.05 + fib / 128 * 0.03
        _grain[(w, h)] = g[..., None]
    return _grain[(w, h)]


class Canvas:
    def __init__(self, w, h, frame, bg=(255, 255, 255), transparent=False):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0) if transparent else bg + (255,))
        self.frame = frame
        self.boil = frame // 3          # edges re-cut 4x per second
        self.ox = self.oy = 0.0         # camera offset
        self.zoom, self.zc = 1.0, (w / 2, h / 2)
        self.ol = 7                     # outline width
        self.shadow, self.shadow_alpha = (8, 10), 60

    # ---- geometry ----------------------------------------------------------
    def T(self, pts):
        zx, zy = self.zc
        z = self.zoom
        return [((x - zx) * z + zx + self.ox, (y - zy) * z + zy + self.oy) for x, y in pts]

    def rng(self, key):
        return random.Random(zlib.crc32(f"{key}|{self.boil}".encode()))

    def jag(self, pts, key, amt=2.5, step=40):
        r = self.rng(key)
        out = []
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
            for k in range(n):
                f = k / n
                out.append((x0 + (x1 - x0) * f + r.uniform(-amt, amt), y0 + (y1 - y0) * f + r.uniform(-amt, amt)))
        return out

    def ell(self, cx, cy, rx, ry, key="", amt=0.012, rot=0.0, a0=0.0, a1=2 * math.pi, n=None):
        r = self.rng(key)
        n = n or max(20, int((abs(rx) + abs(ry)) / 5))
        full = abs(a1 - a0 - 2 * math.pi) < 1e-6
        pts = []
        cr, sr = math.cos(rot), math.sin(rot)
        for i in range(n if full else n + 1):
            a = a0 + (a1 - a0) * i / n
            k = 1 + r.uniform(-amt, amt)
            x, y = math.cos(a) * rx * k, math.sin(a) * ry * k
            pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
        return pts

    def rrect_pts(self, x, y, w, h, rad, key=""):
        rad = min(rad, w / 2, h / 2)
        pts = []
        for cx, cy, a in ((x + w - rad, y + rad, -math.pi / 2), (x + w - rad, y + h - rad, 0),
                          (x + rad, y + h - rad, math.pi / 2), (x + rad, y + rad, math.pi)):
            for i in range(7):
                aa = a + math.pi / 2 * i / 6
                pts.append((cx + math.cos(aa) * rad, cy + math.sin(aa) * rad))
        return self.jag(pts, key, 1.5, 60)

    def capsule_pts(self, p0, p1, r):
        (x0, y0), (x1, y1) = p0, p1
        a = math.atan2(y1 - y0, x1 - x0)
        pts = []
        for i in range(9):
            aa = a - math.pi / 2 - math.pi * i / 8
            pts.append((x0 + math.cos(aa) * r, y0 + math.sin(aa) * r))
        for i in range(9):
            aa = a + math.pi / 2 - math.pi * i / 8
            pts.append((x1 + math.cos(aa) * r, y1 + math.sin(aa) * r))
        return pts

    # ---- painting ----------------------------------------------------------
    def poly(self, pts, color, ol=None, shadow=True, alpha=255, world=True):
        if len(pts) < 3:
            return
        if world:
            pts = self.T(pts)
        ol = self.ol if ol is None else ol
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        pad = ol + 24
        x0, y0 = int(max(0, min(xs) - pad)), int(max(0, min(ys) - pad))
        x1 = int(min(self.w, max(xs) + pad + self.shadow[0]))
        y1 = int(min(self.h, max(ys) + pad + self.shadow[1]))
        if x1 <= x0 or y1 <= y0:
            return
        bw, bh = x1 - x0, y1 - y0
        loc = [(x - x0, y - y0) for x, y in pts]
        fill = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(fill).polygon(loc, fill=255)
        outer = fill
        if ol:
            outer = fill.copy()
            d = ImageDraw.Draw(outer)
            d.line(loc + [loc[0]], fill=255, width=ol * 2, joint="curve")
            d.polygon(loc, fill=255)
        region = self.img.crop((x0, y0, x1, y1))
        a = alpha / 255
        if shadow and self.shadow_alpha:
            sm = Image.new("L", (bw, bh), 0)
            sm.paste(outer, self.shadow)
            sm = sm.filter(ImageFilter.BoxBlur(4)).point(lambda v: int(v * self.shadow_alpha / 255 * a))
            region.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (bw, bh), (0, 0, 0)).split(), sm)))
        if ol:
            m = outer.point(lambda v: int(v * a))
            region.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", (bw, bh), INK).split(), m)))
        g = grain(self.w, self.h)[y0:y1, x0:x1]
        col = np.clip(np.array(color[:3], np.float32)[None, None, :] * g, 0, 255).astype(np.uint8)
        m = fill.point(lambda v: int(v * a))
        region.alpha_composite(Image.merge("RGBA", (*Image.fromarray(col, "RGB").split(), m)))
        self.img.paste(region, (x0, y0))

    def rect(self, x, y, w, h, color, key="", amt=2.5, **kw):
        self.poly(self.jag([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], key, amt), color, **kw)

    def rrect(self, x, y, w, h, rad, color, key="", **kw):
        self.poly(self.rrect_pts(x, y, w, h, rad, key), color, **kw)

    def ellipse(self, cx, cy, rx, ry, color, key="", amt=0.012, rot=0.0, **kw):
        self.poly(self.ell(cx, cy, rx, ry, key, amt, rot), color, **kw)

    def circle(self, cx, cy, r, color, key="", **kw):
        self.ellipse(cx, cy, r, r, color, key, **kw)

    def shape(self, pts, color, key="", amt=2.0, **kw):
        self.poly(self.jag(pts, key, amt), color, **kw)

    def capsule(self, p0, p1, r, color, key="", **kw):
        self.poly(self.capsule_pts(p0, p1, r), color, **kw)

    def stroke(self, pts, width, color=INK, world=True, alpha=255):
        """Plain ink line (no outline), e.g. for facial features."""
        if world:
            pts = self.T(pts)
            width = width * self.zoom
        d = ImageDraw.Draw(self.img, "RGBA")
        d.line(pts, fill=tuple(color[:3]) + (alpha,), width=max(1, int(width)), joint="curve")
        r = width / 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(color[:3]) + (alpha,))

    def star(self, cx, cy, r, color, key="", points=4, inner=0.38, rot=0.0, **kw):
        pts = []
        for i in range(points * 2):
            a = rot + math.pi * i / points - math.pi / 2
            rr = r if i % 2 == 0 else r * inner
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        self.poly(pts, color, **kw)

    def text(self, txt, cx, cy, size, fill=INK, angle=0.0, world=False):
        if world:
            (cx, cy), = self.T([(cx, cy)])
            size = int(size * self.zoom)
        f = font(size)
        bb = f.getbbox(txt)
        tw, th = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
        tmp = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=tuple(fill[:3]) + (255,))
        if angle:
            tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))

    def overlay(self, color, alpha):
        self.img.alpha_composite(Image.new("RGBA", (self.w, self.h), tuple(color) + (int(max(0, min(255, alpha))),)))

    def paste(self, im, x, y):
        self.img.alpha_composite(im, (int(x), int(y)))
