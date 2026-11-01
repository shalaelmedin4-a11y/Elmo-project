# Ein Tag als Profifußballer … mit Halbo! (~55 s, 9:16)

Eigener, sauberer Anime-Look per Code (kein Papier-Stil): klare Linien,
Zwei-Ton-Schattierung, weiches warmes Licht, leicht entsättigt. Halbo:
dunkelblonde kurze Haare, grüne Augen, gelb-schwarzes Trikot Nr. 3 ohne Logo.
Fiktiver Verein, keine echten Logos.

| Datei | Inhalt |
|---|---|
| `fb_rig.py` | Figur: Front- und Seitenansicht, Gelenk-Skelett (Laufen, Flanke, Schuss), Anime-Gesicht, Lippensync |
| `fb_scenes.py` | Intro + 8 Szenen mit je 2–3 Perspektiven (Nah, Halbtotale, Seite, Drohne), Zeitlupe beim Tor |
| `fb_render.py` | Rendering (12 Zeichnungen/s, Ausgabe 24 fps), Licht/Bloom/Vignette, Uhrzeit-Einblendung |
| `fb_voice.py` | Halbos kurze Sätze (KI-Stimme „Florian“), Timeline |
| `fb_audio.py` | leiser Lo-Fi-Beat + Geräusche (Wecker, Pfiff, Ball, Stadion, Torjubel, Eisbad …) |
| `build.sh` | alles bauen → `output/ein_tag_als_profifussballer_mit_halbo.mp4` |
