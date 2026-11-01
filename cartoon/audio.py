#!/usr/bin/env python3
"""Synthesises the sound bed: soft tense march music, quiet ambience and light
cartoon SFX, all timed to the animation. Output: 48 kHz stereo WAV (no voice).

usage: python3 audio.py out.wav
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 45.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def noise(d):
    return rng.standard_normal(int(d * SR))


def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)


class Track:
    def __init__(self):
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, sig, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= N:
            return
        sig = sig[: N - i] * gain
        self.L[i:i + len(sig)] += sig * (1 - pan) ** .5
        self.R[i:i + len(sig)] += sig * (1 + pan) ** .5


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m else x


# ---------------------------------------------------------------- SFX
def whistle(d):
    t = t_axis(d)
    f = 2900 + 120 * np.sin(2 * np.pi * 38 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + .2 * band(noise(d), 2500, 4000)
    e = np.minimum(1, t / .02) * np.minimum(1, (d - t) / .04)
    return norm(s * e)


def boing(d=0.6, f0=180, f1=420):
    t = t_axis(d)
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 9)) + 30 * np.sin(2 * np.pi * 14 * t)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5))


def crash(d=0.9):
    t = t_axis(d)
    thud = np.sin(2 * np.pi * (70 - 30 * t) * t) * np.exp(-t * 12)
    clat = band(noise(d), 800, 7000) * np.exp(-t * 6) * .35
    for k in range(5):
        i = int((.05 + .1 * k) * SR)
        clat[i:i + 2400] += band(noise(.05), 2000, 6000) * np.exp(-np.arange(2400) / 300) * .5
    return norm(thud + clat)


def thud(d=0.18, f=90):
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 30) + .3 * band(noise(d), 100, 900) * np.exp(-t * 40))


def splat(d=0.5):
    t = t_axis(d)
    s = band(noise(d), 150, 1800) * np.exp(-t * 9)
    s += .6 * np.sin(2 * np.pi * (220 - 160 * t) * t) * np.exp(-t * 10)
    return norm(s)


def blip(f=880, d=0.25):
    t = t_axis(d)
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 14) + .3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 20))


def ding(d=1.2):
    t = t_axis(d)
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, a, dcy in
            ((1568, 1, 3), (3136, .4, 5), (2349, .3, 4)))
    return norm(s)


def whoosh(d=0.7):
    t = t_axis(d)
    s = band(noise(d), 300, 2500) * np.sin(np.pi * t / d) ** 2
    return norm(s)


def chirp_bird():
    d = rng.uniform(.06, .14)
    t = t_axis(d)
    f0 = rng.uniform(3000, 4500)
    f = f0 + rng.uniform(-1500, 1500) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)


def shout_far(d=0.6):
    """Unintelligible distant shout: buzzy source through two formants."""
    t = t_axis(d)
    f = 170 + 40 * np.sin(2 * np.pi * 2 * t)
    src = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + .3 * noise(d)
    s = band(src, 500, 900) + .6 * band(src, 1100, 1700)
    return norm(s * np.sin(np.pi * t / d) ** .6)


def cheer(d=1.8):
    t = t_axis(d)
    s = np.zeros(len(t))
    for _ in range(6):
        s += shout_far(d) * rng.uniform(.5, 1)
    s += .5 * band(noise(d), 400, 3000)
    return norm(s * np.minimum(1, t / .15) * np.minimum(1, (d - t) / .5))


def murmur(d):
    n = noise(d)
    s = band(n, 250, 1400)
    mod = np.interp(np.arange(len(s)), np.linspace(0, len(s), int(d * 6)), rng.uniform(.4, 1, int(d * 6)))
    return norm(s * mod)


def engine(d):
    t = t_axis(d)
    f = 42 + 4 * np.sin(2 * np.pi * .7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k for k in range(1, 9))
    s = band(s, 30, 600) + .2 * band(noise(d), 60, 300)
    return norm(s)


def snore(d, rate=0.32):
    t = t_axis(d)
    e = np.maximum(0, np.sin(2 * np.pi * rate * t)) ** 2
    src = band(noise(d), 80, 500) * (1 + .6 * np.sin(2 * np.pi * 28 * t))
    return norm(src * e)


def crickets(d):
    t = t_axis(d)
    gate = (np.sin(2 * np.pi * 26 * t) > .3) * (np.sin(2 * np.pi * .9 * t) > 0)
    return norm(np.sin(2 * np.pi * 4600 * t) * gate * .7)


def wind(d):
    s = band(noise(d), 80, 900)
    return norm(s * (0.6 + 0.4 * np.sin(2 * np.pi * .13 * t_axis(d))))


def rub(d):
    t = t_axis(d)
    return norm(band(noise(d), 1500, 6000) * np.abs(np.sin(2 * np.pi * 2.55 * t)) ** 3)


def room_tone(d):
    return norm(band(noise(d), 40, 400))


# ---------------------------------------------------------------- music
def pluck(f, d=0.5):
    t = t_axis(d)
    s = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .1 * np.sin(6 * np.pi * f * t)
    return s * np.minimum(1, t / .004) * np.exp(-t * 6)


def snare(d=0.12, soft=1.0):
    t = t_axis(d)
    return (band(noise(d), 1200, 7000) * .8 + .4 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 35) * soft


def kick(d=0.25):
    t = t_axis(d)
    return np.sin(2 * np.pi * (110 * np.exp(-t * 18) + 45) * t) * np.exp(-t * 14)


def pad(freqs, d):
    t = t_axis(d)
    s = np.zeros(len(t))
    for f in freqs:
        for det in (-.6, .6):
            ph = 2 * np.pi * (f + det) * t
            s += sum(np.sin(k * ph) / k for k in range(1, 6))
    s = band(s, 60, 1800)
    return norm(s)


def music():
    tr = Track()
    bpm = 100
    beat = 60 / bpm
    D2, A1, F2, C2, Bb1, E2 = 73.42, 55.0, 87.31, 65.41, 58.27, 82.41
    bass_line = [D2, A1, D2, A1, F2, C2, D2, A1, Bb1, F2, A1, E2]
    n_beats = int(DUR / beat)
    for b in range(n_beats):
        tb = b * beat
        if tb > 44.0:
            break
        intensity = 0.55 + 0.45 * min(1, tb / 30)       # slow build ...
        if 30 <= tb < 37:
            intensity = 1.25                              # ... strongest in scene 5
        if tb >= 37:
            intensity = 0.45                              # calm night
        if b % 2 == 0:
            tr.add(pluck(bass_line[(b // 2) % len(bass_line)]), tb, .5 * intensity)
        if tb < 37:
            tr.add(kick(), tb, (.35 if b % 2 == 0 else .15) * intensity)
            # march snare: beat + 8th + roll fragments
            tr.add(snare(soft=.6 if b % 2 else 1), tb, .16 * intensity, .2)
            tr.add(snare(soft=.5), tb + beat / 2, .09 * intensity, .2)
            if b % 8 == 7:
                for k in range(4):
                    tr.add(snare(soft=.5), tb + beat / 2 + k * beat / 8, .07 * intensity, .2)
    # tension pads
    tr.add(pad([146.8, 220.0], 8) * np.minimum(1, t_axis(8) / 3) * .10, 0)
    tr.add(pad([146.8, 174.6, 220.0], 7) * .14, 30)
    tr.add(pad([138.6, 207.7], 3.5) * np.linspace(.06, .2, int(3.5 * SR)), 33.5)
    tr.add(pad([146.8, 220.0, 293.7], 8) * np.minimum(1, t_axis(8) / 1) * np.linspace(.08, 0, int(8 * SR)), 37)
    # soft glockenspiel lullaby at night
    for k, f in enumerate((587.3, 440, 523.3, 440, 587.3, 659.3)):
        tr.add(pluck(f * 2, 1.2) * .5, 37.3 + k * 1.1, .10)
    return tr


# ---------------------------------------------------------------- ambience + sfx
def sfx():
    tr = Track()
    # scene 1 -- 05:00
    tr.add(room_tone(8), 0, .05)
    tr.add(whoosh(.5), .65, .10)
    tr.add(whistle(.55), 1.0, .22, .1)
    tr.add(whistle(.7), 1.75, .22, .1)
    for k in range(3):
        tr.add(thud(), 2.45 + k * .05, .25, (-.5, .3, .6)[k])
    tr.add(shout_far(.8), 2.65, .10, .1)
    tr.add(whoosh(.8), 2.8, .18, -.3)
    tr.add(crash(), 3.6, .35, -.4)
    tr.add(blip(1320, .3), 4.6, .05)
    tr.add(blip(1560, .3), 5.0, .05)
    tr.add(boing(), 5.8, .25, -.2)
    tr.add(blip(1760, .4), 6.1, .08)
    # scene 2 -- 06:00
    tr.add(wind(7), 8, .05)
    for _ in range(14):
        tr.add(chirp_bird(), rng.uniform(8, 15), .05, rng.uniform(-.8, .8))
    tr.add(shout_far(.7), 9.45, .09, .4)
    for k in range(int(3.5 * 6.4)):
        tr.add(thud(.12, 120), 11.5 + k / 6.4, .10, rng.uniform(-.3, .3))
    for k in range(int(3.5 * 4.8)):
        tr.add(band(noise(.25), 300, 1500) * env(int(.25 * SR), .05, .08), 11.5 + k / 4.8, .04, -.4)
    # scene 3 -- 10:00
    tr.add(wind(8), 15, .04)
    for _ in range(10):
        tr.add(chirp_bird(), rng.uniform(15, 23), .04, rng.uniform(-.8, .8))
    for k in range(4):
        tr.add(shout_far(.5), 15.4 + k * .8, .08, -.6)
    for k in range(int(3.4 * 3.5)):
        tr.add(band(noise(.2), 400, 3000) * env(int(.2 * SR), .03, .06), 15 + k / 3.5, .05)
    for k in range(3):
        tr.add(thud(.12, 150), 18.6 + k * .25, .08)
    tr.add(whoosh(.4), 19.3, .1)
    tr.add(boing(.7, 140, 360), 19.8, .26)
    for k in range(4):
        tr.add(thud(.12, 150), 20.4 + k * .22, .08)
    tr.add(cheer(1.7), 21.3, .14)
    tr.add(blip(1760, .5), 21.3, .07)
    # scene 4 -- 12:30
    tr.add(murmur(7), 23, .06)
    for _ in range(18):
        tr.add(blip(rng.uniform(2500, 4200), .08), rng.uniform(23, 30), .025, rng.uniform(-.7, .7))
    tr.add(whoosh(.4), 24.0, .06)
    tr.add(splat(), 24.6, .30)
    tr.add(blip(660, .25), 25.1, .08)
    tr.add(blip(520, .3), 27.3, .06)
    for k in range(10):
        tr.add(band(noise(.09), 500, 2500) * env(int(.09 * SR), .005, .03), 28.45 + k / 3, .10)
    # scene 5 -- 15:00
    tr.add(engine(3.6) * np.minimum(1, t_axis(3.6) / .3) * np.minimum(1, (3.6 - t_axis(3.6)) / .5), 30, .14)
    for k in range(6):
        tr.add(thud(.2, 70), 30.2 + k * .6, .12)
    tr.add(wind(3.5), 33.5, .07)
    for k in range(5):
        tr.add(band(noise(.3), 1000, 5000) * env(int(.3 * SR), .05, .1), 33.8 + k * .55, .04, rng.uniform(-.6, .6))
    tr.add(whoosh(.3), 35.4, .06)
    tr.add(blip(1200, .2), 36.2, .08)
    # scene 6 -- 21:00
    tr.add(crickets(8), 37, .03, .5)
    tr.add(snore(8), 37, .07, .5)
    tr.add(snore(8, .27), 37.8, .05, -.4)
    tr.add(rub(4), 37, .06, -.3)
    tr.add(blip(2400, .3), 38.6, .04)
    tr.add(blip(2400, .3), 39.9, .04)
    tr.add(band(noise(.4), 200, 1500) * env(int(.4 * SR), .1, .2), 41.0, .05)
    tr.add(ding(), 43.0, .12)
    tr.add(thud(.05, 2000), 44.5, .06)
    return tr


def main(out):
    m, s = music(), sfx()
    fade = np.ones(N)
    fade[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR))
    L = (m.L + s.L) * fade
    R = (m.R + s.R) * fade
    peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
    g = 0.5 / peak                     # bed peaks at -6 dBFS: leaves room for the voice
    data = (np.stack([L, R], 1) * g * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build/cartoon_bed.wav")
