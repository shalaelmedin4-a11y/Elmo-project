# Shot list & generation prompts

Format: **vertical 9:16, 1080×1920, 24 or 30 fps**. Generate each scene as its own
clip (8 s generations are fine – the assembly script trims to the exact length).
Always attach the character reference images and prepend the character block from
[`character.md`](character.md). Do **not** let the model render subtitles or
timestamps – those are added in post (`scripts/assemble.sh`).

Global style suffix (append to every prompt):

> Cinematic realistic style, natural colors, shallow depth of field, mix of
> handheld vlog camera and smooth cinematic close-ups, quick clear cuts every
> 2–4 seconds, vertical 9:16, other soldiers visible in the background slightly
> out of focus, realistic military base, no flags, no insignia, no text.

| # | Time | Clip | Dur. | Light / color |
|---|---|---|---|---|
| 1 | 05:00 | `clips/scene1.mp4` | 0–8 s (8 s) | cold blue, dark → fluorescent on |
| 2 | 06:00 | `clips/scene2.mp4` | 8–15 s (7 s) | orange sunrise, visible breath |
| 3 | 10:00 | `clips/scene3.mp4` | 15–23 s (8 s) | bright neutral daylight, dust |
| 4 | 12:30 | `clips/scene4.mp4` | 23–30 s (7 s) | warm indoor light |
| 5 | 15:00 | `clips/scene5.mp4` | 30–37 s (7 s) | golden afternoon |
| 6 | 21:00 | `clips/scene6.mp4` | 37–45 s (8 s) | dark, small warm lamp |

---

## Scene 1 — 05:00 — "Weckruf" (8 s)

**Prompt**
> [CHARACTER]. Dark military barracks dormitory at 5 a.m., rows of metal bunk
> beds, cold blue moonlight through the windows. A loud whistle, the overhead
> fluorescent lights snap on with a flicker. The soldier throws off his blanket
> and jumps down from the top bunk, landing on the floor in socks, while other
> soldiers around him get up, slightly out of focus. Handheld vlog camera, slight
> shake. Cut to a smooth close-up: his hands pull the grey wool blanket tight
> and fold the corner into a perfect hospital corner, bed made perfectly. Cold
> blue color grade. [STYLE]

**Cuts:** 0–1.5 s darkness + whistle → 1.5–3.5 s lights on, jump down →
3.5–5.5 s others rising (handheld) → 5.5–8 s close-up bed making.
**SFX:** sharp whistle at 0.3 s, fluorescent *clack-hum*, bunk creak, feet on floor.

## Scene 2 — 06:00 — "Antreten & Laufen" (7 s)

**Prompt**
> [CHARACTER]. Outside on a parade ground at sunrise, orange and pink sky, low
> sun behind the barracks. He stands at attention in a formation of soldiers,
> breath visible in the cold air. Cut: the group starts running on a dirt path,
> he runs in the second row, steady rhythm, condensation clouds from his breath,
> sun flare behind him. Tracking shot from the side, then a close-up of his face
> while running. Warm orange rim light, cool shadows. [STYLE]

**Cuts:** 0–2.5 s formation wide → 2.5–5 s group starts running (tracking) →
5–7 s face close-up, breath clouds.
**SFX:** cadence of boots, wind, distant command call.

## Scene 3 — 10:00 — "Hindernisbahn" (8 s)

**Prompt**
> [CHARACTER]. Bright daylight on a dusty military obstacle course. He crawls on
> his elbows under a low camouflage net, dust in the air. Cut: he climbs a tall
> wooden wall, gripping the top edge, an instructor in the blurred background
> shouts and points. Cut: slow-motion shot as he jumps down from the wall,
> dust exploding as his boots hit the ground. Dynamic handheld + one smooth
> slow-motion close-up. Neutral bright daylight, natural colors. [STYLE]

**Cuts:** 0–2.5 s crawl under net (low angle) → 2.5–5 s wall climb, instructor
in BG → 5–8 s slow-motion jump down (ramp speed to 40 %).
**SFX:** heavy breathing, net rustle, instructor shout (unintelligible), thump.

## Scene 4 — 12:30 — "Mittag" (7 s)

**Prompt**
> [CHARACTER]. Busy military mess hall at noon, long tables, many soldiers
> eating and talking in the blurred background. He sits at a table with
> comrades, eating from a compartmented metal tray (potatoes, meat, vegetables).
> A comrade next to him tells a joke, he laughs genuinely, shoulders shaking.
> Warm golden indoor light from large windows. Handheld vlog angle across the
> table, then a close-up of his laugh. [STYLE]

**Cuts:** 0–2.5 s wide mess hall → 2.5–4.5 s tray close-up / fork →
4.5–7 s laugh close-up.
**SFX:** cutlery clatter, crowd murmur, one burst of laughter.

## Scene 5 — 15:00 — "Übung im Gelände" (7 s)

**Prompt**
> [CHARACTER]. Golden afternoon light. He checks and packs his gear on a bench:
> backpack straps, canteen, radio pouch, tightens his boot laces, puts on his
> helmet. Cut: he sits in the back of an open military truck with his squad,
> driving across a bumpy grass field, golden dust in the light. Tense close-up
> of his focused face, jaw set, eyes looking ahead, the truck shaking. Smooth
> cinematic close-up, warm golden grade with slightly cooler shadows. [STYLE]

**Cuts:** 0–2.5 s packing gear (inserts) → 2.5–4.5 s truck driving wide →
4.5–7 s tense face close-up.
**SFX:** buckles, diesel engine rumble, radio chatter (soft), wind.

## Scene 6 — 21:00 — "Feierabend" (8 s)

**Prompt**
> [CHARACTER, uniform jacket off, olive t-shirt]. Dark barracks room at night lit
> only by a small warm desk lamp. In the blurred background other soldiers
> relax: one reads, one looks at his phone, one sleeps. He sits on the edge of
> his bunk and polishes his black boots with a cloth. Cut: he lies in his bunk,
> turns his head and looks directly into the camera with a tired, warm smile.
> Handheld vlog selfie angle for the final shot. Warm lamp light against deep
> blue shadows. [STYLE]

**Cuts:** 0–3 s boot cleaning → 3–5 s room wide with others → 5–8 s bunk,
look into camera, tired smile (hold).
**SFX:** cloth on leather, quiet snoring, soft radio, lamp click at the end
(optional cut to black at 44.6 s).
