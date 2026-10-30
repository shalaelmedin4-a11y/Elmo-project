# Messis unmögliches Tor – Quellprojekt

Fertiges Video: `../messi_unmoegliches_tor.mp4` (1080×1920, 30 fps, 69 s).

- `vo/script.txt`: Sprechertext je Szene (Stimme: Piper TTS `de_DE-thorsten-high`)
- `index.html`: Three.js-Szene und Text-Overlays, deterministisch über `renderAt(t)`
- `render.js`: Playwright rendert die Einzelbilder (`node render.js video frames <start> <ende>`)
- `audio.py`: erzeugt Musik und Sounds und mischt die Stimme (`mix.wav`)
- `go.sh`: rendert parallel in 4 Abschnitten

Ablauf: `npm i`, Stimme je Szene nach `vo/<id>.wav` erzeugen, `vo/dur.json` schreiben,
`python3 -m http.server 8765` starten, `bash go.sh`, `python3 audio.py`,
dann die Einzelbilder und `mix.wav` mit ffmpeg zusammenführen (loudnorm I=-14).
