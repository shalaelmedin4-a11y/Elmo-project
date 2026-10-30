# Background music + sound design + voice mix for the Messi video.
# Everything is synthesized here; levels are set so the voice stays clearly on top.
import json, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal

SR = 48000
sj = json.load(open('scenes.json')); T = sj['total']; S = {s['id']: s for s in sj['scenes']}
N = int((T + 1.0) * SR)
rng = np.random.default_rng(11)
SHOT, BALL_IN, TOUCH = 10.45, 10.85, [5.5, 5.9, 6.3]

def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output='sos')
def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x)
def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    e[:A] = np.linspace(0, 1, A, endpoint=False) if A else e[:A]
    e[A:A + D] = np.linspace(1, s, D, endpoint=False)[:max(0, min(D, n - A))]
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e
def add(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    j0 = max(0, -i); i = max(0, i); j = min(len(buf), i + len(x) - j0)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    seg = x[j0:j0 + (j - i)] * gain
    buf[i:j, 0] += seg * l * 1.414; buf[i:j, 1] += seg * r * 1.414
def reverb_ir(sec, decay, seed):
    r = np.random.default_rng(seed); n = int(sec * SR)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * decay)
    ir = filt(ir, 'lowpass', 6000); ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))
IR = [reverb_ir(2.6, 2.4, 1), reverb_ir(2.6, 2.4, 2)]
def reverb(st, wet):
    out = st.copy()
    for c in range(2):
        out[:, c] += signal.fftconvolve(st[:, c], IR[c])[:len(st)] * wet
    return out
def saw(freq, n, harmonics=24):
    t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(1, harmonics + 1):
        if freq * k > 9000: break
        x += np.sin(2 * np.pi * freq * k * t + k * 0.7) / k
    return x
def note(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- music ----------------
music = np.zeros((N, 2))
bpm = 92; beat = 60 / bpm; bar = 4 * beat
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
roots = [45, 41, 48, 43]
end_music = T - 0.3
# pad (whole track), 2 bars per chord
k = 0; t0 = 0.0
while t0 < end_music:
    ch = prog[k % 4]; n = int(2 * bar * SR + 1.5 * SR)
    pad = np.zeros(n)
    for m in ch:
        for det in (-0.08, 0.0, 0.08):
            pad += saw(note(m + 12) * 2 ** (det / 12), n, 12)
    pad = filt(pad, 'lowpass', 1400, 2) * env_adsr(n, 1.2, 0.5, 0.85, 1.5)
    add(music, pad * 0.010, t0, pan=-0.15)
    # sub bass
    nb = int(2 * bar * SR); tb = np.arange(nb) / SR
    sub = np.sin(2 * np.pi * note(roots[k % 4] - 12) * tb) * env_adsr(nb, 0.05, 0.4, 0.7, 0.4)
    add(music, sub * 0.05, t0)
    k += 1; t0 += 2 * bar
# rhythm only in the action part (receive .. shot), soft
r0, r1 = S['receive']['start'], S['shot']['start'] + 2.0
nk = int(0.3 * SR); tk = np.arange(nk) / SR
kick = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-tk * 35)) / SR) * np.exp(-tk * 11)
nh = int(0.05 * SR); hat = filt(rng.standard_normal(nh), 'highpass', 7000) * np.exp(-np.arange(nh) / SR * 70)
npl = int(0.35 * SR); tp = np.arange(npl) / SR
arp = [57, 64, 69, 72, 69, 64, 60, 64]
b = r0; i = 0
while b < r1:
    fade = min(1, (b - r0) / 3) * min(1, (r1 - b) / 1.5)
    if i % 4 in (0, 2): add(music, kick * 0.16 * fade, b)
    add(music, hat * 0.025 * fade, b + beat / 2, pan=0.35)
    for s16 in range(2):
        m = arp[(i * 2 + s16) % 8] + 12
        pl = (np.sin(2 * np.pi * note(m) * tp) + 0.3 * np.sin(2 * np.pi * note(m) * 2 * tp)) * np.exp(-tp * 9)
        add(music, pl * 0.012 * fade, b + s16 * beat / 2, pan=0.3 if s16 else -0.3)
    b += beat; i += 1
music = reverb(music, 0.35)
music = np.stack([filt(music[:, c], 'highpass', 35) for c in range(2)], 1)

# ---------------- sound design ----------------
sfx = np.zeros((N, 2))
def whoosh(dur=0.55, f0=300, f1=2600):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 512
    for s in range(0, n, blk):
        f = f0 * (f1 / f0) ** (s / n)
        out[s:s + blk] = signal.sosfilt(signal.butter(2, [f * 0.7, f * 1.3], btype='band', fs=SR, output='sos'), x[s:s + blk])
    return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
def touch_tick():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 220 * t) * 0.8 + filt(rng.standard_normal(n), 'bandpass', [900, 2500]) * 0.25) * np.exp(-t * 45)
def strike():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t * 20) + 60) / SR) * np.exp(-t * 16) + filt(rng.standard_normal(n), 'bandpass', [400, 3000]) * np.exp(-t * 60) * 0.6)
def net_hit():
    n = int(1.6 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-t * 9)) / SR) * np.exp(-t * 3.2)
    swish = filt(rng.standard_normal(n), 'bandpass', [1200, 6000]) * np.exp(-t * 7) * 0.35
    return boom * 0.9 + swish
