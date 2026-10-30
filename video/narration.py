"""Synthesise the narration: the boy himself (piper, German 'thorsten' voice
shifted up into a cracking teenage voice), and write a timeline.json with
exact segment timings."""
import json, os, subprocess, sys, wave
import numpy as np
from script_data import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
VOICE = os.path.join(BUILD, "voice", "de_DE-thorsten-high.onnx")
SR = 44100


def ensure_voice():
    if os.path.exists(VOICE):
        return
    os.makedirs(os.path.dirname(VOICE), exist_ok=True)
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/"
    for ext in (".onnx", ".onnx.json"):
        subprocess.run(["curl", "-sSL", "-o", VOICE.replace(".onnx", ext), base + "de_DE-thorsten-high" + ext], check=True)


def read_wav(path):
    with wave.open(path) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return data


def _ff(src, dst, af):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af,
                    "-ac", "1", "-ar", str(SR), dst], check=True)


def write_wav(path, x):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def synth(text, out, crack=None):
    raw = out + ".raw.wav"
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", raw,
                    "--length-scale", "1.05", "--noise-scale", "0.7", "--noise-w-scale", "0.9"],
                   input=text.encode(), check=True, capture_output=True)
    # 14-year-old: pitch and formants shifted up, thin and dry, trying hard to sound cool.
    _ff(raw, out, "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                  "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                  "aresample=44100,rubberband=pitch=1.38,highpass=f=140,"
                  "equalizer=f=2500:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
    os.remove(raw)
    audio = read_wav(out)
    if crack:
        # voice crack: one syllable jumps up into falsetto
        a, b = (int(f * len(audio)) for f in crack)
        part = out + ".crack.wav"
        write_wav(part, audio[a:b])
        _ff(part, part + ".hi.wav", "rubberband=pitch=1.6,volume=1.15")
        hi = read_wav(part + ".hi.wav")[: b - a]
        hi = np.pad(hi, (0, b - a - len(hi)))
        fade = np.ones(b - a)
        k = min(int(0.02 * SR), (b - a) // 3)
        fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        audio = audio.copy()
        audio[a:b] = audio[a:b] * (1 - fade) + hi * fade
        write_wav(out, audio)
        os.remove(part); os.remove(part + ".hi.wav")
    return audio


def main():
    ensure_voice()
    os.makedirs(os.path.join(BUILD, "narr"), exist_ok=True)
    timeline, t0, track = [], 0.0, []
    for si, sc in enumerate(SCENES):
        t = sc["lead"]
        segs = []
        for gi, (tts, sub, pause, *crack) in enumerate(sc["segments"]):
            t += pause
            audio = synth(tts, os.path.join(BUILD, "narr", f"s{si}_{gi}.wav"), crack[0] if crack else None)
            dur = len(audio) / SR
            segs.append(dict(start=round(t, 3), end=round(t + dur, 3), text=sub))
            track.append((t0 + t, audio))
            t += dur
        dur = max(sc["min_dur"], t + sc["tail"])
        timeline.append(dict(name=sc["name"], start=round(t0, 3), dur=round(dur, 3), segments=segs))
        t0 += dur
    total = t0
    mix = np.zeros(int(total * SR) + SR, np.float32)
    for start, a in track:
        i = int(start * SR)
        mix[i:i + len(a)] += a
    mix /= max(1e-6, np.abs(mix).max()) / 0.9
    np.save(os.path.join(BUILD, "narration.npy"), mix[: int(total * SR)])
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(dict(total=round(total, 3), scenes=timeline), f, indent=1, ensure_ascii=False)
    for s in timeline:
        print(s["name"], s["start"], s["dur"], [(g["start"], g["end"]) for g in s["segments"]])
    print("total", total)


if __name__ == "__main__":
    main()
