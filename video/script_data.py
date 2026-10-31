"""Shot list for "Looksmaxx Morgenroutine" – timing, narration and subtitles.

The boy narrates himself, like a 14-year-old filming a casual video.
Each narration segment is a dict:
  tts    text spoken (natural spelling; the voice model handles English words)
  sub    subtitle shown on screen
  pause  silence before the line (seconds)
  ex     expressiveness 0.25 (flat, tired) … 1.0 (very excited)
  pre    "breath" – audible inhale right before the line
  post   "laugh" – small giggle after the line (not subtitled)
  crack  word that breaks up into a voice crack
"""

FPS_ANIM = 12      # paper cut-out "on twos" animation rate
FPS_OUT = 24
W, H = 1080, 1920


def L(tts, sub=None, pause=0.0, ex=0.6, pre=None, post=None, crack=None):
    return dict(tts=tts, sub=sub or tts, pause=pause, ex=ex, pre=pre, post=post, crack=crack)


SCENES = [
    dict(name="alarm", min_dur=5.0, lead=1.6, tail=0.4, segments=[
        L("Sechs Uhr dreißig.", "6:30 Uhr.", ex=0.55, pre="breath"),
        L("Während ihr schlaft, beginnt mein Glow-up.", "Während ihr schlaft,\nbeginnt mein Glow-up.",
          pause=0.4, ex=0.75, post="laugh", crack="Glow"),
    ]),
    # scream happens between line 2 and 3 (see narration.py)
    dict(name="water", min_dur=5.0, lead=0.3, tail=0.4, segments=[
        L("Kaltes Wasser.", ex=0.6),
        L("Für die Kieferlinie.", pause=0.3, ex=0.7),
        L("... Alles nach Plan.", "… Alles nach Plan.", pause=0.35, ex=0.35, pre="breath"),
    ]),
    dict(name="cream", min_dur=5.0, lead=0.3, tail=0.4, segments=[
        L("Zwölf Produkte.", ex=0.7),
        L("Ich weiß nicht, was sie machen.", "Ich weiß nicht,\nwas sie machen.", pause=0.45, ex=0.5, post="laugh"),
        L("Aber sie machen es.", pause=0.35, ex=0.8),
    ]),
    dict(name="eggs", min_dur=6.0, lead=0.3, tail=0.5, segments=[
        L("Vierzehn Eier.", ex=0.6),
        L("Protein ist kein Essen.", pause=0.45, ex=0.7, pre="breath"),
        L("Protein ist ein Lifestyle.", pause=0.4, ex=0.85),
    ]),
    # one push-up, collapse, awkward silence, then line 2
    dict(name="pushup", min_dur=6.0, lead=0.3, tail=0.6, segments=[
        L("Hundert Liegestütze.", ex=0.85, pre="breath"),
        L("... Ungefähr.", "… Ungefähr.", pause=2.3, ex=0.3, pre="breath", crack="Ungefähr"),
    ]),
    dict(name="pose", min_dur=6.0, lead=0.4, tail=0.6, segments=[
        L("Ich sehe ...", "Ich sehe …", ex=0.6, pre="breath"),
        L("perfekt aus.", "… perfekt aus.", pause=0.6, ex=0.85),
        L("Die anderen haben keine Chance.", "Die anderen\nhaben keine Chance.", pause=0.35, ex=0.9,
          post="laugh", crack="Chance"),
    ]),
    dict(name="night", min_dur=7.0, lead=0.4, tail=1.5, segments=[
        L("Zweiundzwanzig Uhr.", "22 Uhr.", ex=0.4),
        L("Schlaf ist der wahre Looksmaxx.", "Schlaf ist der wahre\nLooksmaxx.", pause=0.4, ex=0.55),
        L("Gute Nacht, ihr Normies.", "Gute Nacht,\nihr Normies.", pause=0.45, ex=0.65, post="laugh"),
    ]),
]

SCREAM = L("Aaaaaah! Kalt! Kalt, kalt, kalt!", ex=1.0)
LAUGH = L("Hehe.", ex=0.7)
