"""Synthesise music + cartoon sound effects and mix them with the narration."""
import json, os, wave
import numpy as np
from narration import BUILD, SR

TL = json.load(open(os.path.join(BUILD, "timeline.json")))
SC = {s["name"]: s for s in TL["scenes"]}
rng = np.random.default_rng(3)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if r:
        e *= np.exp(-np.arange(n) / (r * SR))
    return e


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


# ------------------------------------------------------------------ sfx
def ring(d):
    t = tt(d)
    bell = np.sign(np.sin(2 * np.pi * 1850 * t)) * 0.3 + np.sin(2 * np.pi * 2650 * t) * 0.3
    return bell * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t))) * 0.5


def boom():
    n = rng.normal(0, 1, int(1.1 * SR))
    low = lowpass(n, 40) * 6 * env(len(n), 0.002, 0.25)
    crack = n * env(len(n), 0.001, 0.05)
    t = tt(1.1)
    thump = np.sin(2 * np.pi * (90 - 50 * t) * t) * env(len(t), 0.002, 0.3)
    return (low + crack * 0.6 + thump) * 0.8


def sweep(f0, f1, d, wobble=0, amp=0.5, decay=None):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d)
    if wobble:
        f = f * (1 + 0.15 * np.sin(2 * np.pi * wobble * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(len(t), 0.005, decay or d * 0.6) * amp


def boing():
    return sweep(180, 420, 0.55, wobble=14, amp=0.55)


def whoop():
    return sweep(300, 1200, 0.35, amp=0.35)


def splash():
    n = rng.normal(0, 1, int(0.7 * SR))
    hi = n - lowpass(n, 6)
    bub = sum(sweep(f, f * 1.8, 0.08, amp=0.2) for f in (500, 700))
    out = hi * env(len(n), 0.003, 0.18) * 0.7
    out[: len(bub)] += bub
    return out


def freeze():
    out = np.zeros(int(1.0 * SR))
    for i, f in enumerate((2093, 2637, 3136, 4186)):
        s = sweep(f, f, 0.6, amp=0.18, decay=0.25)
        out[int(i * 0.07 * SR): int(i * 0.07 * SR) + len(s)] += s
    return out


def squirt():
    n = rng.normal(0, 1, int(0.18 * SR))
    return lowpass(n, 4) * env(len(n), 0.01, 0.06) * 0.5 + sweep(900, 300, 0.18, amp=0.25)


def munch():
    n = rng.normal(0, 1, int(0.16 * SR))
    return lowpass(n, 12) * env(len(n), 0.002, 0.04) * 1.6


def thud():
    t = tt(0.6)
    return np.sin(2 * np.pi * (75 - 30 * t) * t) * env(len(t), 0.002, 0.15) * 0.9


def crash():
    n = rng.normal(0, 1, int(0.5 * SR))
    return (lowpass(n, 20) * 3 + n * 0.3) * env(len(n), 0.001, 0.12) * 0.6


def cricket():
    out = np.zeros(int(0.5 * SR))
    for k in range(3):
        s = sweep(4300, 4300, 0.06, amp=0.12, decay=0.03) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 70 * tt(0.06))))
        out[int(k * 0.09 * SR): int(k * 0.09 * SR) + len(s)] += s
    return out


def chime():
    out = np.zeros(int(0.7 * SR))
    for i, f in enumerate((1568, 2093, 2637)):
        s = sweep(f, f, 0.5, amp=0.12, decay=0.15)
        out[int(i * 0.05 * SR): int(i * 0.05 * SR) + len(s)] += s
    return out


def wind(d):
    n = rng.normal(0, 1, int(d * SR))
    w = lowpass(n, 30) - lowpass(n, 120)
    t = tt(d)
    return w * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * 1.6 * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3)


def click():
    n = rng.normal(0, 1, int(0.03 * SR))
    return n * env(len(n), 0.0005, 0.004) * 0.8


def swish():
    n = rng.normal(0, 1, int(0.25 * SR))
    w = n - lowpass(n, 8)
    return w * np.sin(np.linspace(0, np.pi, len(n))) * 0.12


