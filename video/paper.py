"""Construction-paper cut-out drawing helpers (PIL).

Every shape is a slightly jagged, hand-cut polygon with a soft drop shadow
and paper grain. Edges "boil" (re-cut) every few animation frames, which
gives the choppy stop-motion feel."""
import math, random, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_grain_cache = {}


def grain(size):
    if size not in _grain_cache:
        rng = np.random.default_rng(7)
        w, h = size
        n = rng.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
        img = Image.fromarray(np.clip(128 + n * 30, 0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
        fib = rng.normal(0, 1, (h // 8 + 1, w // 2 + 1)).astype(np.float32)
        fimg = Image.fromarray(np.clip(128 + fib * 25, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        a = (np.asarray(img, np.float32) * 0.6 + np.asarray(fimg, np.float32) * 0.4 - 128) / 128
        _grain_cache[size] = (1 + a * 0.07)[..., None]
    return _grain_cache[size]


class Canvas:
    def __init__(self, w, h, frame, bg=(255, 255, 255), boil_every=2):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), bg + (255,))
        self.frame = frame
        self.boil = frame // boil_every
        self.shadow = (10, 12)
        self.shadow_alpha = 90

    # ---- jagged geometry -------------------------------------------------
    def rng(self, key):
        return random.Random(zlib.crc32(f"{key}|{self.boil}".encode()))

    def jag_poly(self, pts, key, amt=3.0, sub=10):
        r = self.rng(key)
        out = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            seglen = math.hypot(x1 - x0, y1 - y0)
            steps = max(1, int(seglen / (sub * 6)))
            for s in range(steps):
                f = s / steps
                out.append((x0 + (x1 - x0) * f + r.uniform(-amt, amt), y0 + (y1 - y0) * f + r.uniform(-amt, amt)))
        return out

    def ellipse_pts(self, cx, cy, rx, ry, key, amt=0.02, n=None, rot=0.0, a0=0, a1=2 * math.pi):
        r = self.rng(key)
        n = n or max(18, int((rx + ry) / 6))
        pts = []
        full = abs(a1 - a0 - 2 * math.pi) < 1e-6
        cnt = n if full else n + 1
        cr, sr = math.cos(rot), math.sin(rot)
        for i in range(cnt):
            a = a0 + (a1 - a0) * i / n
            k = 1 + r.uniform(-amt, amt)
            x, y = math.cos(a) * rx * k, math.sin(a) * ry * k
            pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
        return pts

    # ---- painting ----------------------------------------------------------
    def poly(self, pts, color, shadow=True, alpha=255):
        if len(pts) < 3:
            return
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        pad = 30
        x0 = int(max(0, min(xs) - pad)); y0 = int(max(0, min(ys) - pad))
        x1 = int(min(self.w, max(xs) + pad + self.shadow[0])); y1 = int(min(self.h, max(ys) + pad + self.shadow[1]))
        if x1 <= x0 or y1 <= y0:
            return
        bw, bh = x1 - x0, y1 - y0
        loc = [(x - x0, y - y0) for x, y in pts]
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).polygon(loc, fill=alpha)
        region = self.img.crop((x0, y0, x1, y1))
        if shadow and self.shadow_alpha:
            sm = Image.new("L", (bw, bh), 0)
            ImageDraw.Draw(sm).polygon([(x + self.shadow[0], y + self.shadow[1]) for x, y in loc], fill=self.shadow_alpha * alpha // 255)
            sm = sm.filter(ImageFilter.BoxBlur(5))
            region = Image.composite(Image.new("RGBA", (bw, bh), (0, 0, 0, 255)), region, sm)
        g = grain((self.w, self.h))[y0:y1, x0:x1]
        col = np.clip(np.array(color[:3], np.float32)[None, None, :] * g, 0, 255).astype(np.uint8)
        fill = Image.fromarray(col, "RGB").convert("RGBA")
        region = Image.composite(fill, region, mask)
        self.img.paste(region, (x0, y0))

    def rect(self, x, y, w, h, color, key, amt=3, **kw):
        self.poly(self.jag_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], key, amt), color, **kw)

    def ellipse(self, cx, cy, rx, ry, color, key, amt=0.02, rot=0.0, **kw):
        self.poly(self.ellipse_pts(cx, cy, rx, ry, key, amt, rot=rot), color, **kw)

    def circle(self, cx, cy, r, color, key, **kw):
        self.ellipse(cx, cy, r, r, color, key, **kw)

    def tri(self, pts, color, key, amt=3, **kw):
        self.poly(self.jag_poly(pts, key, amt), color, **kw)

    def thick_line(self, p0, p1, width, color, key, **kw):
        (x0, y0), (x1, y1) = p0, p1
        d = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / d * width / 2, (x1 - x0) / d * width / 2
        pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
        self.poly(self.jag_poly(pts, key, 2), color, **kw)

    def star(self, cx, cy, r, color, key, points=4, inner=0.35, rot=0.0, **kw):
        pts = []
        for i in range(points * 2):
            a = rot + math.pi * i / points - math.pi / 2
            rr = r if i % 2 == 0 else r * inner
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        self.poly(pts, color, **kw)

    def paste_sprite(self, sprite, cx, cy, angle=0.0, sx=1.0, sy=1.0):
        s = sprite
        if sx != 1 or sy != 1:
            s = s.resize((max(1, int(s.width * sx)), max(1, int(s.height * sy))), Image.BICUBIC)
        if angle:
            s = s.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

    def overlay(self, color, alpha):
        ov = Image.new("RGBA", (self.w, self.h), color + (int(alpha),))
        self.img.alpha_composite(ov)

    def text(self, txt, cx, cy, size, fill=(255, 255, 255), stroke=(0, 0, 0), sw=8, angle=0, key=None):
        font = ImageFont.truetype(FONT_BOLD, size)
        tmp = Image.new("RGBA", (self.w, int(size * 1.4 * (txt.count("\n") + 1)) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        d.multiline_text((tmp.width / 2, tmp.height / 2), txt, font=font, fill=fill, anchor="mm",
                         align="center", stroke_width=sw, stroke_fill=stroke, spacing=size * 0.18)
        if angle:
            tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))


def sprite_canvas(w, h, frame):
    c = Canvas(w, h, frame)
    c.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return c
