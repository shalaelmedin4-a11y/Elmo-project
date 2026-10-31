#!/usr/bin/env bash
# Build the full video: narration -> frames -> audio -> mp4
set -euo pipefail
cd "$(dirname "$0")"
pip install -q chatterbox-tts faster-whisper librosa numpy pillow
python3 narration.py
rm -rf build/frames
python3 render.py
python3 audio.py
ffmpeg -y -loglevel error -framerate 12 -i build/frames/%05d.png -i build/audio.wav \
  -vf "fps=24,format=yuv420p" -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 192k \
  -movflags +faststart -shortest looksmaxx_morgenroutine.mp4
echo "done: video/looksmaxx_morgenroutine.mp4"
