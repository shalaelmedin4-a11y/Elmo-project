#!/usr/bin/env python3
"""Quiet lo-fi background music + scene sounds for the football video (timed from fb_timeline.json)."""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cartoon"))
sys.path.insert(0, os.path.join(ROOT, "kpop"))
import audio as A  # noqa: E402
import kaudio as K  # noqa: E402

with open(os.path.join(ROOT, "build", "fb_timeline.json")) as fh:
    TL = json.load(fh)
DUR = TL["dur"]
for m in (A, K):
    m.DUR = DUR
    m.N = int(DUR * A.SR)
SR, N = A.SR, A.N
SC = {s["name"]: s for s in TL["scenes"]}
rng = np.random.default_rng(77)
band, noise, t_axis, norm = A.band, A.noise, A.t_axis, A.norm


def at(name, lt):
    return SC[name]["start"] + lt


def length(name):
    return SC[name]["end"] - SC[name]["start"]


# ---------------------------------------------------------------- lo-fi music
def rhodes(f, d=1.8):
    t = t_axis(d)
    trem = 1 + .15 * np.sin(2 * np.pi * 4.5 * t)
    s = (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + .2 * np.sin(6 * np.pi * f * t) * np.exp(-t * 6))
    return s * trem * np.minimum(1, t / .01) * np.exp(-t * 1.1)


def lofi():
    tr = A.Track()
    bpm = 80
    beat = 60 / bpm
    prog = [(146.8, 174.6, 220.0, 261.6), (130.8, 164.8, 196.0, 246.9), (110.0, 130.8, 164.8, 196.0),
            (123.5, 146.8, 185.0, 220.0)]                   # Dm9-ish / Cmaj7 / Am7 / Bm7b5-ish
    bars = int(DUR / (beat * 4)) + 1
    for b in range(bars):
        tb = b * beat * 4
        for f in prog[b % 4]:
            tr.add(rhodes(f, beat * 4 + .5), tb + rng.uniform(0, .02), .10)
        tr.add(rhodes(prog[b % 4][0] / 2, beat * 4), tb, .12)
        for k in range(4):
            if k in (0, 2):
                tr.add(A.kick(), tb + k * beat + (0.04 if k == 2 else 0), .30)
            else:
                tr.add(A.snare(soft=.7), tb + k * beat, .10, .1)
            for h in range(2):
                tr.add(K.hat(), tb + k * beat + h * beat / 2 + (0.03 if h else 0), .035, .3)
    crackle = np.zeros(N)
    idx = rng.integers(0, N, int(DUR * 25))
    crackle[idx] = rng.uniform(-1, 1, len(idx))
    crackle = band(crackle, 1000, 9000) * 0.6 + band(noise(DUR), 200, 3000) * 0.02
    L, R = tr.L + crackle[:N] * .2, tr.R + crackle[:N] * .2
    # a little quieter in the match (crowd takes over) and at night
    g = np.interp(np.arange(N) / SR, [0, SC["match"]["start"], SC["match"]["start"] + .5, SC["night"]["start"], DUR],
                  [1, 1, .6, .7, .5])
    return L * g, R * g


# ---------------------------------------------------------------- sounds
def alarm(d=0.12):
    t = t_axis(d)
    return np.sign(np.sin(2 * np.pi * 1760 * t)) * .5 * np.minimum(1, (d - t) / .01)


def crowd(d, excite=0.0):
    s = band(noise(d), 300, 2500)
    mod = np.interp(np.arange(len(s)), np.linspace(0, len(s), int(d * 4) + 2), rng.uniform(.6, 1, int(d * 4) + 2))
    return norm(s * mod * (1 + excite))


def roar(d=3.5):
    t = t_axis(d)
    env = np.minimum(1, t / .25) * np.exp(-np.maximum(0, t - .8) * .8)
    return norm(band(noise(d), 250, 3500) * env + A.cheer(d) * .6 * env)


def whistle_ref(d=0.7):
    return A.whistle(d)


def kick_sfx():
    return norm(A.thud(.12, 120) + .5 * band(noise(.12), 400, 3000) * np.exp(-t_axis(.12) * 40))


def splash(d=1.0):
    t = t_axis(d)
    return norm(band(noise(d), 300, 6000) * np.exp(-t * 4) + .3 * band(noise(d), 2000, 8000) * np.exp(-t * 10))


