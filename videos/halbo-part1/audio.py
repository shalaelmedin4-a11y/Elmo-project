# Sound for "Halbo – Part 1": voices, class murmur, clock, street, crash, steps, heartbeat. Also writes lips.json.
import json, glob, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal

SR = 48000
TL = json.load(open('halbo/timeline.json')); PICK = json.load(open('halbo/vo/pick.json'))
T = TL['total']; N = int((T + 0.5) * SR)
rng = np.random.default_rng(5)
IMPACT, RESUME = 19.0, 43.0

def filt(x, kind, f, order=2): return signal.sosfilt(signal.butter(order, f, btype=kind, fs=SR, output='sos'), x)
def load(path):
    x, sr = sf.read(path)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    return x
def add(buf, x, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:j, 0] += x[:j - i] * g * l * 1.414; buf[i:j, 1] += x[:j - i] * g * r * 1.414
def env(n, a, r):
    e = np.ones(n); A, R = int(a * SR), int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e
def ir(sec, decay, seed):
    r = np.random.default_rng(seed); n = int(sec * SR); x = r.standard_normal(n) * np.exp(-np.arange(n) / SR * decay)
    x = filt(x, 'lowpass', 5000); return x / np.sqrt(np.sum(x ** 2))
ROOM = [ir(0.6, 9, 1), ir(0.6, 9, 2)]; HALL = [ir(2.2, 2.6, 3), ir(2.2, 2.6, 4)]
def verb(st, irs, wet):
    o = st.copy()
    for c in range(2): o[:, c] += signal.fftconvolve(st[:, c], irs[c])[:len(st)] * wet
    return o
def gain(x, gdb): return x * 10 ** (gdb / 20)

meter = pyln.Meter(SR)
def norm_clip(x, target):  # loudness of a short clip, measured on its active part
    try: l = meter.integrated_loudness(x[:, None] if x.ndim == 1 else x)
    except Exception: return x
    return x * 10 ** ((target - l) / 20) if np.isfinite(l) else x

voice = np.zeros((N, 2)); inner = np.zeros((N, 2)); amb = np.zeros((N, 2)); sfx = np.zeros((N, 2))
lips = {'halbo': np.zeros(int(T * 30) + 2), 'teacher': np.zeros(int(T * 30) + 2)}
def place_voice(key, who, t, target, buf, lipsync=True):
    x = load(f"halbo/vo/{PICK[key]}.wav"); x = filt(x, 'highpass', 80); x = norm_clip(x, target)
    add(buf, x, t)
    if lipsync:
        e = np.abs(signal.hilbert(x)); e = filt(e, 'lowpass', 8, 1); hop = SR // 30
        for k in range(len(x) // hop):
            f = int(t * 30) + k
            if f < len(lips[who]): lips[who][f] = max(lips[who][f], e[k * hop:(k + 1) * hop].mean())
    return len(x) / SR
place_voice('t1', 'teacher', TL['t1'], -18, voice)
place_voice('h1', 'halbo', TL['h1'], -21, voice)
place_voice('h2', 'halbo', TL['h2'], -17, voice)
place_voice('t2', 'teacher', TL['t2'], -18, voice)
# thoughts: no lip movement, softer, with hall reverb
d3 = place_voice('h3', 'halbo', TL['h3'], -22, inner, False)
place_voice('h4', 'halbo', TL['h4'], -22, inner, False)
inner = np.stack([filt(inner[:, c], 'lowpass', 6500) for c in range(2)], 1)
inner = verb(inner, HALL, 0.55)
for k in lips:
    a = lips[k]; m = np.percentile(a[a > 0], 95) if np.any(a > 0) else 1; lips[k] = np.clip(a / m, 0, 1)
    lips[k] = np.where(lips[k] < 0.12, 0, lips[k])
json.dump({k: [round(float(v), 3) for v in a] for k, a in lips.items()}, open('halbo/lips.json', 'w'))

# ---- class murmur: many overlapping, unintelligible voices ----
def babble(dur, density=7):
    files = sorted(glob.glob('halbo/sfx/babble/*.wav')); out = np.zeros(int(dur * SR))
    for s in range(density):
        t = rng.uniform(-1, 0)
        while t < dur:
            x = load(files[rng.integers(len(files))]); x = x / (np.max(np.abs(x)) + 1e-9)
            i = int(max(t, 0) * SR); j = min(len(out), i + len(x)); out[i:j] += x[:j - i] * rng.uniform(0.4, 1.0)
            t += len(x) / SR + rng.uniform(0.3, 1.6)
    out = filt(out, 'lowpass', 2200); out = filt(out, 'highpass', 150)
    return out / (np.max(np.abs(out)) + 1e-9)
mur = babble(T)
m_env = np.zeros(N)
def seg(a, b, ga, gb):
    i, j = int(a * SR), int(b * SR); m_env[i:j] = np.linspace(ga, gb, j - i)
seg(0, 1.0, 0, 1); seg(1.0, 7.45, 1, 1); seg(7.45, 9.45, 0.15, 0.15); seg(9.45, 10.1, 0.15, 1); seg(10.1, 10.3, 1, 0.25)  # hush when the teacher shouts
seg(10.3, 14.5, 0.25, 0.25); seg(14.5, 15.5, 0.25, 0.8); seg(15.5, IMPACT, 0.8, 0.8)                                    # IMPACT: hard cut to silence
seg(RESUME + 1.2, RESUME + 2.0, 0, 1.6); seg(RESUME + 2.0, 52.0, 1.6, 1.4); seg(51.8, 54.3, 1.4, 0.0); seg(58.6, 59.0, 0, 0.4); seg(59.0, 60.25, 0.4, 0.4)
mur = mur[:N] * m_env[:len(mur)]
add(amb, mur, 0, 0.05)

# ---- room tone + very soft pad (not during the frozen world) ----
n = N; t_ = np.arange(n) / SR
tone = (np.sin(2 * np.pi * 110 * t_) + 0.6 * np.sin(2 * np.pi * 164.8 * t_) + 0.4 * np.sin(2 * np.pi * 220.4 * t_)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t_))
tone = filt(tone, 'lowpass', 600) * 0.004
pe = np.ones(n); pe[int(IMPACT * SR):int(RESUME * SR)] = 0.35; pe[int(60.25 * SR):] = 0
add(sfx, tone * pe, 0)
room = filt(rng.standard_normal(n), 'lowpass', 900) * 0.0025; room[int(IMPACT * SR):int(RESUME * SR)] *= 0.0
add(amb, room, 0)

