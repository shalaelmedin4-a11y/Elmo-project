#!/usr/bin/env python3
"""Render 'Ein Tag als Profifußballer … mit Halbo!' (clean anime look, 1080x1920).

usage: python3 fb_render.py out.mp4 | python3 fb_render.py OUTDIR --still t1,t2,...
"""
import json
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fb_rig  # noqa: E402,F401  (path setup)
import cast  # noqa: E402
from fb_scenes import FUNCS  # noqa: E402
from paper import FONT_BLACK, H, W, Ctx, font  # noqa: E402

FPS = 12
with open(os.path.join(ROOT, "build", "fb_timeline.json")) as fh:
    TL = json.load(fh)
DUR = TL["dur"]
YY, XX = np.mgrid[0:H, 0:W]
VIG = (1 - 0.28 * (((XX - W / 2) / (W * .8)) ** 2 + ((YY - H / 2) / (H * .8)) ** 2)).astype(np.float32)
GRAIN = None


def _init():
    global GRAIN
    GRAIN = np.random.default_rng(5).normal(0, 3.0, (4, H, W)).astype(np.float32)


def finish(c, look, f):
    base = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 255))
    for k in ("bg", "mid", "fg", "ui"):
        base.alpha_composite(c.img[k])
    img = base.convert("RGB").resize((W, H), Image.LANCZOS)
    arr = np.asarray(img, np.float32)
    # soft bloom: blurred highlights added back (soft warm light)
    hi = Image.fromarray(np.clip((arr - 170) * 1.6, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(18))
    arr = arr + np.asarray(hi, np.float32) * 0.22
    lum = arr @ np.array([.3, .59, .11], np.float32)
    arr = lum[..., None] + (arr - lum[..., None]) * look.get("sat", 0.85)
    warm = look.get("warm", 0.05)
    arr *= np.array([1 + warm, 1 + warm * .3, 1 - warm * .6], np.float32)
    arr *= np.array(look.get("tint", (1, 1, 1)), np.float32)
    if look.get("glow"):
        gx, gy, gr, gc = look["glow"]
        k = np.clip(1 - np.sqrt((XX - gx) ** 2 + (YY - gy) ** 2) / gr, 0, 1)[..., None] ** 1.5
        arr = arr * (1 - .25 * k) + np.array(gc, np.float32) * .25 * k
    if look.get("spot"):
        x, y, r, dark = look["spot"]
        k = np.clip(1 - np.sqrt((XX - x) ** 2 + (YY - y) ** 2) / r, 0, 1) ** 1.2
        arr *= (dark + (1.05 - dark) * k)[..., None]
    arr = arr * VIG[..., None] + GRAIN[f % 4][..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def time_pill(img, txt):
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((44, 70, 300, 162), radius=46, fill=(24, 24, 30, 170))
    d.ellipse((66, 92, 114, 140), outline=(250, 214, 96), width=5)
    d.line((90, 116, 90, 100), fill=(250, 214, 96), width=5)
    d.line((90, 116, 102, 122), fill=(250, 214, 96), width=5)
    d.text((132, 116), txt, font=font(54, FONT_BLACK), fill=(250, 250, 246), anchor="lm")


def frame(f):
    t = f / FPS
    lv = TL["level"]
    cast.SPEAK[0] = lv[f] if f < len(lv) else 0.0
    cast.SPEAK[1] = f
    sc = TL["scenes"][-1]
    for s in TL["scenes"]:
        if s["start"] <= t < s["end"]:
            sc = s
            break
    c = Ctx(f)
    c.boil = 0
    look = FUNCS[sc["name"]](c, t - sc["start"], sc["end"] - sc["start"], sc["cues"])
    img = finish(c, look, f)
    if sc["clock"]:
        time_pill(img, sc["clock"])
    return np.asarray(img).tobytes()


def main():
    args = sys.argv[1:]
    if "--still" in args:
        out_dir = args[0]
        os.makedirs(out_dir, exist_ok=True)
        _init()
        for tt in [float(x) for x in args[args.index("--still") + 1].split(",")]:
            Image.frombytes("RGB", (W, H), frame(int(round(tt * FPS)))).resize((540, 960)).save(f"{out_dir}/t{tt:05.1f}.png")
        return
    out = args[0]
    n = int(DUR * FPS)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-vf", "fps=24", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "22", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count(), initializer=_init) as pool:
        for i, buf in enumerate(pool.imap(frame, range(n), chunksize=4)):
            enc.stdin.write(buf)
            if i % 60 == 0:
                print(f"frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
