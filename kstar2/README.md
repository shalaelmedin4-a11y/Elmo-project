# Ein Tag als K-Pop-Star – Version 2 (Papier-Cutout, ~60 s, 9:16)

Fiktive Figuren und Firma. **Feste Bildaufteilung:** Halbo immer exakt in der
Mitte, von den Knien aufwärts, ca. zwei Drittel der Bildhöhe, in jeder Szene
gleich groß (`X0, FEET, SC` in `k2cast.py`). Einfarbige Hintergründe mit 1–2
großen Objekten, höchstens 1–2 kleine Nebenfiguren am Rand.
**Kein Text** außer dem Uhr-Schild oben links.

| Datei | Inhalt |
|---|---|
| `k2voice.py` | 19 kurze Sätze, langsam & deutlich (KI-Stimme „Seraphina“), Pause nach jedem Satz; erzeugt die Timeline |
| `k2cast.py` | große Halbo-Figur: große Augen (Blinzeln, Blickrichtung, Brauen), Arme mit Ellbogen (IK) für Gesten |
| `k2scenes.py` | 9 Szenen, je eine klare Handlung |
| `k2render.py` | Rendering (12 fps Stop-Motion), Lippensync, Uhr oben links |
| `k2audio.py` | sehr leise Pop-Musik (hell bei Fans/Konzert, langsam in grauen Szenen), fast keine Effekte |
| `build.sh` | alles bauen → `output/ein_tag_als_kpop_star_v2.mp4` |

Eigene Stimme: Sätze als `kstar2/voice/cue_XX.wav` ablegen, dann `RERENDER=1 ./kstar2/build.sh`.
