"""Tiny 'construction paper cut-out' drawing kit on top of Pillow.

Everything is a polygon with a thick dark outline. Each frame the shapes get a
small random offset ("boil") so the result looks like hand-placed paper pieces
in stop-motion. Layers: bg (flat, no shadow), mid (set pieces) and fg
(characters, props); mid/fg/ui cast a soft paper shadow.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SS = 2                       # supersampling factor
INK = (38, 30, 42)
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

_font_cache = {}


def font(size, path=FONT_BLACK):
    key = (path, int(size))
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, int(size))
        except OSError:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def _mat(x=0, y=0, s=1, rot=0, sx=1):
    r = math.radians(rot)
    c, n = math.cos(r), math.sin(r)
    T = np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], float)
    R = np.array([[c, -n, 0], [n, c, 0], [0, 0, 1]], float)
    S = np.array([[s * sx, 0, 0], [0, s, 0], [0, 0, 1]], float)
    return T @ R @ S


class Ctx:
    LAYERS = ("bg", "mid", "fg", "ui")

    def __init__(self, frame, cam=(540, 960, 1.0)):
        self.img = {k: Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)) for k in self.LAYERS}
        self.drw = {k: ImageDraw.Draw(v) for k, v in self.img.items()}
        self.layer = "mid"
        self.stack = [np.eye(3)]
        self.cam = cam
        self.rng = random.Random(frame * 7919 + 17)
        self.boil = 1.4

    # ---- transform stack -------------------------------------------------
    def push(self, x=0, y=0, s=1, rot=0, flip=False):
        self.stack.append(self.stack[-1] @ _mat(x, y, s, rot, -1 if flip else 1))

    def pop(self):
        self.stack.pop()

    def scale(self):
        M = self.stack[-1]
        return math.sqrt(abs(M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0])) * self.cam[2] * SS

    def tf(self, pts, jit=True):
        M = self.stack[-1]
        cx, cy, z = self.cam
        ox = oy = 0.0
        if jit and self.boil:
            ox, oy = self.rng.uniform(-1, 1) * self.boil, self.rng.uniform(-1, 1) * self.boil
        out = []
        for x, y in pts:
            X = M[0, 0] * x + M[0, 1] * y + M[0, 2]
            Y = M[1, 0] * x + M[1, 1] * y + M[1, 2]
            jx = jy = 0.0
            if jit and self.boil:
                jx, jy = self.rng.uniform(-.6, .6), self.rng.uniform(-.6, .6)
            out.append((((X - cx) * z + W / 2 + ox + jx) * SS, ((Y - cy) * z + H / 2 + oy + jy) * SS))
        return out

    # ---- primitives ------------------------------------------------------
    def poly(self, pts, fill, ol=INK, w=5, jit=True):
        P = self.tf(pts, jit)
        wd = max(1, int(round(w * self.scale() / SS * SS))) if ol else 0
        self.drw[self.layer].polygon(P, fill=fill, outline=ol if ol else None, width=wd)

    def ell(self, cx, cy, rx, ry, fill, ol=INK, w=5, n=30, a0=0, a1=360, jit=True):
        pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
               for a in np.linspace(a0, a1, n, endpoint=(a1 - a0) < 360)]
        self.poly(pts, fill, ol, w, jit)

    def rect(self, x0, y0, x1, y1, fill, ol=INK, w=5, jit=True):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, ol, w, jit)

    def rrect(self, x0, y0, x1, y1, r, fill, ol=INK, w=5):
        pts = []
        for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(6):
                t = math.radians(a + 90 * k / 5)
                pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        self.poly(pts, fill, ol, w)

    def line(self, pts, w=5, col=INK, jit=True):
        P = self.tf(pts, jit)
        self.drw[self.layer].line(P, fill=col, width=max(1, int(w * self.scale())), joint="curve")

    def arc(self, cx, cy, rx, ry, a0, a1, w=5, col=INK):
        pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
               for a in np.linspace(a0, a1, 12)]
        self.line(pts, w, col)

    def text(self, x, y, s, size, fill=INK, stroke=0, stroke_fill=(255, 255, 255), anchor="mm"):
        (X, Y), = self.tf([(x, y)])
        sc = self.scale()
        self.drw[self.layer].text((X, Y), s, font=font(size * sc), fill=fill, anchor=anchor,
                                  stroke_width=int(stroke * sc), stroke_fill=stroke_fill)


# ---- paper texture & compositing ------------------------------------------

def make_paper_texture(seed=3):
    rng = np.random.default_rng(seed)
    coarse = Image.fromarray((rng.random((H // 8, W // 8)) * 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    coarse = np.asarray(coarse.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255 - .5
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    fibers = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fibers)
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        a, ln = rng.uniform(0, math.pi), rng.uniform(8, 40)
        d.line([(x, y), (x + ln * math.cos(a), y + ln * math.sin(a))], fill=int(rng.uniform(40, 120)), width=1)
    fibers = np.asarray(fibers.filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
    tex = 1 + coarse * .10 + fine * .022 - fibers * .07
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - .22 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .75)) ** 2)
    return (tex * vig).astype(np.float32)


def composite(ctx, tex, grade=None):
    """Down-sample layers, add paper shadows, apply colour grade and texture."""
    small = {k: v.resize((W, H), Image.LANCZOS) for k, v in ctx.img.items()}
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base.alpha_composite(small["bg"])
    for k in ("mid", "fg", "ui"):
        a = small[k].getchannel("A").filter(ImageFilter.GaussianBlur(5))
        sh = Image.new("RGBA", (W, H), (25, 10, 35, 0))
        sh.putalpha(a.point(lambda v: int(v * .42)))
        base.alpha_composite(sh, (6, 9))
        base.alpha_composite(small[k])
    arr = np.asarray(base.convert("RGB"), np.float32)
    if grade is not None:
        arr = arr * grade
    arr = arr * tex[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def subtitle(img, text, y=900, size=78):
    """Bold white subtitle with thick black outline, centred, wrapped to ~900px."""
    d = ImageDraw.Draw(img)
    f = font(size, FONT_BLACK)
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=f) > 900 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    lh = size * 1.18
    y0 = y - lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        d.text((W / 2 + 4, y0 + i * lh + 6), ln, font=f, fill=(0, 0, 0), anchor="mm",
               stroke_width=10, stroke_fill=(0, 0, 0))
        d.text((W / 2, y0 + i * lh), ln, font=f, fill=(255, 255, 255), anchor="mm",
               stroke_width=9, stroke_fill=(10, 8, 12))
