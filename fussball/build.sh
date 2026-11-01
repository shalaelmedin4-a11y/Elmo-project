#!/usr/bin/env bash
# Builds "Ein Tag als Profifußballer … mit Halbo!" (~55 s, 9:16, clean anime-style look).
#   ./fussball/build.sh                (RERENDER=1 to redraw the picture)
# 1. fussball/fb_voice.py  -> narration (fussball/voice/cue_XX.wav, neural voice for missing cues) + lip-sync
# 2. fussball/fb_render.py -> animation (lip-synced mouth, clock sign; no subtitles)
# 3. fussball/fb_audio.py  -> music + SFX
# 4. mix: voice at -14 LUFS, music+sounds 6 dB lower than generated and ducked under the voice
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build output
OUT=output/ein_tag_als_profifussballer_mit_halbo.mp4

python3 fussball/fb_voice.py
LEN=$(python3 -c "import json;print(json.load(open('build/fb_timeline.json'))['dur'])")
if [[ ! -f build/fb_video.mp4 || "${RERENDER:-0}" == 1 ]]; then
  python3 fussball/fb_render.py build/fb_video.mp4
fi
python3 fussball/fb_audio.py build/fb_bed.wav

VI=$(ffmpeg -hide_banner -i build/fb_voice_track.wav -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
VGAIN=$(awk "BEGIN{print -14 - ($VI)}")
echo "voice ${VI} LUFS -> gain ${VGAIN} dB"

ffmpeg -y -v error -i build/fb_video.mp4 -i build/fb_bed.wav -i build/fb_voice_track.wav -filter_complex "\
[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${VGAIN}dB,asplit[vo][key];\
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-6dB[bed0];\
[bed0][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[bed];\
[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89,apad,atrim=0:$LEN[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $LEN "$OUT"
echo "✔ $OUT"
