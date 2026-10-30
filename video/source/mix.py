import json,subprocess,numpy as np,wave
s=json.load(open('script.json'))
SR=44100; T=71.7
# (clip file, start, slot end)
plan=[(f'vo/{i:02d}.mp3',a,b) for i,(a,b,_,_) in enumerate(s) if i not in (20,21)]
plan.append(('vo/2021.mp3',54.4,57.0))
fix={7:(19.3,21.0),13:(36.0,39.05),17:(46.0,49.0),26:(67.5,71.6)}
for i,(st,en) in fix.items(): plan[i if i<20 else i-2]=(f'vo/{i:02d}.mp3',st,en)
def load(f,tempo=1.0):
    af=f"silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03,areverse,atempo={tempo}"
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f,'-af',af,'-ac','1','-ar',str(SR),'-f','s16le','-'])
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
out=np.zeros(int(SR*T)+SR,np.float32)
for f,st,en in plan:
    x=load(f); d=len(x)/SR; slot=en-st
    if d>slot: x=load(f,min(1.2,d/slot)); 
    print(f,st,f'{d:.2f}->{len(x)/SR:.2f} slot {slot:.2f}')
    f_=min(len(x)//4,int(.02*SR)); r_=np.linspace(0,1,f_); x[:f_]*=r_; x[-f_:]*=r_[::-1]  # click-free edges
    i=int(st*SR); out[i:i+len(x)]+=x
# original background music (vocals removed)
import soundfile as sf
mu,_=sf.read('music_clean.wav',dtype='float32');mu=mu[:len(out)]
mix=np.zeros((len(out),2),np.float32);mix[:len(mu)]+=mu;mix+=(out*0.9)[:,None]
mix=mix[:int(SR*T)]; mix/=max(1,np.abs(mix).max()/0.95)
w=wave.open('voice_mix.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((mix*32767).astype(np.int16).tobytes());w.close()