# ------------------------------------------------------------------ music
def pluck(freq, d, decay=0.996):
    n = int(d * SR)
    p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def marimba(freq, d):
    t = tt(d)
    return (np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 30)) * np.exp(-t * 7)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def music(total):
    bpm = 116
    beat = 60 / bpm
    out = np.zeros(int((total + 2) * SR))
    prog = [(60, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7]), (55, [0, 4, 7])]  # C Am F G
    melody = [76, 79, 81, 79, 76, 74, 72, 74, 76, 72, 69, 72, 74, 79, 77, 74]
    cache = {}
    bar = 0
    t = 0.0
    while t < total + 1:
        root, ch = prog[bar % 4]
        for b in range(4):
            tb = t + b * beat
            i = int(tb * SR)
            # bass
            key = ("b", root, b % 2)
            if key not in cache:
                cache[key] = pluck(note(root - 24 + (7 if b % 2 else 0)), beat * 0.9, 0.994) * 0.5
            s = cache[key]; out[i:i + len(s)] += s[: len(out) - i]
            # ukulele-ish offbeat chord strum
            for k, iv in enumerate(ch):
                kk = ("c", root + iv)
                if kk not in cache:
                    cache[kk] = pluck(note(root + iv + 12), beat * 0.6, 0.99) * 0.22
                j = int((tb + beat / 2 + k * 0.012) * SR)
                s = cache[kk]; out[j:j + len(s)] += s[: max(0, len(out) - j)]
            # melody (marimba)
            m = melody[(bar * 4 + b) % len(melody)]
            km = ("m", m)
            if km not in cache:
                cache[km] = marimba(note(m), beat * 0.9) * 0.18
            s = cache[km]; out[i:i + len(s)] += s[: len(out) - i]
        t += 4 * beat
        bar += 1
    return out[: int(total * SR)]


def main():
    total = TL["total"]
    n = int(total * SR)
    narr = np.zeros(n)
    _nv = np.load(os.path.join(BUILD, "narration.npy"))[:n]
    narr[: len(_nv)] = _nv
    fx = np.zeros(n + SR * 2)

    def add(t, s, g=1.0):
        i = int(t * SR)
        fx[i:i + len(s)] += s[: len(fx) - i] * g

    a = SC["alarm"]["start"]
    add(a + 0.25, ring(0.95), 0.8)
    add(a + 1.2, boom(), 0.9)
    add(a + 1.3, whoop())
    add(a + 1.85, boing())
    w = SC["water"]["start"]
    add(w + 0.6, splash(), 0.9)
    add(w + 0.95, freeze())
    for k in range(4):
        add(w + SC["water"]["events"]["scream_end"] + 0.1 + k * 0.33, sweep(1400, 2200, 0.05, amp=0.15))
    c = SC["cream"]["start"]
    for i in range(12):
        add(c + 0.5 + i * 2.9 / 12, squirt(), 0.8)
        add(c + 0.62 + i * 2.9 / 12, squirt(), 0.5)
    add(c + 3.45, sweep(400, 900, 0.12, amp=0.3))
    e = SC["eggs"]
    t0, t1 = 0.55, e["dur"] - 0.5
    for k in range(14):
        add(e["start"] + t0 + (k + 0.6) * (t1 - t0) / 14, munch(), 0.9)
    add(e["start"] + t1 + 0.05, sweep(300, 200, 0.25, amp=0.3))  # gulp
    p = SC["pushup"]
    ps = p["start"]
    add(ps + 1.4, sweep(300, 220, 0.3, amp=0.2))
    add(ps + 1.85, sweep(220, 330, 0.3, amp=0.2))
    add(ps + 2.5, crash(), 0.9)
    add(ps + 2.55, thud())
    add(ps + 2.6, boing(), 0.7)
    add(ps + 3.3, cricket())
    po = SC["pose"]
    add(po["start"] + po["segments"][0]["start"], swish() * 4)
    add(po["start"] + po["segments"][0]["start"] + 0.2, wind(po["dur"] - po["segments"][0]["start"] - 0.2), 0.35)
    tsp = po["segments"][1]["start"] - 0.2
    k = 0
    while tsp + k * 0.42 < po["dur"] - 0.3:
        add(po["start"] + tsp + k * 0.42, chime())
        k += 1
    ni = SC["night"]
    t_off = ni["start"] + ni["segments"][2]["post_end"] + 0.1
    add(t_off, click() * 1.5)
    for s in TL["scenes"][1:]:
        add(s["start"] - 0.05, swish())

    mus = music(total)
    # ducking: music sits under the narrator, drops out for the awkward silence and at lights-out
    gain = np.full(n, 0.55)
    for s in TL["scenes"]:
        for g in s["segments"]:
            i0, i1 = int((s["start"] + g["start"] - 0.1) * SR), int((s["start"] + g["end"] + 0.1) * SR)
            gain[i0:i1] = 0.3
    gain[int((ps + 2.55) * SR): int((ps + p["segments"][1]["end"]) * SR)] = 0.0
    gain[int(t_off * SR):] = 0.0
    gain = lowpass(gain, int(0.08 * SR))
    gain[int(t_off * SR):] = 0.0
    fade = np.minimum(1, np.arange(n) / (0.5 * SR))
    mix = narr * 1.0 + fx[:n] * 0.55 + mus * gain * fade * 0.5
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix *= 0.95 / np.abs(mix).max()
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(os.path.join(BUILD, "audio.wav"), "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print("audio ok", len(pcm) / SR)


if __name__ == "__main__":
    main()
