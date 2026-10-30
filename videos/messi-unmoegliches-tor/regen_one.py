import sys, torch, librosa, numpy as np, soundfile as sf
exec(open('tts_gen.py').read().split('only=sys.argv')[0])  # model, asr, norm, check
sid, idx = sys.argv[1], int(sys.argv[2])
sents = [l.strip().split('|') for l in open('vo2/script.txt')]
row = [r for r in sents if r[0] == sid][0]; txt = row[1 + idx]
best = None
for attempt in range(6):
    torch.manual_seed(3000 + attempt * 13)
    wav = m.generate(txt, language_id="de", audio_prompt_path="ref/ref_amused.wav", exaggeration=0.6, cfg_weight=0.4, temperature=0.8)
    sc, hyp = check(wav, m.sr, txt)
    if best is None or sc > best[0]: best = (sc, wav, hyp)
    if sc >= 0.99: break
print(sid, idx, round(best[0], 2), '|', txt, '=>', best[2], flush=True)
yt, _ = librosa.effects.trim(best[1].squeeze().numpy(), top_db=40)
sf.write(f'vo2/parts/{sid}_{idx}.wav', yt, m.sr)
parts = [sf.read(f'vo2/parts/{sid}_{i}.wav')[0] for i in range(len(row) - 1)]
gap = np.zeros(int(0.22 * m.sr))
sf.write(f'vo2/{sid}.wav', np.concatenate([np.concatenate([p, gap]) for p in parts])[:-len(gap)], m.sr)
