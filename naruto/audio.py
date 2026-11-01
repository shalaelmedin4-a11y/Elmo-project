"""Quiet ninja-style background music (shakuhachi, koto, taiko – original melody),
subtle sound effects and the voices -> build/audio.wav"""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 44100
TOTAL = 58.0
rng = np.random.default_rng(21)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- instruments
def shakuhachi(freq, d, bend=0.0):
    """Breathy bamboo flute: sine + soft 2nd harmonic, slow vibrato, air noise, scoop into the note."""
    t = tt(d)
    f = freq * (1 + bend * np.exp(-t * 9)) * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    air = rng.normal(0, 1, len(t))
    air = (lowpass(air, 3) - lowpass(air, 30)) * 0.35
    env = np.minimum(1, t / 0.18) * np.minimum(1, (d - t) / 0.35)
    env *= 1 + 0.15 * np.sin(2 * np.pi * 0.7 * t)
    return (tone + air) * env


def koto(freq, d):
    n = int(d * SR)
    p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p) * np.hanning(p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.997 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * 0.8


def taiko(big=True):
    t = tt(0.9 if big else 0.4)
    f = (62 if big else 110) + 40 * np.exp(-t * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * decay(len(t), 0.28 if big else 0.1)
    hit = lowpass(rng.normal(0, 1, len(t)), 12) * decay(len(t), 0.02)
    return body + hit * 0.6


def music(total):
    bpm = 70
    b = 60 / bpm
    out = np.zeros(int((total + 4) * SR))

    def put(t, s, g=1.0):
        i = int(t * SR)
        if i >= len(out):
            return
        out[i:i + len(s)] += s[: len(out) - i] * g

    # D "in" scale: D Eb G A Bb
    scale = [62, 63, 67, 69, 70, 74, 75, 79]
    koto_pat = [0, 2, 3, 2, 5, 3, 2, 1]
    flute = [  # (beat, scale index, beats, bend)
        (0, 5, 3, -0.04), (3, 4, 1, 0), (4, 3, 2, 0), (6, 2, 2, -0.03), (8, 3, 3, 0), (11, 4, 1, 0), (12, 5, 4, -0.05),
        (16, 6, 2, 0), (18, 5, 2, 0), (20, 4, 3, -0.03), (23, 3, 1, 0), (24, 2, 4, 0), (28, 1, 2, 0), (30, 0, 2, -0.04)]
    cache = {}
    t = 0.0
    cycle = 0
    while t < total + 1:
        for beat in range(32):          # 8 bars of 4/4
            tb = t + beat * b
            if beat % 4 == 0:
                put(tb, taiko(True), 0.55)
            if beat % 8 == 6:
                put(tb + b / 2, taiko(False), 0.3)
            for half in (0, 1):
                k = koto_pat[(beat * 2 + half) % 8]
                if (beat * 2 + half) % 3 == 2:
                    continue
                key = ("k", k)
                if key not in cache:
                    cache[key] = koto(note(scale[k] - 12), b * 1.6)
                put(tb + half * b / 2, cache[key], 0.35)
        for beat, idx, beats, bend in flute:
            if cycle == 0 and beat < 4:   # flute enters after the intro
                continue
            put(t + beat * b, shakuhachi(note(scale[idx]), beats * b * 0.95, bend), 0.22)
        t += 32 * b
        cycle += 1
    out = out[: int(total * SR)]
    return out / np.abs(out).max()


# ---------------------------------------------------------------- sfx
def noise(d):
    return rng.normal(0, 1, int(d * SR))


def whoosh(d=0.35):
    x = noise(d)
    x = lowpass(x, 4) - lowpass(x, 40)
    return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * 1.4


def splash():
    x = noise(0.6)
    return (x - lowpass(x, 5)) * decay(len(x), 0.15) * 0.6


def ring(d):
    t = tt(d)
    return np.sin(2 * np.pi * 1900 * t) * (np.sin(2 * np.pi * 16 * t) > 0) * 0.15


def thud(f=90, tau=0.08):
    t = tt(0.3)
    return np.sin(2 * np.pi * f * t) * decay(len(t), tau) + lowpass(noise(0.3), 6) * decay(len(t), 0.02) * 0.6


def thunk():
    t = tt(0.25)
    return (np.sin(2 * np.pi * 320 * t) * decay(len(t), 0.03) + thud(140, 0.05)[: len(t)]) * 0.8


def poof():
    x = noise(0.7)
    return lowpass(x, 25) * np.minimum(1, np.arange(len(x)) / (0.02 * SR)) * decay(len(x), 0.18) * 2.2


def crash():
    x = noise(0.5)
    return (lowpass(x, 10) * 2 + x * 0.3) * decay(len(x), 0.1) * 0.7


def hiss(d=0.6):
    x = noise(d)
    return (x - lowpass(x, 3)) * np.sin(np.linspace(0, np.pi, len(x))) * 0.5


def meow():
    t = tt(0.55)
    f = 520 + 380 * np.sin(np.pi * t / 0.55) ** 1.5
    ph = 2 * np.pi * np.cumsum(f) / SR
    v = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)
    return v * np.sin(np.pi * t / 0.55) ** 0.6 * 0.3


def ding(f=1760):
    t = tt(1.0)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 5) * 0.3


