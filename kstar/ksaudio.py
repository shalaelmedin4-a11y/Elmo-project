#!/usr/bin/env python3
"""Music + quiet SFX for 'Ein Tag als K-Pop-Star', timed from build/ks_timeline.json."""
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

with open(os.path.join(ROOT, "build", "ks_timeline.json")) as fh:
    TL = json.load(fh)
DUR = TL["dur"]
for m in (A, K):
    m.DUR = DUR
    m.N = int(DUR * A.SR)
SR, N = A.SR, A.N
SC = {s["name"]: s for s in TL["scenes"]}
rng = np.random.default_rng(33)


def at(name, local):
    return SC[name]["start"] + local


def curve(points):
    ts, gs = zip(*sorted(points))
    return np.interp(np.arange(N) / SR, ts, gs)


def music():
    br, dk = K.bright_stem(), K.dark_stem()
    cut = at("stage", SC["stage"]["cues"][1][0] - 0.35)
    st, en = SC["stage"]["start"], SC["intro"]["end"]
    g_bright = curve([(0, .9), (en - .2, .9), (en + .1, 0), (st - .05, 0), (st, .8), (cut - .02, .8), (cut, 0), (DUR, 0)])
    g_dark = curve([(0, 0), (en - .1, 0), (en + .4, .5), (st - .1, .5), (st, 0), (cut, 0), (cut + .5, .45),
                    (at("practice", 0), .4), (at("outro", 0), .4), (DUR, .55)])
    g_arp = curve([(0, 0), (at("outro", 0), 0), (at("outro", 1.5), .22), (DUR, .22)])
    L = br.L * (g_bright + g_arp) + dk.L * g_dark
    R = br.R * (g_bright + g_arp) + dk.R * g_dark
    return L, R


def sfx():
    tr = A.Track()
    # intro: one paper thump per sign, sparkle on the last one, a ding for the pose
    for t0 in (0.02, 1.0, 2.5):
        tr.add(A.paper_thump(), t0, .26)
    tr.add(A.sparkle(), 2.55, .06, .2)
    tr.add(A.ding(), 2.78, .06)
    # 05:00 van
    v = SC["van"]
    L = v["end"] - v["start"]
    tr.add(A.engine(L) * .6, v["start"], .07)
    for k in range(int(L * 1.1)):
        tr.add(A.whoosh(.35), v["start"] + .3 + k * .9, .025, .5)
    tr.add(A.thud(.08, 400), at("van", 2.0), .05)
    tr.add(A.thud(.08, 400), at("van", 2.25), .05)
    tr.add(A.band(A.noise(1.2), 1500, 7000) * np.linspace(1, .2, int(1.2 * SR)), at("van", 2.7), .035, .4)
    # 07:00 make-up
    m = SC["makeup"]
    L = m["end"] - m["start"]
    tr.add(A.band(A.noise(L), 300, 3000), m["start"], .025, .5)            # hair dryer
    for k in range(int(L * 2.5)):
        tr.add(A.band(A.noise(.15), 2500, 8000) * A.env(int(.15 * SR), .03, .05), m["start"] + k * .4, .02, -.5)
    # 10:00 stage -> backstage
    cut = at("stage", SC["stage"]["cues"][1][0] - 0.35)
    tr.add(A.cheer(cut - SC["stage"]["start"]), SC["stage"]["start"], .05)
    for _ in range(5):
        tr.add(K.shutter(), rng.uniform(SC["stage"]["start"] + .2, cut - .2), .05, rng.uniform(-.6, .6))
    tr.add(A.room_tone(SC["stage"]["end"] - cut), cut, .03)
    # 14:00 office: clock ticking + contract sliding
    o = SC["office"]
    k = 0
    while o["start"] + k < o["end"]:
        tr.add(K.click(.02, 3200), o["start"] + .2 + k, .04, .6)
        k += 1
    tr.add(A.band(A.noise(1.1), 800, 4000) * np.sin(np.linspace(0, np.pi, int(1.1 * SR))), at("office", 0.8), .045)
    # 18:00 phone: a soft notification for every note
    for n in range(9):
        tr.add(A.blip(1900 if n % 2 else 1500, .2), at("phone", 0.6 + n * .75), .035, .3)
    # 23:00 practice: sneaker squeaks while dancing, then cloth when she sits
    p = SC["practice"]
    sit = p["start"] + p["cues"][0][1] + .1
    for _ in range(8):
        tr.add(K.squeak(), rng.uniform(p["start"] + .1, sit - .2), .035, rng.uniform(-.4, .4))
    tr.add(A.band(A.noise(.6), 200, 1500) * A.env(int(.6 * SR), .1, .2), sit, .035)
    # outro
    tr.add(A.ding(), at("outro", 0.3), .04)
    return tr


def main(out):
    mL, mR = music()
    s = sfx()
    L, R = mL * .5 + s.L, mR * .5 + s.R
    fade = np.ones(N)
    fade[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR))
    L, R = L * fade, R * fade
    g = 0.5 / max(np.max(np.abs(L)), np.max(np.abs(R)))
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.stack([L, R], 1) * g * 32767).astype("<i2").tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "kstar_bed.wav"))
