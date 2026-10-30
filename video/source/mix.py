import json,subprocess,numpy as np,wave
s=json.load(open('script.json'))
SR=44100; T=71.7
# (clip file, start, slot end)
plan=[(f'vo/{i:02d}.mp3',a,b) for i,(a,b,_,_) in enumerate(s) if i not in (20,21)]
plan.append(('vo/2021.mp3',54.4,57.0))
fix={7:(19.3,21.0),13:(36.0,39.05),17:(46.0,49.0),26:(67.5,71.6)}
for i,(st,en) in fix.items(): plan[i if i<20 else i-2]=(f'vo/{i:02d}.mp3',st,en)
def load(f,tempo=1.0):
    af=f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tempo}"
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f,'-af',af,'-ac','1','-ar',str(SR),'-f','s16le','-'])
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
out=np.zeros(int(SR*T)+SR,np.float32)
for f,st,en in plan:
    x=load(f); d=len(x)/SR; slot=en-st
    if d>slot: x=load(f,min(1.2,d/slot)); 
    print(f,st,f'{d:.2f}->{len(x)/SR:.2f} slot {slot:.2f}')
    i=int(st*SR); out[i:i+len(x)]+=x
# ambient pad: soft detuned chord in D minor with slow swell
t=np.arange(len(out))/SR
pad=np.zeros_like(out)
for fr,amp in [(73.42,1),(110.0,.6),(146.83,.5),(174.61,.35),(220.0,.25)]:
    pad+=amp*(np.sin(2*np.pi*fr*t)+np.sin(2*np.pi*fr*1.003*t+1))*0.5
pad*=0.6+0.4*np.sin(2*np.pi*t/9.0)
# darker segment 39-46 & 52-72 (night scenes): lower root
k=np.ones(48)/48; pad=np.convolve(pad,k,'same')
pad/=np.abs(pad).max(); pad*=0.035
fade=np.clip(t/2.0,0,1)*np.clip((T-t)/2.0,0,1)
mix=out*0.9+pad*fade
mix=mix[:int(SR*T)]; mix/=max(1,np.abs(mix).max()/0.95)
w=wave.open('voice_mix.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((mix*32767).astype(np.int16).tobytes());w.close()
