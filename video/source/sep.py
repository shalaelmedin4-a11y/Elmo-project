import torch, soundfile as sf, numpy as np
from demucs.pretrained import get_model
from demucs.apply import apply_model
m = get_model('htdemucs'); m.eval()
a, sr = sf.read('orig.wav', dtype='float32')
wav = torch.tensor(a.T)[None]
ref = wav.mean(1, keepdim=True); mu, sd = ref.mean(), ref.std()
with torch.no_grad(): out = apply_model(m, (wav-mu)/sd, device='cpu', split=True, overlap=0.25)[0]*sd+mu
src = dict(zip(m.sources, out))
music = sum(v for k, v in src.items() if k != 'vocals')
sf.write('music.wav', music.numpy().T, sr); sf.write('vocals.wav', src['vocals'].numpy().T, sr)
