#!/usr/bin/env python3
"""Sound bed for the K-pop trainee video: original K-pop-style music that is
full and bright on stage and slow/quiet/muffled behind the scenes, plus quiet
SFX (sneaker squeaks, metronome, camera clicks, phone buzz ...). No voice.

usage: python3 kaudio.py out.wav
"""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon"))
import audio as A  # noqa: E402  (synth helpers from the soldier video)

DUR = 52.0
A.DUR = DUR
A.N = int(DUR * A.SR)
SR, N = A.SR, A.N
rng = np.random.default_rng(21)
t_axis, band, noise, norm, Track = A.t_axis, A.band, A.noise, A.norm, A.Track

BPM = 112
BEAT = 60 / BPM
# I-V-vi-IV in A major (A, E, F#m, D) - bright; same roots as soft pads behind the scenes
CHORDS = [(220.0, 277.2, 329.6), (164.8, 207.7, 246.9), (185.0, 220.0, 277.2), (146.8, 185.0, 220.0)]
ROOTS = [55.0, 41.2, 46.25, 36.7]


def saw(f, d, n_h=8):
    t = t_axis(d)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, n_h + 1))


def stab(freqs, d=0.22):
    t = t_axis(d)
    s = sum(saw(f, d, 6) + saw(f * 1.006, d, 6) for f in freqs)
    return norm(band(s, 150, 5000)) * np.minimum(1, t / .005) * np.exp(-t * 9)


def hat(d=0.05):
    t = t_axis(d)
    return band(noise(d), 7000, 15000) * np.exp(-t * 90)


def clap(d=0.18):
    t = t_axis(d)
    s = band(noise(d), 900, 5000)
    e = np.exp(-t * 25) + .6 * np.exp(-np.maximum(0, t - .012) * 40) * (t > .012)
    return norm(s * e)


def sub_bass(f, d):
    t = t_axis(d)
    return (np.sin(2 * np.pi * f * 2 * t) + .3 * np.sin(4 * np.pi * f * 2 * t)) * np.minimum(1, t / .01) * np.exp(-t * 4)


def piano(f, d=1.6):
    t = t_axis(d)
    s = np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + .15 * np.sin(6 * np.pi * f * t) * np.exp(-t * 5)
    return s * np.minimum(1, t / .003) * np.exp(-t * 2.2)