def click():
    x = noise(0.03)
    return x * decay(len(x), 0.004) * 0.6


def main():
    n = int(TOTAL * SR)
    voices = json.load(open(os.path.join(BUILD, "voices.json")))
    vo = np.zeros(n + SR * 3)
    for lid, v in voices.items():
        a = np.load(os.path.join(BUILD, "voice", f"{lid}.npy"))
        if v["speaker"] == "naruto_q":
            a = a * 0.8           # spoken softly
        i = int(v["start"] * SR)
        vo[i:i + len(a)] += a
    vo = vo[:n]

    fx = np.zeros(n + SR * 3)

    def add(t, s, g=1.0):
        i = int(t * SR)
        fx[i:i + len(s)] += s[: len(fx) - i] * g

    add(0.1, whoosh(0.3), 0.5); add(2.7, whoosh(0.3), 0.5)
    add(4.7, ring(1.15), 0.6); add(5.85, thud(), 0.8)
    add(10.75, splash()); add(11.6, whoosh(0.5), 0.6); add(12.7, whoosh(0.3), 0.4); add(13.9, whoosh(0.25), 0.5)
    add(15.4, ding(), 0.6)
    add(19.75, whoosh(0.45), 0.9)
    add(36.3, whoosh(0.3), 0.8); add(36.7, thunk())
    add(37.2, whoosh(1.9), 0.6)
    add(39.15, poof(), 0.8)
    add(44.3, meow(), 0.6); add(46.4, crash(), 0.8)
    add(47.9, hiss(0.7), 0.8); add(48.75, whoosh(0.15), 0.8); add(49.0, meow(), 0.5)
    add(56.45, click(), 1.2)
    fx = fx[:n]

    # ducking: music sits low and dips further under speech
    env = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = lowpass(np.where(env > 0.01, 0.07, 0.16), int(0.15 * SR))
    fade = np.minimum(1, np.arange(n) / (0.6 * SR))
    fade = np.minimum(fade, np.clip((57.4 * SR - np.arange(n)) / (1.4 * SR), 0, 1))   # fades out with the lights
    mus = music(TOTAL) * duck * fade
    fxd = lowpass(np.where(env > 0.01, 0.55, 1.0), int(0.05 * SR))
    mix = vo * 0.95 + mus + fx * fxd * 0.45
    mix *= 0.97 / np.abs(mix).max()
    with wave.open(os.path.join(BUILD, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    rms = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    on = env > 0.01
    print(f"voice {rms(vo[on]):.1f} dB | music under speech {rms(mus[on]):.1f} dB | music alone {rms(mus[~on]):.1f} dB")


if __name__ == "__main__":
    main()
