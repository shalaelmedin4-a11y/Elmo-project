cd "$(dirname "$0")"; rm -rf frames; rm -f render_done
T=$(node -e "const d=require('./vo2/dur.json');const EX={hook:1.0,shot:1.2,detail:0.6,result:0.4,cta:0.3};let a=2.6;for(const k in d)a+=d[k]+0.45+(EX[k]||0);console.log(a)")
for i in 0 1 2 3; do s=$(python3 -c "print($i*$T/4)"); e=$(python3 -c "print(($i+1)*$T/4+0.04)"); node render.js video frames $s $e > log_$i.txt 2>&1 & done
wait; echo done > render_done
