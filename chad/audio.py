"""Lo-fi hip-hop beat + subtle sound effects + voices -> build/audio.wav"""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 44100
TOTAL = 50.0
rng = np.random.default_rng(11)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


# ---------------------------------------------------------------- drums
def kick():
    t = tt(0.45)
    f = 45 + 85 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * decay(len(t), 0.16)


def snare():
    n = int(0.25 * SR)
    noise = rng.normal(0, 1, n)
    noise = noise - lowpass(noise, 4)
    tone = np.sin(2 * np.pi * 185 * tt(0.25)) * decay(n, 0.05)
    return (noise * decay(n, 0.07) * 0.5 + tone * 0.6) * 0.8


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    x = rng.normal(0, 1, n)
    x = x - lowpass(x, 3)
    return x * decay(n, 0.06 if open_ else 0.012) * 0.25


def keys(freqs, d):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6) for f in freqs)
    return s * np.exp(-t * 1.6) * np.minimum(1, t / 0.01) / len(freqs)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def beat(total):
    bpm = 88
    b = 60 / bpm
    out = np.zeros(int((total + 3) * SR))

    def put(t, s, g=1.0):
        i = int(t * SR)
        out[i:i + len(s)] += s[: len(out) - i] * g

    K, S = kick(), snare()
    chords = [[57, 60, 64, 67], [50, 57, 60, 65], [55, 59, 62, 65], [52, 55, 59, 64]]   # Am7 Dm9 G7 Em7
    bar, t = 0, 0.0
    while t < total + 1:
        for step in range(8):                       # 8th notes with a lazy swing
            st = t + step * b / 2 + (0.035 if step % 2 else 0)
            put(st, hat(step == 7), 0.9 if step % 2 == 0 else 0.6)
        put(t, K); put(t + 2.5 * b, K, 0.8); put(t + 3.25 * b, K, 0.5) if bar % 2 else None
        put(t + b, S); put(t + 3 * b, S)
        ch = chords[bar % 4]
        put(t, keys([note(m) for m in ch], 4 * b) * 0.5)
        put(t, np.sin(2 * np.pi * note(ch[0] - 24) * tt(2 * b)) * decay(int(2 * b * SR), 0.6) * 0.6)
        put(t + 2 * b, np.sin(2 * np.pi * note(ch[0] - 24) * tt(2 * b)) * decay(int(2 * b * SR), 0.6) * 0.5)
        t += 4 * b
        bar += 1
    out = out[: int(total * SR)]
    return out / np.abs(out).max()


# ---------------------------------------------------------------- sfx
def whoosh(d=0.35, up=True):
    n = int(d * SR)
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    for i in range(0, n, 512):          # sweeping band-pass via moving average width
        f = i / n if up else 1 - i / n
        k = int(30 - 26 * f)
        seg = x[i:i + 512 + 64]
        out[i:i + 512] = (lowpass(seg, max(2, k // 3)) - lowpass(seg, k))[:len(out[i:i + 512])]
    return out * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * 1.2


def ding(f=1760):
    t = tt(1.2)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 4) * 0.35


def clap():
    n = int(0.2 * SR)
    x = rng.normal(0, 1, n)
    x = x - lowpass(x, 6)
    env = np.zeros(n)
    for k, off in enumerate((0, 0.008, 0.017)):
        i = int(off * SR)
        env[i:] += decay(n - i, 0.03 if k == 2 else 0.006)
    return x * env * 0.6


def applause(d):
    out = np.zeros(int(d * SR))
    for _ in range(int(d * 22)):
        i = rng.integers(0, len(out) - SR // 4)
        c = clap() * rng.uniform(0.15, 0.4)
        out[i:i + len(c)] += c
    fade = np.minimum(1, np.minimum(np.arange(len(out)) / (0.3 * SR), (len(out) - np.arange(len(out))) / (0.6 * SR)))
    return out * fade


def ring(d):
    t = tt(d)
    s = (np.sin(2 * np.pi * 2300 * t) + np.sin(2 * np.pi * 3100 * t)) * (np.sin(2 * np.pi * 18 * t) > 0)
    return s * 0.12


def click():
    n = int(0.03 * SR)
    return rng.normal(0, 1, n) * decay(n, 0.004) * 0.5


def pop():
    t = tt(0.12)
    return np.sin(2 * np.pi * (500 - 2500 * t) * t) * decay(len(t), 0.03) * 0.5


def main():
    n = int(TOTAL * SR)
    voices = json.load(open(os.path.join(BUILD, "voices.json")))
    vo = np.zeros(n + SR * 3)
    for lid, v in voices.items():
        a = np.load(os.path.join(BUILD, "voice", f"{lid}.npy"))
        i = int(v["start"] * SR)
        vo[i:i + len(a)] += a
    vo = vo[:n]

    fx = np.zeros(n + SR * 3)

    def add(t, s, g=1.0):
        i = int(t * SR)
        fx[i:i + len(s)] += s[: len(fx) - i] * g

    for t in (0.0, 1.0, 2.5):
        add(t, whoosh(0.25), 0.5); add(t + 0.05, pop(), 0.6)
    add(3.0, ding(2093), 0.6)
    add(4.15, ring(1.6), 0.5)
    add(5.75, click())
    add(10.2, ding(), 0.8)
    for t in (14.0, 14.8, 15.6, 16.4, 17.2, 18.0):
        add(t - 0.08, whoosh(0.3), 0.6)
    add(21.35, whoosh(0.35, up=False), 0.4)
    add(27.5, clap(), 1.6)
    add(32.3, applause(2.4), 0.8)
    add(35.0, whoosh(0.5, up=False), 0.4)
    add(43.0, applause(1.6), 0.35)
    add(45.15, whoosh(0.35), 0.4)
    add(46.5, ding(2093), 0.7)
    fx = fx[:n]

    # ducking: beat ~15 %, ~6 % under voices
    env = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = np.where(env > 0.01, 0.06, 0.15)
    duck = lowpass(duck, int(0.12 * SR))
    fade = np.minimum(1, np.minimum(np.arange(n) / (0.4 * SR), (n - np.arange(n)) / (1.2 * SR)))
    music = beat(TOTAL) * duck * fade
    fx_duck = np.where(env > 0.01, 0.5, 1.0)
    mix = vo * 0.95 + music + fx * lowpass(fx_duck, int(0.05 * SR)) * 0.45
    mix *= 0.97 / np.abs(mix).max()
    with wave.open(os.path.join(BUILD, "audio.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    # report levels
    rms = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    on = env > 0.01
    print(f"voice {rms(vo[on]):.1f} dB  music under voice {rms(music[on]):.1f} dB  music alone {rms(music[~on]):.1f} dB")


if __name__ == "__main__":
    main()
