#!/usr/bin/env python3
"""Render the cartoon video frames (12 fps 'on twos' stop-motion) and encode.

usage: python3 render.py [out.mp4] [--frames a:b] [--still t1,t2,...]
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np

import cast
from cast import INK, WHITE, lerp
from paper import H, W, Ctx, composite, make_paper_texture, subtitle
from scenes import INTRO, LAMP, SCENES, SUB_Y, SUBS, intro

FPS = 12
DUR = 49.0  # 4 s intro + 45 s story
TEX = None


LIPS = None
SUBTITLES = []   # (start, end, text) in final-video time, from the voice cues


def _init():
    global TEX, LIPS, SUBTITLES
    TEX = make_paper_texture()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(root, "build", "lipsync.json")) as fh:
            data = json.load(fh)
        LIPS = data["level"]
        cues = data["cues"]
    except OSError:
        from voice import CUES
        cues = [{"start": c[0], "end": c[0] + 2.0, "text": c[1]} for c in CUES]
    for i, cu in enumerate(cues):
        nxt = cues[i + 1]["start"] - 0.05 if i + 1 < len(cues) else DUR
        SUBTITLES.append((cu["start"] - 0.08, min(nxt, max(cu["end"] + 0.9, cu["start"] + 1.6)), cu["text"]))


def radial_grade(cx, cy, warm=(1.12, 1.0, 0.82), cold=(0.42, 0.48, 0.78), r=760):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    k = np.clip(1 - d, 0, 1)[..., None] ** 1.3
    return (np.array(cold) * (1 - k) + np.array(warm) * k).astype(np.float32)


_grades = {}


def clock(c, txt):
    c.cam = (540, 960, 1.0)
    c.stack = [np.eye(3)]
    c.layer = "ui"
    c.push(905, 175, 1, -4)
    c.rrect(-140, -58, 140, 58, 18, (255, 244, 214), w=6)
    c.ell(-88, 0, 36, 36, (240, 90, 70), w=5, n=24)
    c.ell(-88, 0, 26, 26, WHITE, w=3, n=20)
    h = int(txt[:2]) % 12 + int(txt[3:]) / 60
    m = int(txt[3:])
    for ang, ln, wd in ((h / 12 * 360, 15, 5), (m / 60 * 360, 22, 4)):
        a = math.radians(ang - 90)
        c.line([(-88, 0), (-88 + math.cos(a) * ln, math.sin(a) * ln)], wd)
    c.text(36, 3, txt, 58, fill=INK)
    c.pop()


def subs(img, t_abs):
    for a, b, txt in SUBTITLES:
        if a <= t_abs < b:
            subtitle(img, txt, y=330 if t_abs < INTRO else SUB_Y)


def frame(f):
    t = f / FPS
    cast.SPEAK[0] = LIPS[f] if LIPS and f < len(LIPS) else 0.0
    cast.SPEAK[1] = f
    if t < INTRO:
        c = Ctx(f)
        grade = np.array(intro(c, t), np.float32)
        img = composite(c, TEX, grade)
        subs(img, t)
        return np.asarray(img).tobytes()
    t_abs = t
    t -= INTRO
    for start, end, stamp, fn in SCENES:
        if start <= t < end or (fn is SCENES[-1][3] and t >= start):
            break
    c = Ctx(f)
    grade = fn(c, t - start)
    if isinstance(grade, tuple) and grade and grade[0] == "lamp":  # night: warm lamp, cold room
        off = t >= 44.5
        key = (grade[1], off)
        if key not in _grades:
            cx, cy, z = c.cam
            lx, ly = LAMP
            sx, sy = (lx - cx) * z + W / 2, (ly - cy) * z + H / 2
            _grades[key] = radial_grade(sx, sy, (.5, .52, .68), (.28, .3, .5)) if off else radial_grade(sx, sy)
        grade = _grades[key]
    else:
        grade = np.array(grade, np.float32)
    clock(c, stamp)
    img = composite(c, TEX, grade)
    subs(img, t_abs)
    return np.asarray(img).tobytes()


def main():
    args = sys.argv[1:]
    if "--still" in args:
        times = [float(x) for x in args[args.index("--still") + 1].split(",")]
        out_dir = args[0]
        os.makedirs(out_dir, exist_ok=True)
        _init()
        from PIL import Image
        for tt in times:
            Image.frombytes("RGB", (W, H), frame(int(round(tt * FPS)))).resize((540, 960)).save(f"{out_dir}/t{tt:05.1f}.png")
        return
    out = args[0] if args else "build/cartoon_video.mp4"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
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
