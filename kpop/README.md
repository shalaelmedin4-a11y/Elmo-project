# Ein Tag als K-Pop Trainee … mit Halbo! (Papier-Cutout, ~52 s, 9:16)

Fiktive Figuren, fiktive Firma, keine echten Künstler, Gruppen oder Logos.

| Datei | Inhalt |
|---|---|
| `kcast.py` | Halbo (blonde Fluffy-Haare, Oversize-Hoodie, weiße Sneaker), andere Trainees, Manager mit Sonnenbrille & Klemmbrett, Jury, Fans, Bühne, Tanzstudio, Schlafsaal |
| `kscenes.py` | Intro + 6 Szenen + Outro, Timeline, Farb-"Look" je Szene (Bühne = pink/glitzernd, hinter den Kulissen = grau/kalt) |
| `krender.py` | Rendering (12 fps Stop-Motion), Uhr-Schild, Untertitel, Lippensync |
| `kvoice.py` | Erzählerin: 23 Satzteile (`voice/cue_XX.wav`), KI-Stimme „Seraphina“ für fehlende Cues; setzt Cues lückenlos ohne Überlappung |
| `kaudio.py` | K-Pop-artige Musik (hell & voll auf der Bühne, gedämpft/langsam/leise dahinter), Metronom, Sneaker, Kamera-Klicks, Handy-Vibration … |
| `build.sh` | alles bauen → `output/ein_tag_als_kpop_trainee_mit_halbo.mp4` |

Eigene Stimme: Satzteile mit gleichem Namen als `kpop/voice/cue_XX.wav` ablegen
(Texte stehen in `CUES` in `kvoice.py`), dann `RERENDER=1 ./kpop/build.sh`.
