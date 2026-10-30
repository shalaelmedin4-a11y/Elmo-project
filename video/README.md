# Looksmaxx-Morgenroutine (9:16 Papier-Cutout-Cartoon)

`looksmaxx_morgenroutine.mp4`: 1080×1920, 24 fps (animiert auf 12 fps, "on twos"), ca. 41,6 s, deutscher Erzähler mit Untertiteln.

Alles wird per Code erzeugt:

| Datei | Inhalt |
|---|---|
| `script_data.py` | Szenen, Erzählertexte (TTS-Lautschrift und Untertitel), Pausen |
| `narration.py` | Erzähler mit Piper-TTS (Stimme `de_DE-thorsten-high`), tiefer gepitcht, mit Kompressor und leichtem Hall; schreibt `build/timeline.json` |
| `paper.py` | Papier-Look: gezackte, „boilende“ Kanten, Papierstruktur, Schlagschatten |
| `character.py` | Die Hauptfigur als Sprite (Mütze, Daunenjacke, Gesichtsausdrücke) |
| `render.py` | Die 7 Szenen, Frame für Frame |
| `audio.py` | Musik (Ukulele, Marimba, Bass), Cartoon-Soundeffekte, Ducking unter dem Erzähler, Mix |

Neu bauen: `./build.sh` (braucht ffmpeg mit Rubberband; lädt das Stimmmodell beim ersten Lauf, ca. 110 MB).
