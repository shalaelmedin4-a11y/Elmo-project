"""Record the boy's voice-over with an expressive neural voice (Chatterbox,
German) and write timeline.json with exact segment timings.

For every line several takes are generated; Whisper listens to each take and
the clearest one with a sensible length wins. Breaths, giggles, the scream and
the voice cracks are placed around the lines."""
import difflib, hashlib, json, os, re, subprocess, wave
import numpy as np
from script_data import SCENES, SCREAM, LAUGH

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
TAKES = os.path.join(BUILD, "takes")
REF = os.path.join(HERE, "voice_ref.wav")   # teen timbre the model clones
SR = 44100
MAX_TAKES = 6
GOOD = 0.93
NUMS = [("sechs uhr dreissig", "630 uhr"), ("zweiundzwanzig", "22"), ("vierzehn", "14"),
        ("zwölf", "12"), ("hundert", "100")]
_model = _whisper = None


def read_wav(path):
    with wave.open(path) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return data


def write_wav(path, x, sr=SR):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def ff(src, dst, af):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ac", "1", "-ar", str(SR), dst], check=True)


def model():
    global _model
    if _model is None:
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.set_num_threads(os.cpu_count())
        _model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    return _model


def whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("small", device="cpu", compute_type="int8")
    return _whisper


def ensure_ref():
    """Default Chatterbox voice, shifted up into a 14-year-old's register."""
    if os.path.exists(REF):
        return
    import torch, torchaudio as ta
    torch.manual_seed(1)
    m = model()
    w = m.generate("Na, Leute? Also heute zeig ich euch mal meine Morgenroutine. Ganz ehrlich, das wird richtig krass.",
                   language_id="de", exaggeration=0.6, cfg_weight=0.5, temperature=0.8)
    raw = REF + ".raw.wav"
    ta.save(raw, w, m.sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "rubberband=pitch=1.3", "-ar", "24000", REF], check=True)
    os.remove(raw)


