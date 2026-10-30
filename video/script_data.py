"""Shot list for "Looksmaxx Morgenroutine" – timing, narration and subtitles.

Each narration segment: (tts_text, subtitle_text, pause_before_seconds).
`tts_text` is spelled phonetically where the German voice would mangle
English words; `subtitle_text` is what appears on screen.
"""

FPS_ANIM = 12      # paper cut-out "on twos" animation rate
FPS_OUT = 24
W, H = 1080, 1920

SCENES = [
    dict(name="alarm", min_dur=5.0, lead=1.6, tail=0.5, segments=[
        ("Sechs Uhr dreißig.", "6:30 Uhr.", 0.0),
        ("Während ihr schlaft, beginnt mein Glou-app.", "Während ihr schlaft,\nbeginnt mein Glow-up.", 0.35),
    ]),
    dict(name="water", min_dur=5.0, lead=0.3, tail=0.4, segments=[
        ("Kaltes Wasser.", "Kaltes Wasser.", 0.0),
        ("Für die Kieferlinie.", "Für die Kieferlinie.", 0.25),
        ("Alles nach Plan.", "… Alles nach Plan.", 2.1),   # freeze + scream happen in this gap
    ]),
    dict(name="cream", min_dur=5.0, lead=0.3, tail=0.5, segments=[
        ("Zwölf Produkte.", "Zwölf Produkte.", 0.0),
        ("Ich weiß nicht, was sie machen.", "Ich weiß nicht,\nwas sie machen.", 0.4),
        ("Aber sie machen es.", "Aber sie machen es.", 0.45),
    ]),
    dict(name="eggs", min_dur=6.0, lead=0.3, tail=0.6, segments=[
        ("Vierzehn Eier.", "Vierzehn Eier.", 0.0),
        ("Protein ist kein Essen.", "Protein ist kein Essen.", 0.45),
        ("Protein ist ein Leifstail.", "Protein ist ein Lifestyle.", 0.35),
    ]),
    dict(name="pushup", min_dur=6.0, lead=0.3, tail=0.6, segments=[
        ("Hundert Liegestütze.", "Hundert Liegestütze.", 0.0),
        ("Ungefähr.", "… Ungefähr.", 2.4),   # one push-up, collapse, awkward silence
    ]),
    dict(name="pose", min_dur=6.0, lead=0.4, tail=0.7, segments=[
        ("Ich sehe", "Ich sehe …", 0.0),
        ("perfekt aus.", "… perfekt aus.", 0.6),
        ("Die anderen haben keine Chance.", "Die anderen\nhaben keine Chance.", 0.4),
    ]),
    dict(name="night", min_dur=7.0, lead=0.4, tail=1.6, segments=[
        ("Zweiundzwanzig Uhr.", "22 Uhr.", 0.0),
        ("Schlaf ist der wahre Luksmäx.", "Schlaf ist der wahre\nLooksmaxx.", 0.4),
        ("Gute Nacht, ihr Normis.", "Gute Nacht,\nihr Normies.", 0.45),
    ]),
]
