# Ein Tag als K-Pop-Star … mit Halbo! (Papier-Cutout, ~52 s, 9:16)

Fiktive Figuren, fiktive Firma, keine echten Künstler, Gruppen oder Logos.
**Keine Untertitel, kein Text im Bild** – außer den Intro-Schildern (einzeln
nacheinander) und dem kleinen Uhr-Schild; nie zwei Texte gleichzeitig. Die
„große rote Zahl“ auf dem Vertrag ist aus gezeichneten Nullen, die Hasskommentare
sind Symbole (wütendes Gesicht, X, Gekritzel, Blitz, durchgestrichenes Herz).

| Datei | Inhalt |
|---|---|
| `ksvoice.py` | Erzählerin (13 Satzteile, `voice/cue_XX.wav`), ruhiges Tempo; erzeugt die Timeline (Szenen werden länger, wenn der Text mehr Platz braucht) |
| `kscast.py` | Halbo (lange pinke Haare, silberne Glitzerjacke / schwarzer Hoodie), Symbole ohne Schrift |
| `ksscenes.py` | Intro + 6 Szenen + Outro, Halbo immer groß in der Mitte |
| `ksrender.py` | Rendering (12 fps Stop-Motion), Lippensync, Uhr-Schild |
| `ksaudio.py` | leise Pop-Musik (hell auf der Bühne, langsam & leise im Dunkeln), leise Geräusche |
| `build.sh` | alles bauen → `output/ein_tag_als_kpop_star_mit_halbo.mp4` |

Eigene Stimme: Satzteile als `kstar/voice/cue_XX.wav` (Texte in `ksvoice.py`)
ablegen, dann `RERENDER=1 ./kstar/build.sh`.
