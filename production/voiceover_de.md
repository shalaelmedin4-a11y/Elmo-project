# Voice-over (Deutsch) – Ich-Erzähler

**Stimme:** junger Mann, ~21, natürlich, warm, entspannt, ein bisschen stolz.
Wie ein echter Vlog: echtes Atmen, kleine Pausen, variierte Betonung, kein
Vorlese-Ton. Nah am Mikro aufgenommen (oder mit einer sehr natürlichen
Stimme in ElevenLabs/Similar: *Stability ~35 %, Similarity ~75 %, Style ~40 %*,
Sprache Deutsch).

Exportiere jede Zeile als eigene Datei – das Assembly-Script legt sie exakt an
die richtige Stelle:

| Datei | Start | Text | Regie |
|---|---|---|---|
| `audio/vo1.wav` | 1.6 s | Fünf Uhr morgens. … Hier gibt's keine Snooze-Taste. | noch etwas verschlafen, Grinsen hörbar bei „Snooze-Taste" |
| `audio/vo2.wav` | 9.0 s | Antreten, dann laufen. Jeden Tag. … Egal, wie kalt es ist. | leicht außer Atem, Stolz in „Jeden Tag" |
| `audio/vo3.wav` | 16.0 s | Hindernisbahn. … Hier merkst du, wer wirklich durchzieht. | angestrengt, Atmer vor „Hier", Betonung auf „wirklich" |
| `audio/vo4.wav` | 24.0 s | Mittag. Die einzige halbe Stunde, in der keiner schreit. | locker, lachend, Augenzwinkern |
| `audio/vo5.wav` | 31.0 s | Nachmittags Übung im Gelände. … Und dann wird's ernst. | ruhiger, fokussiert, „ernst" tief und leise |
| `audio/vo6.wav` | 38.0 s | Morgen wieder um fünf. … Folg mir, wenn du sehen willst, was morgen passiert. | müde, warm, leises Lächeln, letzter Satz direkt an den Zuschauer |

`…` = kurze natürliche Pause (~0,3–0,5 s), einmal hörbar einatmen.

Jede Zeile muss in ihr Fenster passen (max. Länge): vo1 5.5 s, vo2 5.5 s,
vo3 6.5 s, vo4 5.5 s, vo5 5.5 s, vo6 6.8 s.

Die Stimme wird im Mix automatisch auf ~-14 LUFS gebracht und Ambience + Musik
werden unter der Stimme abgesenkt (Sidechain-Ducking) → Stimme immer klar lauter.
