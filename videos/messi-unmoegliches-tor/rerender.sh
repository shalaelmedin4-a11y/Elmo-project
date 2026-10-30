cd "$(dirname "$0")"
bash go.sh
ffmpeg -v error -y -framerate 30 -i frames/f_%05d.jpg -i mix2.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart -af "alimiter=limit=0.89,loudnorm=I=-15:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -shortest messi_v4.mp4
echo ok > rerender_done
