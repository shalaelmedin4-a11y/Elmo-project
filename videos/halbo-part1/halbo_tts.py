import torch, torchaudio as ta, librosa, numpy as np, json, sys
exec(open('tts_gen.py').read().split('only=sys.argv')[0])   # model m, asr, norm, check
L=[
 ('t1','Halbo! Hörst du überhaupt zu?!','teacher',0.85,0.3),
 ('h1','Ja… ja, natürlich.','boy',0.5,0.4),
 ('h2','Stopp!','boy',0.9,0.3),
 ('h3','Oh mein Gott… oh mein Gott… oh mein Gott…','boyq',0.45,0.45),
 ('h4','Ich kann die Zeit anhalten.','boyq',0.45,0.45),
 ('t2','Halbo!','teacher',0.8,0.3),
]
REF={'teacher':sys.argv[1],'boy':sys.argv[2],'boyq':sys.argv[2]}
rep={}
for lid,txt,who,ex,cfg in L:
    for k in range(3):
        torch.manual_seed(100+k*7)
        w=m.generate(txt,language_id="de",audio_prompt_path=REF[who],exaggeration=ex,cfg_weight=cfg,temperature=0.8)
        sc,hyp=check(w,m.sr,txt); y=librosa.resample(w.squeeze().numpy(),orig_sr=m.sr,target_sr=16000)
        f0,_,_=librosa.pyin(y,fmin=60,fmax=500,sr=16000)
        ta.save(f'halbo/vo/{lid}_{k}.wav',w,m.sr)
        rep[f'{lid}_{k}']=[round(sc,2),round(float(np.nanmedian(f0)) if np.any(~np.isnan(f0)) else 0),round(w.shape[-1]/m.sr,2),hyp]
        print(lid,k,rep[f'{lid}_{k}'],flush=True)
json.dump(rep,open('halbo/vo/report.json','w'),ensure_ascii=False,indent=1)
