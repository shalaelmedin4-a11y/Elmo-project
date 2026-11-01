#!/usr/bin/env python3
"""Render 'Ein Tag als K-Pop Trainee' (12 fps stop-motion, 1080x1920 @ 30 fps).

usage: python3 krender.py out.mp4 | python3 krender.py OUTDIR --still t1,t2,...
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np

import kcast  # noqa: F401  (sets up the import path)
import cast
from cast import INK, WHITE
from kscenes import DUR, TIMELINE
from paper import H, W, Ctx, composite, make_paper_texture, subtitle

FPS = 12
SUB_Y, SUB_Y_INTRO = 820, 330
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = LIPS = None
SUBTITLES = []
YY, XX = np.mgrid[0:H, 0:W]


def _init():
    global TEX, LIPS
    TEX = make_paper_texture(seed=11)
    try:
        with open(os.path.join(ROOT, "build", "k_lipsync.json")) as fh:
            data = json.load(fh)
        LIPS, cues = data["level"], data["cues"]
    except OSError:
        cues = []
    for i, cu in enumerate(cues):
        nxt = cues[i + 1]["start"] - 0.05 if i + 1 < len(cues) else DUR
        SUBTITLES.append((cu["start"] - 0.08, min(nxt, max(cu["end"] + 0.7, cu["start"] + 1.4)), cu["text"]))


def clock(c, txt):
    c.cam = (540, 960, 1.0)
    c.stack = [np.eye(3)]
    c.layer = "ui"
    c.push(905, 175, 1, -4)
    c.rrect(-140, -58, 140, 58, 18, (255, 236, 246), w=6)
    c.ell(-88, 0, 36, 36, (255, 92, 170), w=5, n=24)
    c.ell(-88, 0, 26, 26, WHITE, w=3, n=20)
    h = int(txt[:2]) % 12 + int(txt[3:]) / 60
    m = int(txt[3:])
    for ang, ln, wd in ((h / 12 * 360, 15, 5), (m / 60 * 360, 22, 4)):
        a = math.radians(ang - 90)
        c.line([(-88, 0), (-88 + math.cos(a) * ln, math.sin(a) * ln)], wd)
    c.text(36, 3, txt, 58, fill=INK)
    c.pop()


def apply_look(img, look):
    arr = np.asarray(img, np.float32)
    lum = arr @ np.array([.3, .59, .11], np.float32)
    arr = lum[..., None] + (arr - lum[..., None]) * look.get("sat", 1.0)
    arr *= np.array(look.get("tint", (1, 1, 1)), np.float32)
    spot = look.get("spot")
    if spot:
        x, y, r, dark = spot
        d = np.sqrt((XX - x) ** 2 + (YY - y) ** 2) / r
        k = np.clip(1 - d, 0, 1) ** 1.2
        arr *= (dark + (1.08 - dark) * k)[..., None]
    from PIL import Image
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def frame(f):
    t = f / FPS
    cast.SPEAK[0] = LIPS[f] if LIPS and f < len(LIPS) else 0.0
    cast.SPEAK[1] = f
    for start, end, stamp, fn in TIMELINE:
        if start <= t < end:
            break
    c = Ctx(f)
    look = fn(c, t - start)
    if stamp:
        clock(c, stamp(t - start) if callable(stamp) else stamp)
    img = apply_look(composite(c, TEX, None), look)
    for a, b, txt in SUBTITLES:
        if a <= t < b:
            subtitle(img, txt, y=SUB_Y_INTRO if t < 4.0 else SUB_Y)
    return np.asarray(img).tobytes()


def main():
    args = sys.argv[1:]
    if "--still" in args:
        from PIL import Image
        out_dir = args[0]
        os.makedirs(out_dir, exist_ok=True)
        _init()
        for tt in [float(x) for x in args[args.index("--still") + 1].split(",")]:
            Image.frombytes("RGB", (W, H), frame(int(round(tt * FPS)))).resize((540, 960)).save(f"{out_dir}/t{tt:05.1f}.png")
        return
    out = args[0] if args else os.path.join(ROOT, "build", "kpop_video.mp4")
    n = int(DUR * FPS)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-vf", "fps=30", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
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
