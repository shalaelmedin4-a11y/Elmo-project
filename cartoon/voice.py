#!/usr/bin/env python3
"""Builds the narration track + lip-sync data.

Each spoken phrase is one file in cartoon/voice/ (cue_00.wav, cue_01.wav, ...).
Missing files are generated with a neural German voice (Microsoft Edge
'FlorianMultilingual', young male). Record your own takes with the same file
names to replace them - existing files are never overwritten unless --tts.

Outputs:
  build/voice_track.wav      49 s, 48 kHz mono, phrases placed on their subtitle times,
                             soft breaths before some lines
  build/lipsync.json         mouth-opening level per video frame (12 fps) for Halbo
"""
import asyncio
import json
import os
import ssl
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VDIR = os.path.join(ROOT, "cartoon", "voice")
SR = 48000
DUR = 49.0
FPS = 12
VOICE = "de-DE-FlorianMultilingualNeural"

# (start in final video [s], text, rate, pitch, breath_before)
CUES = [
    (0.40, "Ein Tag als Soldat …", "+4%", "+14Hz", False),
    (2.30, "mit Halbo!", "+0%", "+18Hz", False),
    (5.00, "Fünf Uhr morgens.", "-6%", "+4Hz", True),
    (7.50, "Hier gibt's keine Snooze-Taste.", "+0%", "+6Hz", False),
    (12.80, "Antreten, dann laufen.", "-4%", "+4Hz", True),
    (15.80, "Jeden Tag.", "-10%", "+2Hz", True),
    (19.60, "Hindernisbahn!", "+0%", "+6Hz", True),
    (21.60, "Hier merkst du, wer wirklich durchzieht.", "-6%", "+4Hz", True),
    (27.60, "Mittag.", "-4%", "+6Hz", False),
    (29.20, "Die einzige halbe Stunde, in der keiner schreit.", "+2%", "+6Hz", False),
    (34.60, "Nachmittags Übung im Gelände.", "-4%", "+0Hz", True),
    (37.60, "Und dann wird's ernst.", "-12%", "-6Hz", True),
    (41.60, "Morgen wieder um fünf.", "-10%", "+0Hz", True),
    (44.40, "Folg mir für Tag zwei!", "-4%", "+6Hz", False),
]


def tts(text, rate, pitch, out_mp3):
    import edge_tts
    import edge_tts.communicate as cm
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        cm._SSL_CTX = ssl.create_default_context(cafile=ca)

    async def go():
        await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch,
                                   proxy=os.environ.get("HTTPS_PROXY")).save(out_mp3)
    for _ in range(4):
        try:
            asyncio.run(go())
            if os.path.getsize(out_mp3) > 1000:
                return
        except Exception as e:  # the service sometimes drops a request
            print("  retry:", e)
    raise SystemExit(f"TTS failed for: {text}")


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-af",
                                   "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                                   "silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                                   "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, "<i2").astype(np.float32) / 32768


def breath(rng, d=0.32):
    n = int(d * SR)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < 400) | (f > 3500)] = 0
    x = np.fft.irfft(X, n)
    t = np.arange(n) / n
    return x / np.max(np.abs(x)) * np.sin(np.pi * t) ** 2


def main():
    force = "--tts" in sys.argv
    os.makedirs(VDIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    rng = np.random.default_rng(5)
    track = np.zeros(int(DUR * SR), np.float32)
    timing = []
    for i, (start, text, rate, pitch, br) in enumerate(CUES):
        wav = os.path.join(VDIR, f"cue_{i:02d}.wav")
        if force or not os.path.exists(wav):
            mp3 = os.path.join(ROOT, "build", f"cue_{i:02d}.mp3")
            print(f"TTS cue {i:02d}: {text}")
            tts(text, rate, pitch, mp3)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1", wav], check=True)
        x = load(wav)
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.8
        a = int(start * SR)
        if br:
            b = breath(rng) * 0.045
            s0 = max(0, a - len(b) - int(0.04 * SR))
            track[s0:s0 + len(b)] += b
        track[a:a + len(x)] += x[: len(track) - a]
        timing.append({"start": start, "end": round(start + len(x) / SR, 2), "text": text})
        print(f"cue {i:02d} {start:5.2f}-{start + len(x) / SR:5.2f}s  {text}")
    for a, b in zip(timing, timing[1:]):
        if a["end"] > b["start"] - 0.1:
            print("WARNING: overlap between", a["text"], "and", b["text"])
    # lip-sync: RMS per video frame, smoothed and normalised (0..1)
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(track[k * hop:(k + 1) * hop] ** 2)) for k in range(int(DUR * FPS))])
    lvl = np.clip(rms / (np.percentile(rms[rms > 1e-3], 90) + 1e-9), 0, 1)
    with open(os.path.join(ROOT, "build", "lipsync.json"), "w") as f:
        json.dump({"fps": FPS, "level": [round(float(v), 3) for v in lvl], "cues": timing}, f)
    data = (np.clip(track, -1, 1) * 32767).astype("<i2")
    with wave.open(os.path.join(ROOT, "build", "voice_track.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("wrote build/voice_track.wav + build/lipsync.json")


if __name__ == "__main__":
    main()
