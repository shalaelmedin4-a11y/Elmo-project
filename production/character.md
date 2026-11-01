# Character Bible – "Der Soldat"

Paste this **identical** block into every scene prompt (or use it once to create a
character reference image, then attach that image to every scene generation).

## Character reference prompt (English, for the video model)

> A young male soldier, about 21 years old, short brown buzz cut, light stubble,
> green-brown eyes, athletic build, clean natural skin with slight realistic
> texture, wearing a green woodland camouflage uniform with sleeves rolled up to
> the elbows, plain olive t-shirt underneath, no flags, no patches, no unit
> insignia, no name tape, no text on clothing. Same face, same hair, same uniform
> in every shot.

## Character reference image (generate first, reuse everywhere)

> Photorealistic portrait, vertical 9:16, of [character reference prompt above],
> neutral expression with a slight confident half-smile, soft overcast daylight,
> plain blurred military base background, 85mm lens, shallow depth of field,
> natural colors, ultra-detailed skin, no text, no logos.

Generate 3–4 variants (front, 3/4 left, 3/4 right, full body) and keep the best
set as `production/ref/soldier_front.png`, `soldier_34.png`, `soldier_full.png`.
Use them as *image reference / character reference / ingredients* in
Veo, Sora, Kling, Runway or Hailuo for **all six scenes**.

## Continuity rules

| Item | Locked value |
|---|---|
| Age | ~21 |
| Hair | short brown buzz cut (never longer, never helmet-hair except helmet in scene 5) |
| Face | light stubble, green-brown eyes |
| Uniform | green camo, sleeves rolled up, no insignia/flags/text |
| Body | athletic, not bulky |
| Scene 6 | same uniform trousers + olive t-shirt (jacket off is OK) |

## Background soldiers

Always present, slightly out of focus (shallow DOF), generic faces, same camo
pattern, no insignia. They walk, talk, train, eat – the base must feel busy.

## Negative prompt (use everywhere the tool supports it)

> different face, face morphing, changing hairstyle, long hair, helmet hair,
> flags, national flags, patches, unit insignia, logos, readable text, watermark,
> subtitles baked into video, extra fingers, deformed hands, weapons pointed at
> camera, gore, blood, cartoon, CGI look, oversaturated, plastic skin,
> horizontal framing, letterboxing