def take(line, k):
    """One take of a line (cached), cleaned up and at SR."""
    key = hashlib.sha1(f"{line['tts']}|{line['ex']}|{k}|v2".encode()).hexdigest()[:12]
    out = os.path.join(TAKES, f"{key}.wav")
    if not os.path.exists(out):
        import torch, torchaudio as ta
        torch.manual_seed(1000 + k)
        m = model()
        w = m.generate(line["tts"], language_id="de", audio_prompt_path=REF, exaggeration=line["ex"],
                       cfg_weight=0.35 + 0.1 * (1 - line["ex"]), temperature=0.8 + 0.05 * k)
        raw = out + ".raw.wav"
        ta.save(raw, w, m.sr)
        ff(raw, out, "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
                     "silenceremove=start_periods=1:start_threshold=-42dB,areverse,"
                     "highpass=f=90,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                     "apad=pad_dur=0.03")
        os.remove(raw)
    return read_wav(out)


def norm(s):
    s = s.lower().replace("ß", "ss").replace("-", " ")
    s = re.sub(r"[^a-zäöü0-9 ]", "", s)
    for a, b in NUMS:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def squeeze_pauses(a, max_gap=0.28):
    """Shorten silences inside a take so the line flows like real speech."""
    hop = int(0.01 * SR)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, mode="same"))[::hop]
    quiet = rms < 0.012
    out, i, n = [], 0, len(quiet)
    while i < n:
        j = i
        while j < n and quiet[j] == quiet[i]:
            j += 1
        chunk = a[i * hop: j * hop]
        if quiet[i] and 0 < i and j < n and (j - i) * 0.01 > max_gap:
            keep = int(max_gap * SR)
            chunk = np.concatenate([chunk[: keep // 2], chunk[-keep // 2:]])
        out.append(chunk)
        i = j
    return np.concatenate(out)


def trim_to_line(a, line):
    """Cut everything after the last expected word (the model sometimes keeps babbling)."""
    _, ws = transcribe(a, words=True)
    want = norm(line["tts"]).split()
    if not ws or not want:
        return a
    last = want[-1]
    ends = [w.end for w in ws if difflib.SequenceMatcher(None, norm(w.word), last).ratio() > 0.6]
    if not ends:
        return a
    # first occurrence of the final word after enough words were spoken
    cut = ends[0]
    for w_end in ends:
        if sum(1 for w in ws if w.end <= w_end) >= len(want) * 0.7:
            cut = w_end
            break
    n = min(len(a), int((cut + 0.12) * SR))
    out = a[:n].copy()
    k = int(0.04 * SR)
    out[-k:] *= np.linspace(1, 0, k)
    return out


def transcribe(a, words=False):
    import librosa
    y = librosa.resample(a, orig_sr=SR, target_sr=16000)
    segs, _ = whisper().transcribe(y, language="de", word_timestamps=words)
    segs = list(segs)
    text = " ".join(s.text for s in segs)
    ws = [w for s in segs for w in (s.words or [])] if words else []
    return text, ws


def best_take(line):
    refs = [line["tts"], line["sub"]] + line.get("hear", [])
    chars = len(norm(line["tts"]))
    best, best_score = None, -9
    for k in range(MAX_TAKES):
        a = squeeze_pauses(trim_to_line(take(line, k), line))
        dur = len(a) / SR
        text, _ = transcribe(a)
        score = max(difflib.SequenceMatcher(None, norm(text), norm(r)).ratio() for r in refs)
        if dur > chars * 0.085 + 0.9 or dur < chars * 0.035:
            score -= 0.3          # rushed or dragging take
        print(f"   take {k}: {score:.2f} {dur:.2f}s  '{text.strip()}'", flush=True)
        if score > best_score:
            best, best_score = a, score
        if best_score >= GOOD:
            break
    return best


def voice_crack(a, word):
    """Make the given word break upward like a voice in puberty."""
    _, ws = transcribe(a, words=True)
    hit = next((w for w in ws if norm(word) in norm(w.word)), None)
    if hit is None:
        print("   (crack word not found)")
        return a
    s0, s1 = int((hit.start + (hit.end - hit.start) * 0.35) * SR), int(hit.end * SR)
    s1 = min(s1, len(a))
    if s1 - s0 < 2000:
        return a
    tmp = os.path.join(BUILD, "crack.wav")
    write_wav(tmp, a[s0:s1])
    ff(tmp, tmp + ".hi.wav", "rubberband=pitch=1.35")
    hi = read_wav(tmp + ".hi.wav")[: s1 - s0]
    hi = np.pad(hi, (0, s1 - s0 - len(hi)))
    fade = np.ones(s1 - s0)
    k = int(0.025 * SR)
    fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
    a = a.copy()
    a[s0:s1] = a[s0:s1] * (1 - fade) + hi * fade
    return a


def breath(seed, d=0.42):
    """A soft nasal inhale."""
    r = np.random.default_rng(seed)
    n = int(d * SR)
    x = r.normal(0, 1, n)
    # crude formant-ish colouring of the noise
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    shape = np.exp(-((f - 1300) / 900) ** 2) + 0.5 * np.exp(-((f - 3200) / 1200) ** 2)
    x = np.fft.irfft(spec * shape, n)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** 0.7) ** 1.5
    x = x * env
    return x / np.abs(x).max() * 0.07


def level(a, rms=0.09):
    return a * (rms / max(1e-6, np.sqrt((a ** 2).mean())))


def pick_laughs():
    laughs = []
    for k in range(5):
        a = take(LAUGH, k)
        d = len(a) / SR
        if 0.3 < d < 1.6:
            laughs.append(level(a, 0.06))
    return laughs or [level(take(LAUGH, 0)[: int(0.8 * SR)], 0.06)]


def pick_scream():
    best = None
    for k in range(3):
        a = take(SCREAM, k)
        d = len(a) / SR
        if 1.0 < d < 3.2 and (best is None or np.abs(a).max() > np.abs(best).max()):
            best = a
    a = squeeze_pauses(best if best is not None else take(SCREAM, 0), 0.15)[: int(1.9 * SR)].copy()
    a[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
    return level(a, 0.14)


def main():
    os.makedirs(TAKES, exist_ok=True)
    ensure_ref()
    laughs = pick_laughs()
    scream = pick_scream()
    timeline, t0, track, nl = [], 0.0, [], 0
    for si, sc in enumerate(SCENES):
        print(sc["name"], flush=True)
        t = sc["lead"]
        segs, events = [], {}
        for gi, line in enumerate(sc["segments"]):
            if sc["name"] == "water" and gi == 2:
                # freeze, then the scream, then the line
                ts = max(2.6, t + 0.25)
                track.append((t0 + ts, scream))
                events = dict(scream=round(ts, 3), scream_end=round(ts + len(scream) / SR, 3))
                t = ts + len(scream) / SR
            t += line["pause"]
            if line["pre"] == "breath":
                b = breath(si * 10 + gi)
                track.append((t0 + t - 0.05, b))
                t += len(b) / SR - 0.05
            print(" ", line["tts"], flush=True)
            a = best_take(line)
            if line["crack"]:
                a = voice_crack(a, line["crack"])
            a = level(a)
            dur = len(a) / SR
            seg = dict(start=round(t, 3), end=round(t + dur, 3), text=line["sub"])
            track.append((t0 + t, a))
            t += dur
            if line["post"] == "laugh":
                lg = laughs[nl % len(laughs)]; nl += 1
                track.append((t0 + t + 0.08, lg))
                t += 0.08 + len(lg) / SR
            seg["post_end"] = round(t, 3)
            segs.append(seg)
        dur = max(sc["min_dur"], t + sc["tail"])
        timeline.append(dict(name=sc["name"], start=round(t0, 3), dur=round(dur, 3), segments=segs, events=events))
        t0 += dur
    total = t0
    mix = np.zeros(int(total * SR) + SR, np.float32)
    for start, a in track:
        i = int(start * SR)
        mix[i:i + len(a)] += a[: len(mix) - i]
    mix /= max(1e-6, np.abs(mix).max()) / 0.9
    np.save(os.path.join(BUILD, "narration.npy"), mix[: int(total * SR)])
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(dict(total=round(total, 3), scenes=timeline), f, indent=1, ensure_ascii=False)
    for s in timeline:
        print(s["name"], s["start"], s["dur"], [(g["start"], g["end"]) for g in s["segments"]], s["events"])
    print("total", total)


if __name__ == "__main__":
    main()
