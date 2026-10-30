"""Synthesise the narrator (piper, German 'thorsten' voice), make it deep and
documentary-like, and write a timeline.json with exact segment timings."""
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


def synth(text, out):
    raw = out + ".raw.wav"
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", raw,
                    "--length-scale", "1.18", "--noise-scale", "0.5"],
                   input=text.encode(), check=True, capture_output=True)
    # Deeper, warmer, slightly roomy "documentary" voice.
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "aresample=44100,rubberband=pitch=0.82:formant=preserved,"
          "bass=g=5:f=140,equalizer=f=3000:t=q:w=1:g=2,"
          "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"
          "aecho=0.8:0.5:40:0.12")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af,
                    "-ac", "1", "-ar", str(SR), out], check=True)
    os.remove(raw)
    return read_wav(out)


def main():
    ensure_voice()
    os.makedirs(os.path.join(BUILD, "narr"), exist_ok=True)
    timeline, t0, track = [], 0.0, []
    for si, sc in enumerate(SCENES):
        t = sc["lead"]
        segs = []
        for gi, (tts, sub, pause) in enumerate(sc["segments"]):
            t += pause
            audio = synth(tts, os.path.join(BUILD, "narr", f"s{si}_{gi}.wav"))
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
