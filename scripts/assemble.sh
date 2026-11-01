#!/usr/bin/env bash
# Assemble the 45 s vertical TikTok video from 6 generated clips + voice lines.
#
#   clips/scene1.mp4 … scene6.mp4   (any resolution/fps – cropped to 9:16)
#   audio/vo1.wav … vo6.wav          (German voice lines, one per scene)
#   audio/ambience.wav  (optional)   boots, wind, voices, radio – looped
#   audio/music.wav     (optional)   slowly building tension track
#
# Output: output/soldier_day_de.mp4  (1080x1920, 30 fps, H.264 + AAC, ~45 s)
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=${OUT:-output/soldier_day_de.mp4}
FONT=${FONT:-$(fc-match -f '%{file}' 'Inter:style=Bold' 2>/dev/null || true)}
DUR=(8 7 8 7 7 8)                       # scene lengths (sum = 45)
STAMP=(05:00 06:00 10:00 12:30 15:00 21:00)
VO_START=(1.6 9.0 16.0 24.0 31.0 38.0)  # must match production/subtitles_de.ass
TOTAL=45
AMB_VOL=${AMB_VOL:-0.18}               # background ambience level
MUSIC_VOL=${MUSIC_VOL:-0.14}           # tension music level

mkdir -p "$(dirname "$OUT")" build
for i in 1 2 3 4 5 6; do
  [[ -f clips/scene$i.mp4 ]] || { echo "missing clips/scene$i.mp4" >&2; exit 1; }
  [[ -f audio/vo$i.wav ]]    || { echo "missing audio/vo$i.wav" >&2; exit 1; }
done

# 1) Normalise every clip: 9:16 crop, 30 fps, exact length, timestamp overlay.
for i in 0 1 2 3 4 5; do
  n=$((i+1)); d=${DUR[$i]}
  printf '%s' "${STAMP[$i]}" > build/stamp$n.txt   # textfile avoids ':' escaping
  ffmpeg -y -v error -i clips/scene$n.mp4 -an -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,\
fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=$d,trim=duration=$d,setpts=PTS-STARTPTS,\
fade=t=in:st=0:d=0.12,\
drawtext=fontfile='$FONT':textfile=build/stamp$n.txt:x=w-tw-70:y=110:fontsize=44:\
fontcolor=white:box=1:boxcolor=black@0.35:boxborderw=14[v]" \
    -map "[v]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p build/s$n.mp4
done
printf "file '%s'\n" s1.mp4 s2.mp4 s3.mp4 s4.mp4 s5.mp4 s6.mp4 > build/list.txt
ffmpeg -y -v error -f concat -safe 0 -i build/list.txt -c copy build/video.mp4

# 2) Audio: voice lines placed at their offsets, bed ducked under the voice.
inputs=(); vo_chain=""; k=0
for i in 0 1 2 3 4 5; do
  inputs+=(-i audio/vo$((i+1)).wav)
  ms=$(awk "BEGIN{print int(${VO_START[$i]}*1000)}")
  vo_chain+="[$k:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=${ms}|${ms}[v$k];"
  k=$((k+1))
done
vo_chain+="[v0][v1][v2][v3][v4][v5]amix=inputs=6:normalize=0,apad,atrim=0:$TOTAL,\
loudnorm=I=-14:TP=-1.5:LRA=7,asplit=2[vo][key];"

bed=""; bedins=()
if [[ -f audio/ambience.wav ]]; then
  inputs+=(-stream_loop -1 -i audio/ambience.wav)
  bed+="[$k:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:$TOTAL,volume=$AMB_VOL[amb];"
  bedins+=("[amb]"); k=$((k+1))
fi
if [[ -f audio/music.wav ]]; then
  inputs+=(-i audio/music.wav)
  # slow build: starts at 35 % of level, reaches full level by scene 5, fades out at the end
  bed+="[$k:a]aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:$TOTAL,\
volume='$MUSIC_VOL*(0.35+0.65*min(t/32\,1))':eval=frame,afade=t=out:st=43:d=2[mus];"
  bedins+=("[mus]"); k=$((k+1))
fi

if (( ${#bedins[@]} )); then
  nb=${#bedins[@]}
  bed+="$(IFS=; echo "${bedins[*]}")amix=inputs=$nb:normalize=0[bedraw];\
[bedraw][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[bed];\
[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.89,aresample=48000,apad,atrim=0:$TOTAL[a]"
else
  bed+="[key]anullsink;[vo]alimiter=limit=0.89,aresample=48000,apad,atrim=0:$TOTAL[a]"
fi

ffmpeg -y -v error "${inputs[@]}" -filter_complex "$vo_chain$bed" \
  -map "[a]" -c:a pcm_s16le build/audio.wav

# 3) Burn bold white subtitles (middle-lower) and mux.
ffmpeg -y -v error -i build/video.mp4 -i build/audio.wav \
  -vf "ass=production/subtitles_de.ass" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart -t $TOTAL "$OUT"

echo "✔ $OUT"; ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
