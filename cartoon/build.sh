#!/usr/bin/env bash
# Builds the paper cut-out cartoon video (4 s intro + 45 s story = 49 s).
#
#   ./cartoon/build.sh
#
# 1. cartoon/voice.py  -> narration track + lip-sync data (uses cartoon/voice/cue_XX.wav;
#                         missing cues are generated with a neural German voice)
# 2. cartoon/render.py -> animation with lip-synced mouth + subtitles
# 3. cartoon/audio.py  -> music, ambience, SFX
# 4. mix: voice at -14 LUFS, bed ducked underneath so the voice is always clearly louder
#
# Re-render the picture after changing scenes or voice timing: RERENDER=1 ./cartoon/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build output
LEN=49
OUT=output/ein_tag_als_soldat_mit_halbo.mp4

python3 cartoon/voice.py
if [[ ! -f build/cartoon_video.mp4 || "${RERENDER:-0}" == 1 ]]; then
  python3 cartoon/render.py build/cartoon_video.mp4
fi
python3 cartoon/audio.py build/cartoon_bed.wav

# static gain so the speech sits at -14 LUFS (no pumping in the pauses)
VI=$(ffmpeg -hide_banner -i build/voice_track.wav -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
VGAIN=$(awk "BEGIN{print -14 - ($VI)}")
echo "voice ${VI} LUFS -> gain ${VGAIN} dB"

ffmpeg -y -v error -i build/cartoon_video.mp4 -i build/cartoon_bed.wav -i build/voice_track.wav -filter_complex "\
[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${VGAIN}dB,asplit[vo][key];\
[1:a]aformat=sample_rates=48000:channel_layouts=stereo[bed0];\
[bed0][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[bed];\
[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89,apad,atrim=0:$LEN[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $LEN "$OUT"
echo "✔ $OUT"
