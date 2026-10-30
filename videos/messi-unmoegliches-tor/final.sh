cd "$(dirname "$0")"
while pgrep -f "[t]ts_gen.py" >/dev/null; do sleep 15; done
for i in hook setup receive space trick touches fourth angle shot detail result cta; do ffmpeg -v error -y -i vo2/$i.wav -af atempo=1.12 vo2/fast/$i.wav; done
python3 - <<'PY'
import json,subprocess
ids=['hook','setup','receive','space','trick','touches','fourth','angle','shot','detail','result','cta']
d={i:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'vo2/fast/{i}.wav'])) for i in ids}
json.dump(d,open('vo2/dur.json','w'))
PY
pgrep -f "[h]ttp.server 8765" >/dev/null || (nohup python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &); sleep 1
bash go.sh
cp frames/scenes.json scenes.json
./ttsenv/bin/python -I audio2.py > audio.log 2>&1
ffmpeg -v error -y -framerate 30 -i frames/f_%05d.jpg -i mix2.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart -af "alimiter=limit=0.89,loudnorm=I=-15:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -shortest messi_v5.mp4
echo ok > final_done