def steps(tr, a, b, rate, gain, f=110):
    k = 0
    while a + k / rate < b:
        tr.add(A.thud(.08, f), a + k / rate, gain, rng.uniform(-.3, .3))
        k += 1


def sfx():
    tr = A.Track()
    # intro
    tr.add(A.whoosh(.5), 0.05, .10)
    tr.add(A.boing(.3, 400, 900), at("intro", SC["intro"]["cues"][1][0] - .05), .06)
    # 06:30
    for k in range(5):
        tr.add(alarm(), at("wake", .2 + k * .3), .10, .3)
    for _ in range(8):
        tr.add(A.chirp_bird(), at("wake", rng.uniform(.2, length("wake"))), .04, rng.uniform(-.8, .8))
    tr.add(band(noise(.6), 200, 1500) * A.env(int(.6 * SR), .1, .2), at("wake", 1.75), .07)
    # 07:30
    cut = SC["breakfast"]["cues"][1][0] - .25
    for k in range(int(cut * 1.4)):
        tr.add(K.click(.02, 4200), at("breakfast", .3 + k / 1.4), .05, .3)
    tr.add(band(noise(.5), 300, 2000) * A.env(int(.5 * SR), .1, .15), at("breakfast", cut + .4), .04)
    # 09:30 training
    Lt = length("training")
    tr.add(whistle_ref(.35), at("training", .05), .05, .4)
    steps(tr, at("training", 0), at("training", Lt / 3), 6.4, .06)
    tr.add(kick_sfx(), at("training", Lt / 3 + .55), .20)
    steps(tr, at("training", 2 * Lt / 3), at("training", Lt), 5.8, .06)
    tr.add(A.thud(.1, 160), at("training", 2 * Lt / 3 + .4), .08)
    # 12:00 canteen
    tr.add(A.murmur(length("canteen")), at("canteen", 0), .05)
    for _ in range(8):
        tr.add(A.blip(rng.uniform(2600, 4000), .07), at("canteen", rng.uniform(0, length("canteen"))), .025)
    # 14:00 home
    cut = length("home") * .55
    for k in range(int(cut * 7)):
        tr.add(K.click(.015, 2600), at("home", k / 7 + rng.uniform(0, .05)), .03, .2)
    tr.add(band(noise(cut), 200, 4000) * .3, at("home", 0), .03, .4)          # game sound from the TV
    tr.add(A.snore(length("home") - cut, .25), at("home", cut), .04)
    # 17:00
    cut = length("drive") * .48
    tr.add(A.engine(cut) * .7, at("drive", 0), .08)
    tr.add(crowd(length("drive") - cut), at("drive", cut), .07)
    tr.add(A.cheer(1.6), at("drive", cut + .4), .06)
    # 19:30 match
    m0, Lm = SC["match"]["start"], length("match")
    goal = SC["match"]["cues"][1][0] - .15
    tr.add(crowd(Lm), m0, .07)
    tr.add(whistle_ref(.8), m0 + .15, .09)
    steps(tr, m0 + 1.8, m0 + 6.6, 6.0, .05)
    tr.add(A.thud(.15, 90), m0 + 4.3, .12)                                      # duel
    tr.add(kick_sfx(), m0 + 6.6 + .25, .10)
    t_ = t_axis(1.1)                                                            # slow-motion strike (low, stretched)
    tr.add(norm(np.sin(2 * np.pi * (60 - 20 * t_) * t_) * np.exp(-t_ * 3)) + .2 * A.whoosh(1.1), m0 + goal - 1.0 - .4, .16)
    tr.add(band(noise(.5), 1500, 7000) * np.exp(-t_axis(.5) * 8), m0 + goal - .75, .10)   # net
    tr.add(roar(4.0), m0 + goal - .7, .22)
    # 22:30
    tr.add(splash(), at("night", 0.05), .10)
    for k in range(4):
        tr.add(A.blip(rng.uniform(3000, 4500), .12), at("night", .5 + k * .6), .03)
    tr.add(A.crickets(length("night")), at("night", 0), .015, .5)
    return tr


def main(out):
    mL, mR = lofi()
    s = sfx()
    L, R = mL * .4 + s.L, mR * .4 + s.R
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
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "fb_bed.wav"))
