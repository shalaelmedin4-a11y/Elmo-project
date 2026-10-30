import os
import torch, torchaudio as ta, librosa, numpy as np, difflib, re, json, sys
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
m=ChatterboxMultilingualTTS.from_pretrained(device="cpu")
asr=WhisperModel("small", device="cpu", compute_type="int8")
from num2words import num2words
def norm(s):
    s=re.sub(r"(\d+),(\d+)",lambda m:num2words(int(m.group(1)),lang="de")+" komma "+" ".join(num2words(int(c),lang="de") for c in m.group(2)),s)
    s=re.sub(r"(\d+)\.",lambda m:num2words(int(m.group(1)),lang="de",to="ordinal"),s)
    s=re.sub(r"\d+",lambda m:num2words(int(m.group(0)),lang="de"),s)
    return re.sub(r"[^a-zäöüß ]","",s.lower().replace("-"," ").replace("ç","c"))
def check(wav,sr,txt):
    y=librosa.resample(wav.squeeze().numpy(),orig_sr=sr,target_sr=16000)
    segs,_=asr.transcribe(y,language="de",beam_size=5); hyp=' '.join(s.text for s in segs)
    a,b=norm(txt).split(),norm(hyp).split()
    r=difflib.SequenceMatcher(None,a,b).ratio()
    return (r if len(b)<=len(a) else r*0.8), hyp
only=sys.argv[1:] 
report={}
for line in open('vo2/script.txt'):
    sid,*sents=line.strip().split('|')
    if only and sid not in only: continue
    if not only and os.path.exists(f'vo2/{sid}.wav'): continue
    parts=[]
    for i,txt in enumerate(sents):
        best=None
        for attempt in range(6):
            torch.manual_seed(1000+attempt*17+i)
            wav=m.generate(txt,language_id="de",audio_prompt_path="ref/ref_deep.wav",exaggeration=0.55,cfg_weight=0.4,temperature=0.8)
            sc,hyp=check(wav,m.sr,txt)
            dur=wav.shape[-1]/m.sr
            if best is None or sc>best[0]: best=(sc,wav,hyp)
            if sc>=0.99 and dur < len(txt)*0.11+1.0: break
        print(sid,i,round(best[0],2),'|',txt,'=>',best[2],flush=True)
        # trim silence edges
        y=best[1].squeeze().numpy(); yt,idx=librosa.effects.trim(y,top_db=40); parts.append(yt); import soundfile as sf; os.makedirs('vo2/parts',exist_ok=True); sf.write(f'vo2/parts/{sid}_{i}.wav',yt,m.sr)
        report[f"{sid}_{i}"]=[best[0],best[2]]
    gap=np.zeros(int(0.22*m.sr),dtype=np.float32)
    out=np.concatenate([np.concatenate([p,gap]) for p in parts])[:-len(gap)]
    ta.save(f"vo2/{sid}.wav",torch.from_numpy(out).unsqueeze(0),m.sr)
json.dump(report,open('vo2/asr_report.json','w'),ensure_ascii=False,indent=1)
