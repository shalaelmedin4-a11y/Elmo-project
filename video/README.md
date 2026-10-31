# Looksmaxx-Morgenroutine (9:16 Papier-Cutout-Cartoon)

`looksmaxx_morgenroutine.mp4`: 1080×1920, 24 fps (animiert auf 12 fps, "on twos"), ca. 43 s. Der Junge erzählt selbst, wie in einem lockeren Handyvideo: Atmer, kleine Lacher, Schrei, Stimmbruch-Kiekser. Mit Untertiteln.

Alles wird per Code erzeugt:

| Datei | Inhalt |
|---|---|
| `script_data.py` | Szenen, Texte (TTS-Lautschrift und Untertitel), Pausen, Stellen mit Stimmbruch-Kiekser |
| `narration.py` | Stimme mit dem neuronalen Sprachmodell Chatterbox (Deutsch, ausdrucksstark), geklont auf `voice_ref.wav` (Teenager-Klangfarbe). Pro Zeile bis zu 6 Takes; Whisper hört mit, wählt den saubersten und schneidet Nachgeplapper ab. Dazu Atmer, Lacher, Schrei, Kiekser; schreibt `build/timeline.json` |
| `paper.py` | Papier-Look: gezackte, „boilende“ Kanten, Papierstruktur, Schlagschatten |
| `character.py` | Die Hauptfigur als Sprite (Mütze, Daunenjacke, Gesichtsausdrücke) |
| `render.py` | Die 7 Szenen, Frame für Frame |
| `audio.py` | Musik (Ukulele, Marimba, Bass), Cartoon-Soundeffekte, Ducking unter dem Erzähler, Mix |

Neu bauen: `./build.sh` (braucht ffmpeg mit Rubberband; lädt beim ersten Lauf die Modelle herunter. Die Sprachaufnahmen dauern auf CPU ca. 20–30 Minuten und werden in `build/takes/` zwischengespeichert).
