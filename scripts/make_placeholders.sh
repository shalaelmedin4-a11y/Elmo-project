#!/usr/bin/env bash
# Creates dummy clips + audio so assemble.sh can be dry-run before the real
# AI-generated footage and voice recordings exist. Does NOT overwrite real files.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p clips audio
colors=(0x10204a 0xd9822b 0xc8c8b4 0xb5793a 0xd8a03c 0x1a1a2e)
for i in 0 1 2 3 4 5; do
  n=$((i+1))
  [[ -f clips/scene$n.mp4 ]] || ffmpeg -y -v error -f lavfi -i "color=c=${colors[$i]}:s=720x1280:d=8:r=24" \
    -vf "drawtext=text='SCENE $n':fontsize=90:fontcolor=white:x=(w-tw)/2:y=(h-th)/2" clips/scene$n.mp4
  [[ -f audio/vo$n.wav ]] || ffmpeg -y -v error -f lavfi -i "sine=f=$((180+n*20)):d=3.5" -af "volume=0.5" audio/vo$n.wav
done
[[ -f audio/ambience.wav ]] || ffmpeg -y -v error -f lavfi -i "anoisesrc=c=brown:a=0.3:d=10" audio/ambience.wav
[[ -f audio/music.wav ]]    || ffmpeg -y -v error -f lavfi -i "sine=f=55:d=45" audio/music.wav
echo "placeholders ready"