# ---- daydream: soft waves ----
nw = int(2.3 * SR); w = filt(rng.standard_normal(nw), 'lowpass', 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.6 * np.arange(nw) / SR)) * env(nw, 0.3, 0.4)
add(sfx, w, 7.35, 0.05)

# ---- street: speeding car, braking, freeze ----
def engine(dur, f0, f1):
    n = int(dur * SR); f = np.linspace(f0, f1, n); ph = np.cumsum(f) / SR
    x = signal.sawtooth(2 * np.pi * ph) * 0.6 + signal.sawtooth(2 * np.pi * ph * 2.01) * 0.3
    x = filt(x, 'lowpass', 900) + filt(rng.standard_normal(n), 'bandpass', [300, 1500]) * 0.3
    return x * np.linspace(0.15, 1, n) ** 2
add(sfx, engine(IMPACT - 14.0, 70, 110), 14.0, 0.06, 0.3)
nsq = int(0.7 * SR); sq = filt(rng.standard_normal(nsq), 'bandpass', [1800, 3800]) * (1 + 0.5 * np.sin(2 * np.pi * 30 * np.arange(nsq) / SR)) * env(nsq, 0.08, 0.05)
add(sfx, sq, IMPACT - 0.7, 0.05, 0.3)
nf = int(1.2 * SR); thump = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 30, nf)) / SR) * np.exp(-np.arange(nf) / SR * 3)
add(sfx, thump, IMPACT, 0.25)                      # time stops: deep "whoom"
# clock ticks in the frozen world
nt = int(0.05 * SR); tick = filt(rng.standard_normal(nt), 'bandpass', [2500, 6000]) * np.exp(-np.arange(nt) / SR * 160)
tock = filt(rng.standard_normal(nt), 'bandpass', [1500, 3500]) * np.exp(-np.arange(nt) / SR * 160)
k = 0; tt = IMPACT + 0.9
while tt < RESUME - 0.3:
    add(sfx, tick if k % 2 == 0 else tock, tt, 0.07 if tt < 23 else 0.045); tt += 1.0; k += 1
# ---- Halbo moving through the frozen world ----
def step(hard=False):
    n = int(0.12 * SR); x = filt(rng.standard_normal(n), 'bandpass', [120, 2400 if hard else 1200]) * np.exp(-np.arange(n) / SR * (45 if hard else 30))
    return x + np.sin(2 * np.pi * 70 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 40) * 0.6
nch = int(0.6 * SR); chair = filt(rng.standard_normal(nch), 'bandpass', [300, 900]) * (1 + np.sin(2 * np.pi * 23 * np.arange(nch) / SR)) * env(nch, 0.05, 0.2)
add(sfx, chair, 23.2, 0.04)
for a, b, dt in ((24.3, 26.8, 0.5), (27.6, 28.4, 0.5), (30.1, 31.4, 0.38)):
    tt = a
    while tt < b: add(sfx, step(), tt, 0.06, rng.uniform(-0.3, 0.3)); tt += dt
add(sfx, filt(rng.standard_normal(int(0.08 * SR)), 'lowpass', 900) * np.exp(-np.arange(int(0.08 * SR)) / SR * 60), 27.1, 0.04)   # tap on the shoulder
def door_sound():
    n = int(0.5 * SR); t_ = np.arange(n) / SR
    click = filt(rng.standard_normal(n), 'bandpass', [1500, 5000]) * np.exp(-t_ * 80)
    creak = np.sin(2 * np.pi * np.cumsum(np.linspace(380, 260, n)) / SR) * 0.15 * env(n, 0.05, 0.2)
    clunk = np.sin(2 * np.pi * 95 * t_) * np.exp(-t_ * 18) * 0.6
    return click + creak + clunk
