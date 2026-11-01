#!/usr/bin/env python3
"""Very quiet pop music for version 2 (bright on stage, slow and soft in the grey scenes).
Almost no sound effects - only a soft chime at the very end."""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "kpop"))
sys.path.insert(0, os.path.join(ROOT, "cartoon"))
import audio as A  # noqa: E402
import kaudio as K  # noqa: E402

with open(os.path.join(ROOT, "build", "k2_timeline.json")) as fh:
    TL = json.load(fh)
DUR = TL["dur"]
for m in (A, K):
    m.DUR = DUR
    m.N = int(DUR * A.SR)
SR, N = A.SR, A.N
BRIGHT = {"intro", "fans", "concert"}


def main(out):
    br, dk = K.bright_stem(), K.dark_stem()
    pts_b, pts_d = [], []
    for s in TL["scenes"]:
        b = 0.7 if s["name"] in BRIGHT else 0.0
        d = 0.0 if s["name"] in BRIGHT else 0.5
        for tt in (s["start"] + .02, s["end"] - .02):
            pts_b.append((tt, b))
            pts_d.append((tt, d))
    tax = np.arange(N) / SR
    gb = np.interp(tax, *zip(*pts_b))
    gd = np.interp(tax, *zip(*pts_d))
    L = br.L * gb + dk.L * gd
    R = br.R * gb + dk.R * gd
    ch = A.Track()
    intro = TL["scenes"][0]
    c1 = intro["cues"]
    for t0 in (0.0, c1[0][0] + 0.45 * (c1[0][1] - c1[0][0]), c1[1][0]):   # very soft paper thump per sign
        ch.add(A.paper_thump(), t0, .10)
    ch.add(A.ding(), DUR - 1.6, .03)
    L, R = L * .5 + ch.L, R * .5 + ch.R
    fade = np.ones(N)
    fade[-int(1.0 * SR):] = np.linspace(1, 0, int(1.0 * SR))
    L, R = L * fade, R * fade
    g = 0.5 / max(np.max(np.abs(L)), np.max(np.abs(R)))
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.stack([L, R], 1) * g * 32767).astype("<i2").tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "kstar2_bed.wav"))
