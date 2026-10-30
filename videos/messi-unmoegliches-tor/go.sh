cd "$(dirname "$0")"; rm -rf frames
for i in 0 1 2 3; do s=$(python3 -c "print($i*17.25)"); e=$(python3 -c "print(($i+1)*17.25)"); node render.js video frames $s $e > log_$i.txt 2>&1 & done
wait; echo done > render_done
