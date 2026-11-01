# Elmo-project – „Ein Tag im Leben eines Soldaten“ (TikTok, 9:16, 45 s)

Production kit for a vertical, cinematic-realistic vlog video narrated in German.

```
production/character.md     locked character bible + reference-image prompt + negative prompt
production/scenes.md        6 scene prompts, cut timings, light/color, SFX per scene
production/voiceover_de.md  German VO lines with start times and delivery direction
production/subtitles_de.ass bold white subtitles, middle-lower, timed to the VO
production/subtitles_de.srt same subtitles as SRT (for CapCut / TikTok editor)
scripts/assemble.sh         builds the final 1080x1920 MP4 (crop, timestamps, subs, mix)
scripts/make_placeholders.sh dummy clips/audio for a dry run
```

## Workflow

1. **Character first** – generate the reference images from `production/character.md`
   and attach them to *every* scene generation (keeps the face/uniform identical).
2. **Generate 6 clips** (Veo / Sora / Kling / Runway …) with the prompts in
   `production/scenes.md` → save as `clips/scene1.mp4` … `clips/scene6.mp4`.
   No subtitles or timestamps in the generation – they are added in post.
3. **Record / generate the voice** per `production/voiceover_de.md`
   → `audio/vo1.wav` … `audio/vo6.wav`.
4. Optional: `audio/ambience.wav` (boots, wind, voices, radio) and
   `audio/music.wav` (subtle building tension, ≥45 s).
5. Run `./scripts/assemble.sh` → `output/soldier_day_de.mp4`.

The script crops to 9:16, trims each scene to its slot (8/7/8/7/7/8 s), adds the
time stamp (05:00 … 21:00) in the top corner, burns in the subtitles, normalises
the voice to −14 LUFS and ducks ambience/music under it so the voice is always
clearly louder. Levels: `AMB_VOL=0.18 MUSIC_VOL=0.14 ./scripts/assemble.sh`.

Dry run without real material: `./scripts/make_placeholders.sh && ./scripts/assemble.sh`.
Needs `ffmpeg` with libass + freetype.
