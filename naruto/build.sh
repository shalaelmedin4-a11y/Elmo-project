#!/usr/bin/env bash
# POV: Ein Tag als junger Naruto – voices -> music/sfx -> frames -> MP4
set -euo pipefail
cd "$(dirname "$0")"
pip install -q pillow numpy edge-tts
python3 voices.py
python3 audio.py
rm -rf build/frames
python3 render.py
ffmpeg -y -loglevel error -framerate 12 -i build/frames/%05d.png -i build/audio.wav \
  -vf "fps=24,format=yuv420p" -c:v libx264 -preset slow -crf 24 -profile:v high -tune grain \
  -c:a aac -b:a 192k -ar 44100 -movflags +faststart -shortest pov_ein_tag_als_junger_naruto.mp4
echo "fertig: naruto/pov_ein_tag_als_junger_naruto.mp4"
