# Stimme & Lippensynchronisation

Die Erzählung besteht aus 14 Satzteilen (`cartoon/voice/cue_00.wav` … `cue_13.wav`).
Jeder Satzteil liegt exakt auf seinem Untertitel. Halbos Mund bewegt sich Bild für
Bild mit der Lautstärke der Stimme (`build/lipsync.json`).

**Aktuell:** neuronale KI-Stimme (Microsoft „Florian“, junger Mann, Deutsch),
erzeugt von `cartoon/voice.py`, mit leisen Atemgeräuschen vor einigen Sätzen.
Sie klingt natürlicher als klassisches Text-to-Speech, ist aber keine echte
menschliche Aufnahme.

**Durch eine echte Stimme ersetzen:** jeden Satzteil einzeln aufnehmen (Handy reicht,
ruhiger Raum, 15–20 cm Abstand), als WAV unter dem gleichen Namen speichern und
`RERENDER=1 ./cartoon/build.sh` ausführen. Stille am Anfang/Ende wird automatisch
abgeschnitten; Untertitel-Dauer und Mundbewegung passen sich an.

| Datei | Start | Text | Regie |
|---|---|---|---|
| cue_00 | 0:00.4 | Ein Tag als Soldat … | Intro: weich, jugendlich, euphorisch |
| cue_01 | 0:02.3 | mit Halbo! | strahlend, ein bisschen albern |
| cue_02 | 0:05.0 | Fünf Uhr morgens. | verschlafen |
| cue_03 | 0:07.5 | Hier gibt's keine Snooze-Taste. | trocken-witzig |
| cue_04 | 0:12.8 | Antreten, dann laufen. | sachlich, leicht außer Atem |
| cue_05 | 0:15.8 | Jeden Tag. | resigniert-stolz |
| cue_06 | 0:19.6 | Hindernisbahn! | angestrengt |
| cue_07 | 0:21.6 | Hier merkst du, wer wirklich durchzieht. | „wirklich“ betonen, stolz |
| cue_08 | 0:27.6 | Mittag. | locker |
| cue_09 | 0:29.2 | Die einzige halbe Stunde, in der keiner schreit. | Augenzwinkern |
| cue_10 | 0:34.6 | Nachmittags Übung im Gelände. | ruhiger, fokussiert |
| cue_11 | 0:37.6 | Und dann wird's ernst. | leise, tief |
| cue_12 | 0:41.6 | Morgen wieder um fünf. | müde, warm |
| cue_13 | 0:44.4 | Folg mir für Tag zwei! | direkt an die Zuschauer, Lächeln |

Startzeiten ändern: `CUES` in `cartoon/voice.py`.
