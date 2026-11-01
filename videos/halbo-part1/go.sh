cd "$(dirname "$0")/.."; rm -rf halbo/frames; rm -f halbo/render_done
pgrep -f "[h]ttp.server 8765" >/dev/null || (nohup python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &); sleep 1
T=62
for i in 0 1 2 3; do s=$(python3 -c "print($i*$T/4)"); e=$(python3 -c "print(($i+1)*$T/4+0.04)"); node halbo/render.js video halbo/frames $s $e > halbo/log_$i.txt 2>&1 & done
wait
ffmpeg -v error -y -framerate 30 -i halbo/frames/f_%05d.jpg -i halbo/mix.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -ar 48000 -shortest halbo/halbo_part1.mp4
echo ok > halbo/render_done
