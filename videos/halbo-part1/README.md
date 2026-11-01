# Halbo – Part 1

Video: `../halbo_part1.mp4` (1080×1920, 30 fps, 62 s).

- `scene.html` – Three.js-Szene (Klassenzimmer, Straße, Unfall, Tagtraum am Meer), alle Kameraeinstellungen und Abläufe über `renderAt(t)`
- `person.js` – Figuren: Mixamo-Skelett (`../messi-unmoegliches-tor/models/Xbot.glb`) mit modellierten Körperteilen, Gesicht, Haaren, Kleidung und Konturlinien
- `audio.py` – Stimmen, Klassengemurmel, Uhrticken, Straße, Crash, Schritte, Herzschlag; schreibt auch `lips.json` (Mundbewegung)
- `vo/` – verwendete Sprachaufnahmen (Chatterbox Multilingual; Stimmvorlagen: Thorsten-Voice CC0, Piper „kerstin“)
- `render.js` / `go.sh` – Einzelbilder rendern und mit Ton zum MP4 zusammenführen

Zeitplan der Sätze: `timeline.json`.
