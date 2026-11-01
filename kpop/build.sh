#!/usr/bin/env bash
# Builds "Ein Tag als K-Pop Trainee … mit Halbo!" (~52 s, 9:16).
#   ./kpop/build.sh                (RERENDER=1 to redraw the picture)
# 1. kpop/kvoice.py  -> narration (kpop/voice/cue_XX.wav, neural voice for missing cues) + lip-sync
# 2. kpop/krender.py -> animation (lip-synced mouth, clock signs, subtitles)
# 3. kpop/kaudio.py  -> music + SFX
# 4. mix: voice at -14 LUFS, music/SFX 5 dB lower than generated and ducked under the voice
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build output
LEN=52
OUT=output/ein_tag_als_kpop_trainee_mit_halbo.mp4

python3 kpop/kvoice.py
if [[ ! -f build/kpop_video.mp4 || "${RERENDER:-0}" == 1 ]]; then
  python3 kpop/krender.py build/kpop_video.mp4
fi
python3 kpop/kaudio.py build/kpop_bed.wav

VI=$(ffmpeg -hide_banner -i build/k_voice_track.wav -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
VGAIN=$(awk "BEGIN{print -14 - ($VI)}")
echo "voice ${VI} LUFS -> gain ${VGAIN} dB"

ffmpeg -y -v error -i build/kpop_video.mp4 -i build/kpop_bed.wav -i build/k_voice_track.wav -filter_complex "\
[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${VGAIN}dB,asplit[vo][key];\
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-5dB[bed0];\
[bed0][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[bed];\
[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89,apad,atrim=0:$LEN[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $LEN "$OUT"
echo "✔ $OUT"
