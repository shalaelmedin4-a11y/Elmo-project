import torch, torchaudio as ta, librosa, numpy as np, soundfile as sf
exec(open('tts_gen.py').read().split('only=sys.argv')[0])
parts=[];info=[]
for k,(seed,ex) in enumerate([(11,0.4),(23,0.5),(37,0.6)]):
    best=None
    for a in range(4):
        torch.manual_seed(seed+a*101)
        w=m.generate('Oh mein Gott.',language_id="de",audio_prompt_path='halbo/ref/boy_3.wav',exaggeration=ex,cfg_weight=0.45,temperature=0.8)
        sc,hyp=check(w,m.sr,'Oh mein Gott.');d=w.shape[-1]/m.sr
        if sc>=0.99 and d<1.8: best=(sc,w,hyp);break
        if best is None or sc>best[0]: best=(sc,w,hyp)
    y,_=librosa.effects.trim(best[1].squeeze().numpy(),top_db=40);parts.append(y);info.append((k,best[0],best[2],len(y)/m.sr))
gap=[0.55,0.7]
out=np.concatenate([parts[0],np.zeros(int(gap[0]*m.sr)),parts[1]*0.9,np.zeros(int(gap[1]*m.sr)),parts[2]*0.8])
sf.write('halbo/vo/h3_omg.wav',out,m.sr);print(info,len(out)/m.sr)
