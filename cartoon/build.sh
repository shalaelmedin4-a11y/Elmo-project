#!/usr/bin/env bash
# Builds the paper cut-out cartoon video (4 s intro + 45 s story = 49 s).
#   ./cartoon/build.sh            -> renders frames + sound, muxes
# If voice recordings exist (cartoon/voice/vo0.wav … vo6.wav) they are placed at
# the subtitle times, normalised to -14 LUFS, and the music/SFX bed is ducked
# underneath so the voice is always clearly louder.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build output
[[ -f build/cartoon_video.mp4 && "${RERENDER:-0}" != 1 ]] || python3 cartoon/render.py build/cartoon_video.mp4
python3 cartoon/audio.py build/cartoon_bed.wav

# vo0 = intro line, vo1..vo6 = scenes (subtitle start + 4 s intro)
VO_START=(0.35 5.0 12.8 19.6 27.6 34.6 41.6)
LEN=49
have_vo=1
for i in 0 1 2 3 4 5 6; do [[ -f cartoon/voice/vo$i.wav ]] || have_vo=0; done

if (( have_vo )); then
  OUT=output/ein_tag_soldat_cartoon.mp4
  in=(-i build/cartoon_video.mp4 -i build/cartoon_bed.wav); fc=""
  for i in 0 1 2 3 4 5 6; do
    in+=(-i cartoon/voice/vo$i.wav)
    ms=$(awk "BEGIN{print int(${VO_START[$i]}*1000)}")
    fc+="[$((i+2)):a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=${ms}|${ms}[v$i];"
  done
  fc+="[v0][v1][v2][v3][v4][v5][v6]amix=inputs=7:normalize=0,apad,atrim=0:$LEN,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,asplit[vo][key];"
  fc+="[1:a]aformat=sample_rates=48000:channel_layouts=stereo[bed0];[bed0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[bed];"
  fc+="[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89,apad,atrim=0:$LEN[a]"
  ffmpeg -y -v error "${in[@]}" -filter_complex "$fc" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t $LEN "$OUT"
else
  OUT=output/ein_tag_soldat_cartoon_ohne_stimme.mp4
  ffmpeg -y -v error -i build/cartoon_video.mp4 -i build/cartoon_bed.wav -map 0:v -map 1:a -c:v copy \
    -af "volume=4dB,alimiter=limit=0.89" -c:a aac -b:a 192k -movflags +faststart -t $LEN "$OUT"
  echo "(no voice files in cartoon/voice/ - built the version without narration)"
fi
echo "✔ $OUT"
