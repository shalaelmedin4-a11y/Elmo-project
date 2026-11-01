"""All voice lines for \"POV: Ein Tag als junger Naruto\", synthesised with edge-tts (German neural voices)."""
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
    "naruto":  ("de-DE-FlorianMultilingualNeural", "+10%", "+65Hz"),   # young, cheeky
    "naruto_q": ("de-DE-FlorianMultilingualNeural", "-8%", "+55Hz"),   # quiet, at night
    "sakura":  ("de-DE-AmalaNeural", "+6%", "+25Hz"),
    "sasuke":  ("de-DE-KillianNeural", "-10%", "+30Hz"),
    "iruka":   ("de-DE-ConradNeural", "+4%", "+5Hz"),
    "kakashi": ("de-DE-ConradNeural", "-14%", "-12Hz"),
    "teuchi":  ("de-DE-KillianNeural", "+0%", "-15Hz"),
}

# (id, speaker, global start time in s, text)
LINES = [
    ("intro1", "naruto", 0.15, "POV: Ein Tag als junger Naruto"),
    ("intro2", "naruto", 2.70, "… mit Halbo!"),
    ("s1", "naruto", 6.60, "Heute werde ich wieder besser als alle anderen!"),
    ("s2", "naruto", 14.80, "Hehe. Sieht gut aus!"),
    ("s3a", "iruka", 19.80, "Naruto, nicht zu spät!"),
    ("s3b", "naruto", 21.45, "Jaja, Sensei!"),
    ("s4a", "sakura", 23.60, "Morgen, Naruto!"),
    ("s4b", "naruto", 25.20, "Sasuke, ich schlage dich eines Tages!"),
    ("s4c", "sasuke", 27.90, "Träum weiter."),
    ("s5a", "naruto", 32.30, "Noch eine Portion, bitte!"),
    ("s5b", "teuchi", 34.10, "Kommt sofort!"),
    ("s6a", "kakashi", 39.40, "Yo. Sorry, ich hab mich verlaufen."),
    ("s6b", "naruto", 42.80, "Schon wieder zu spät!"),
    ("s7a", "sakura", 44.60, "Da ist sie!"),
    ("s7b", "naruto", 48.10, "Hab dich!"),
    ("s7c", "naruto", 49.20, "Aua! Aua!"),
    ("s8a", "naruto_q", 52.20, "Eines Tages sehen mich alle."),
    ("s8b", "naruto_q", 54.80, "Ich werde Hokage."),
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
