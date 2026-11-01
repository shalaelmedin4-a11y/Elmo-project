"""All voice lines, synthesised with edge-tts (Microsoft neural voices, German)."""
import asyncio, json, os, ssl, subprocess, wave
import numpy as np
import edge_tts, edge_tts.communicate as _ec

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 44100
FPS = 12

# The cloud sandbox routes HTTPS through a proxy with its own CA; trust it if present.
_CA = "/root/.ccr/ca-bundle.crt"
if os.path.exists(_CA):
    _ec._SSL_CTX = ssl.create_default_context(cafile=_CA)

# speaker -> (voice, rate, pitch)
VOICES = {
    "chad":   ("de-DE-FlorianMultilingualNeural", "-5%", "+0Hz"),
    "intro":  ("de-DE-FlorianMultilingualNeural", "+6%", "+14Hz"),   # young, hyped
    "friend": ("de-DE-KillianNeural", "+6%", "+4Hz"),
    "mom":    ("de-DE-SeraphinaMultilingualNeural", "-2%", "+0Hz"),
    "girl1":  ("de-DE-AmalaNeural", "+8%", "+18Hz"),
    "girl2":  ("de-DE-SeraphinaMultilingualNeural", "+8%", "+28Hz"),
    "girl3":  ("de-DE-KatjaNeural", "+8%", "+10Hz"),
}

# (id, speaker(s), global start time in s, text)
LINES = [
    ("intro1", "intro", 0.10, "POV:"),
    ("intro2", "intro", 1.05, "Ein Tag als Chad …"),
    ("intro3", "intro", 2.55, "mit Halbo!"),
    ("s1", "chad", 5.95, "Sieben Uhr. Zeit, Chad zu sein."),
    ("s2", "chad", 11.00, "Jawline: check."),
    ("s4", "chad", 22.00, "Jeden Morgen dasselbe."),
    ("s5a", "friend", 24.45, "Ey, yo! Was geht ab, Chad?"),
    ("s5b", "chad", 28.05, "Alles entspannt, Bro."),
    ("s6", "chad", 32.70, "Sehr gut. Wie immer."),
    ("s7a", "mom", 36.00, "Wir haben dein Lieblingsessen gemacht, Schatz!"),
    ("s7b", "chad", 39.20, "Ihr seid die Besten."),
    ("s8a", "girl1+girl2+girl3", 42.20, "Hey Chad!"),
    ("s8b", "chad", 47.30, "Folg mir für Tag zwei."),
]


def read_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


async def tts(text, voice, rate, pitch, out):
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out)
            if os.path.getsize(out) > 0:
                return
        except Exception as e:
            print("  retry", voice, e)
        await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"tts failed: {voice}")


def to_wav(mp3, wav):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,highpass=f=70",
                    "-ac", "1", "-ar", str(SR), wav], check=True)
    return read_wav(wav)


async def main():
    d = os.path.join(BUILD, "voice")
    os.makedirs(d, exist_ok=True)
    meta = {}
    for lid, spk, start, text in LINES:
        clips = []
        for i, sp in enumerate(spk.split("+")):
            v, rate, pitch = VOICES[sp]
            mp3 = os.path.join(d, f"{lid}_{sp}.mp3")
            if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
                await tts(text, v, rate, pitch, mp3)
            a = to_wav(mp3, mp3[:-4] + ".wav")
            # a crowd never speaks in perfect sync; the first voice leads
            clips.append(np.pad(a, (int(i * 0.07 * SR), 0)) * (1.0 if i == 0 else 0.6))
        n = max(len(a) for a in clips)
        mix = sum(np.pad(a, (0, n - len(a))) for a in clips) / (len(clips) ** 0.6)
        mix *= 0.9 / np.abs(mix).max()
        np.save(os.path.join(d, f"{lid}.npy"), mix)
        hop = SR // FPS
        env = [float(np.sqrt((mix[i:i + hop] ** 2).mean())) for i in range(0, len(mix), hop)]
        peak = max(env) or 1
        meta[lid] = dict(speaker=spk.split("+")[0], start=start, dur=len(mix) / SR, text=text,
                         env=[round(e / peak, 3) for e in env])
        print(f"{lid:7s} {spk:18s} {start:6.2f}s +{len(mix) / SR:.2f}s  {text}")
    json.dump(meta, open(os.path.join(BUILD, "voices.json"), "w"), ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
