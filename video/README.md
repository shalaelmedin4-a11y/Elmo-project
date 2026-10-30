# Looksmaxx-Morgenroutine (9:16 Papier-Cutout-Cartoon)

`looksmaxx_morgenroutine.mp4`: 1080×1920, 24 fps (animiert auf 12 fps, "on twos"), ca. 41,2 s. Der Junge erzählt selbst (Stimme eines 14-Jährigen mit Stimmbruch-Kieksern), mit Untertiteln.

Alles wird per Code erzeugt:

| Datei | Inhalt |
|---|---|
| `script_data.py` | Szenen, Texte (TTS-Lautschrift und Untertitel), Pausen, Stellen mit Stimmbruch-Kiekser |
| `narration.py` | Stimme mit Piper-TTS (`de_DE-thorsten-high`), hochgepitcht zum Teenager, an einzelnen Silben kippt sie nach oben weg; schreibt `build/timeline.json` |
| `paper.py` | Papier-Look: gezackte, „boilende“ Kanten, Papierstruktur, Schlagschatten |
| `character.py` | Die Hauptfigur als Sprite (Mütze, Daunenjacke, Gesichtsausdrücke) |
| `render.py` | Die 7 Szenen, Frame für Frame |
| `audio.py` | Musik (Ukulele, Marimba, Bass), Cartoon-Soundeffekte, Ducking unter dem Erzähler, Mix |

Neu bauen: `./build.sh` (braucht ffmpeg mit Rubberband; lädt das Stimmmodell beim ersten Lauf, ca. 110 MB).