def bright_stem():
    tr = Track()
    bars = int(DUR / (BEAT * 4)) + 1
    for b in range(bars * 4):
        tb = b * BEAT
        ch = CHORDS[(b // 8) % 4]
        root = ROOTS[(b // 8) % 4]
        tr.add(A.kick(), tb, .55)
        if b % 2 == 1:
            tr.add(clap(), tb, .30)
        for k in range(2):
            tr.add(hat(), tb + k * BEAT / 2, .10 if k else .06, .3)
        tr.add(sub_bass(root, BEAT * .9), tb + BEAT / 2, .35)
        tr.add(stab(ch), tb + BEAT / 2, .12, -.2)
        for k in range(4):  # sparkly 16th arp
            f = ch[(b * 4 + k) % 3] * 4
            tr.add(A.pluck(f, .25), tb + k * BEAT / 4, .045, .4 * ((k % 2) * 2 - 1))
    return tr


def dark_stem():
    tr = Track()
    seg = BEAT * 8
    for i in range(int(DUR / seg) + 1):
        ch = CHORDS[i % 4]
        tr.add(A.pad([f / 2 for f in ch], seg + .5) * np.minimum(1, t_axis(seg + .5) / 1.2), i * seg, .16)
        for k, f in enumerate((ch[0], ch[2], ch[1], ch[2] * 2)):
            tr.add(piano(f * 2), i * seg + k * BEAT * 2, .10, .2 * (k % 2 * 2 - 1))
        tr.add(A.kick(), i * seg, .10)
        tr.add(A.kick(), i * seg + BEAT * 4, .08)
    return tr


def curve(points):
    """Piecewise-linear gain curve over the whole track from (time, gain) points."""
    ts, gs = zip(*points)
    return np.interp(np.arange(N) / SR, ts, gs)


def music():
    br, dk = bright_stem(), dark_stem()
    muff = [band(br.L, 30, 900), band(br.R, 30, 900)]      # bright beat heard "through a wall"
    g_bright = curve([(0, 1), (3.9, 1), (4.2, 0), (32.4, 0), (32.6, 1), (35.3, 1), (35.9, 0), (52, 0)])
    g_muff = curve([(0, 0), (3.9, 0), (4.2, .55), (25.6, .55), (26.2, 0), (52, 0)])
    g_dark = curve([(0, 0), (3.9, 0), (4.4, .45), (25.9, .55), (32.4, .6), (32.6, 0), (35.4, 0), (36.0, .55),
                    (48.7, .5), (50.5, .65), (52, .65)])
    g_arp = curve([(0, 0), (48.7, 0), (50.5, .25), (52, .25)])  # a little shine returns in the outro
    L = br.L * (g_bright + g_arp) + muff[0] * g_muff + dk.L * g_dark
    R = br.R * (g_bright + g_arp) + muff[1] * g_muff + dk.R * g_dark
    return L, R


# ---------------------------------------------------------------- SFX
def squeak():
    d = rng.uniform(.06, .12)
    t = t_axis(d)
    f = rng.uniform(1800, 2600) + rng.uniform(-600, 900) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * (1 + .3 * band(noise(d), 1000, 4000))


def click(d=0.03, f=2200):
    t = t_axis(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 300)


def shutter():
    s = np.zeros(int(.12 * SR))
    for at in (0, .06):
        i = int(at * SR)
        n = int(.03 * SR)
        s[i:i + n] += band(noise(.03), 1500, 9000) * np.exp(-np.arange(n) / 200)
    return norm(s)


def buzz(d=0.7):
    t = t_axis(d)
    gate = (np.sin(2 * np.pi * 3 * t) > -.2)
    return norm(np.sign(np.sin(2 * np.pi * 160 * t)) * gate * .6 + band(noise(d), 100, 400) * gate * .3)


def buzzer(d=0.6):
    t = t_axis(d)
    return norm(band(np.sign(np.sin(2 * np.pi * 110 * t)), 80, 2000) * np.minimum(1, (d - t) / .05))


def steps(tr, a, b, rate=2.2, gain=.08, f=140):
    k = 0
    while a + k / rate < b:
        tr.add(A.thud(.1, f), a + k / rate, gain, rng.uniform(-.3, .3))
        k += 1


def sfx():
    tr = Track()
    # intro
    for at in (0.35, 1.0, 2.5):
        tr.add(A.paper_thump(), at, .32)
        tr.add(A.whoosh(.25), at - .2, .06)
    tr.add(A.sparkle(), 2.55, .07, .2)
    tr.add(A.boing(.35, 320, 760), 2.9, .14)
    tr.add(A.ding(), 3.2, .07)
    # 06:00 dorm
    tr.add(A.room_tone(7.2), 4.0, .04)
    tr.add(A.snore(7.2, .3), 4.0, .04, .4)
    steps(tr, 4.0, 5.0, 2.5, .07)
    for at in (5.5, 5.95, 6.4, 6.85, 7.3, 9.3):
        tr.add(A.thud(.08, 600), at, .10, .3)
        tr.add(click(.02, 3000), at, .05, .3)
    # 07:00 weighing
    tr.add(A.room_tone(6.9), 11.2, .035)
    tr.add(A.blip(1800, .15), 11.6, .06)
    tr.add(A.blip(900, .25), 12.4, .07)
    tr.add(A.blip(900, .25), 12.65, .07)
    for k in range(10):
        tr.add(band(noise(.12), 2000, 7000) * A.env(int(.12 * SR), .01, .04), 12.8 + k * .17, .035, .5)
    tr.add(A.blip(520, .3), 16.1, .05)
    # 09:00-15:00 dance studio
    k = 0
    while 18.1 + k * BEAT < 25.9:
        tr.add(click(.03, 2400 if k % 4 == 0 else 1800), 18.1 + k * BEAT, .07, .5)
        k += 1
    for _ in range(26):
        tr.add(squeak(), rng.uniform(18.1, 25.8), .05, rng.uniform(-.6, .6))
    tr.add(A.thud(.25, 80), 22.7, .18, .4)
    # 16:00 evaluation
    tr.add(A.room_tone(6.7), 25.9, .04)
    for k in range(3):
        tr.add(A.whoosh(.2), 28.3 + k * .08, .06, .3)
    tr.add(buzzer(), 28.8, .06, .3)
    tr.add(band(noise(.5), 3000, 8000) * np.linspace(1, .3, int(.5 * SR)), 29.6, .03, -.5)
    steps(tr, 29.5, 32.2, 2.0, .04, 160)
    tr.add(A.thud(.15, 110), 32.3, .08, -.6)
    # 19:00 fan event -> grey
    tr.add(A.cheer(2.8), 32.6, .07)
    for _ in range(12):
        tr.add(shutter(), rng.uniform(32.6, 35.2), .07, rng.uniform(-.7, .7))
    t = t_axis(1.0)
    tr.add(np.sin(2 * np.pi * np.cumsum(600 * np.exp(-t * 2.5)) / SR) * np.exp(-t * 2), 35.3, .05)   # "colour drains"
    tr.add(A.whoosh(1.2), 36.0, .09, -.2)
    tr.add(band(noise(.6), 800, 5000) * np.abs(np.sin(2 * np.pi * 9 * t_axis(.6))), 36.4, .03)
    steps(tr, 38.8, 41.4, 2.2, .06)
    # 23:00 alone
    tr.add(buzz(), 42.6, .05, .4)
    for k in range(4):
        tr.add(band(noise(.25), 1500, 6000) * A.env(int(.25 * SR), .02, .08), 42.9 + k * .5, .035, .4)
    for _ in range(9):
        tr.add(squeak(), rng.uniform(41.7, 44.5), .04, rng.uniform(-.4, .4))
    tr.add(band(noise(.6), 200, 1500) * A.env(int(.6 * SR), .1, .2), 44.6, .04)
    for _ in range(7):
        tr.add(squeak(), rng.uniform(46.5, 48.6), .04, rng.uniform(-.4, .4))
    # outro
    tr.add(A.ding(), 49.0, .05)
    tr.add(A.sparkle(1.5), 49.4, .04)
    return tr


def main(out):
    mL, mR = music()
    s = sfx()
    L, R = mL * .55 + s.L, mR * .55 + s.R
    fade = np.ones(N)
    fade[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR))
    L, R = L * fade, R * fade
    g = 0.5 / max(np.max(np.abs(L)), np.max(np.abs(R)))
    data = (np.stack([L, R], 1) * g * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build/kpop_bed.wav")