def crowd(dur, swell=0.6):
    n = int(dur * SR); x = rng.standard_normal(n)
    x = filt(x, 'bandpass', [250, 2800], 2)
    mod = 1 + 0.25 * filt(rng.standard_normal(n), 'lowpass', 3, 1) * 40
    e = np.minimum(1, np.arange(n) / (swell * SR)) * np.linspace(1, 0, n) ** 1.3
    return x * mod * e
def heartbeat(count, bpm=72):
    n = int(count * 60 / bpm * SR) + SR; out = np.zeros(n); nb = int(0.18 * SR); tb = np.arange(nb) / SR
    thump = np.sin(2 * np.pi * 52 * tb) * np.exp(-tb * 22)
    for i in range(count):
        s = int(i * 60 / bpm * SR); out[s:s + nb] += thump; out[s + int(0.22 * SR):s + int(0.22 * SR) + nb] += thump * 0.6
    return out
def riser(dur):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 512
    for s in range(0, n, blk):
        f = 200 * (4000 / 200) ** (s / n)
        out[s:s + blk] = signal.sosfilt(signal.butter(2, [f * 0.8, f * 1.2], btype='band', fs=SR, output='sos'), x[s:s + blk])
    return out * np.linspace(0, 1, n) ** 2

# transitions
for s in sj['scenes'][1:]:
    add(sfx, whoosh(), s['start'] - 0.28, 0.05, pan=rng.uniform(-0.4, 0.4))
# heartbeat under "kein Platz"
add(sfx, heartbeat(int(S['space']['dur'] * 72 / 60)), S['space']['start'] + 0.4, 0.22)
# touches (trick scene at real speed, touches scene in slow motion)
tr = S['trick']
for ta in TOUCH:
    if ta >= 5.4:
        U = 0.4 + (ta - 5.4) / 2.6 * 0.6
        add(sfx, touch_tick(), tr['start'] + U * tr['dur'], 0.10, pan=0.1)
tc = S['touches']
for i, ta in enumerate(TOUCH):
    U = (ta - 5.25) / 1.6
    add(sfx, touch_tick(), tc['start'] + U * tc['dur'], 0.18, pan=-0.1 + 0.05 * i)
# strike + net + crowd (hook and main shot)
hk = S['hook']; sh = S['shot']
for st, strike_t, in_t, g in ((hk, (SHOT - 9.9) / 0.3, (BALL_IN - 9.9) / 0.3, 0.8), (sh, 2.2 + (SHOT - (SHOT - 0.12)) / 0.3, 2.2 + (BALL_IN - (SHOT - 0.12)) / 0.3, 1.0)):
    add(sfx, riser(strike_t), st['start'], 0.03 * g)
    add(sfx, strike(), st['start'] + strike_t, 0.28 * g)
    add(sfx, net_hit(), st['start'] + in_t, 0.30 * g)
    add(sfx, crowd(4.0, 0.25), st['start'] + in_t + 0.05, 0.10 * g)
# low stadium ambience during the action
amb = crowd(S['shot']['start'] - S['receive']['start'], 2.0) * 0.6
add(sfx, amb, S['receive']['start'], 0.03)
sfx = reverb(sfx, 0.18)

# ---------------- voice ----------------
vo = np.zeros((N, 2)); vo_on = np.zeros(N)
for s in sj['scenes']:
    if s['id'] == 'outro': continue
    x, sr = sf.read(f"vo2/fast/{s["id"]}.wav")
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    x = filt(x, 'highpass', 70)
    at = s['start'] + 0.25
    add(vo, x, at); i = int(at * SR); vo_on[i:i + len(x)] = 1
meter = pyln.Meter(SR)
def lufs(st): return meter.integrated_loudness(st[:int(T * SR)])
def gain_to(st, target): return st * 10 ** ((target - lufs(st)) / 20)
vo = gain_to(vo, -16.0)
music = gain_to(music, -30.0)
sfx = gain_to(sfx, -27.0)
# gentle ducking of the music under the voice
duck = signal.sosfiltfilt(sos('lowpass', 2.0, 1), vo_on)
music *= (1 - 0.45 * np.clip(duck, 0, 1))[:, None]
mix = vo + music + sfx
# end fade
fo = int(2.2 * SR); e = int(T * SR); mix[e - fo:e] *= np.linspace(1, 0, fo)[:, None]; mix = mix[:e]
mix = gain_to(mix, -15.0)
peak = np.max(np.abs(mix)); lim = 10 ** (-1.5 / 20)
if peak > lim: mix *= lim / peak
sf.write('mix2.wav', mix.astype(np.float32), SR, subtype='PCM_24')
print('done', T, 'LUFS', round(lufs(mix), 1), 'peak dB', round(20 * np.log10(np.max(np.abs(mix))), 2))