add(sfx, door_sound(), 31.25, 0.08)
tt = 32.0
while tt < 35.5: add(sfx, step(True), tt, 0.07, rng.uniform(-0.2, 0.2)); tt += 0.31
add(sfx, door_sound(), 35.65, 0.1, 0.2)
ndr = int(2.6 * SR); drag = filt(rng.standard_normal(ndr), 'bandpass', [200, 1500]) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 1.2 * np.arange(ndr) / SR))) * env(ndr, 0.3, 0.3)
add(sfx, drag, 38.6, 0.03)
tt = 38.7
while tt < 41.1: add(sfx, step(True), tt, 0.04); tt += 0.55
add(sfx, filt(rng.standard_normal(int(0.25 * SR)), 'lowpass', 500) * np.exp(-np.arange(int(0.25 * SR)) / SR * 14), 41.6, 0.05)

# ---- time runs again: crash, glass, metal, screams, chairs ----
nr = int(0.5 * SR); rev = filt(rng.standard_normal(nr), 'bandpass', [200, 2000]) * np.linspace(0, 1, nr) ** 2
add(sfx, rev, RESUME - 0.5, 0.05)
def crash():
    n = int(2.8 * SR); t_ = np.arange(n) / SR
    bang = filt(rng.standard_normal(n), 'lowpass', 3000) * np.exp(-t_ * 7)
    boom = np.sin(2 * np.pi * np.cumsum(np.linspace(80, 35, n)) / SR) * np.exp(-t_ * 4)
    metal = np.zeros(n)
    for f in (420, 670, 1130, 1590, 2210): metal += np.sin(2 * np.pi * f * t_ * (1 + 0.002 * rng.standard_normal())) * np.exp(-t_ * rng.uniform(3, 7))
    glass = np.zeros(n)
    for _ in range(140):
        i = int(rng.uniform(0.02, 1.4) ** 1.5 * SR); m = int(0.04 * SR)
        if i + m < n: glass[i:i + m] += np.sin(2 * np.pi * rng.uniform(3500, 9000) * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * 120) * rng.uniform(0.2, 1)
    return bang * 1.0 + boom * 1.2 + metal * 0.12 + glass * 0.35
add(sfx, crash(), RESUME + 0.02, 0.45, 0.25)
def scream(f0, dur):
    n = int(dur * SR); t_ = np.arange(n) / SR
    f = f0 * (1 + 0.25 * np.exp(-t_ * 3)) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t_)); ph = np.cumsum(f) / SR
    src = signal.sawtooth(2 * np.pi * ph, 0.3) + 0.15 * rng.standard_normal(n)
    out = np.zeros(n)
    for fc, bw, g in ((850, 140, 1.0), (1250, 160, 0.7), (2700, 300, 0.35)): out += filt(src, 'bandpass', [fc - bw, fc + bw]) * g
    return out * env(n, 0.04, dur * 0.6)
for i in range(7):
    add(sfx, scream(rng.uniform(320, 520), rng.uniform(0.6, 1.1)), RESUME + 0.12 + rng.uniform(0, 0.35), 0.035, rng.uniform(-0.6, 0.6))
for i in range(6):
    add(sfx, chair * rng.uniform(0.6, 1), RESUME + 0.9 + rng.uniform(0, 0.8), 0.03, rng.uniform(-0.5, 0.5))
tt = RESUME + 1.3
while tt < RESUME + 3.4: add(sfx, step(), tt, 0.03, rng.uniform(-0.6, 0.6)); tt += rng.uniform(0.08, 0.2)
# ---- heartbeat getting louder (52-59.3) ----
def beat():
    n = int(0.35 * SR); t_ = np.arange(n) / SR
    b = np.sin(2 * np.pi * 52 * t_) * np.exp(-t_ * 18); b2 = np.sin(2 * np.pi * 48 * t_) * np.exp(-t_ * 22)
    out = b.copy(); s = int(0.24 * SR); out[s:] += b2[:n - s] * 0.7; return filt(out, 'lowpass', 180)
tt = 51.6; k = 0
while tt < 60.2:
    add(sfx, beat(), tt, 0.12 + 0.55 * min(1, (tt - 51.8) / 6)); tt += 60 / (88 + k * 1.5); k += 1

# ---- mix ----
L = int(T * SR)
mix = voice + inner + amb + sfx
mix = np.stack([filt(mix[:, c], 'highpass', 30) for c in range(2)], 1)
cut = int(60.25 * SR); fade = int(0.05 * SR); mix[cut:cut + fade] *= np.linspace(1, 0, fade)[:, None]; mix[cut + fade:] = 0
mix = mix[:L]
l = meter.integrated_loudness(mix); mix *= 10 ** ((-16 - l) / 20)
pk = np.max(np.abs(mix)); lim = 10 ** (-1.5 / 20)
if pk > lim: mix = np.tanh(mix / lim * 0.9) * lim / np.tanh(0.9)
sf.write('halbo/mix.wav', mix.astype(np.float32), SR, subtype='PCM_24')
print('ok LUFS', round(meter.integrated_loudness(mix), 1), 'thought dur', round(d3, 2))
