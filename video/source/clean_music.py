import soundfile as sf, numpy as np, noisereduce as nr, subprocess
a, sr = sf.read('music.wav', dtype='float32')
# steady (stationary) spectral subtraction: removes the separation hiss without pumping
c = np.stack([nr.reduce_noise(y=a[:, i], sr=sr, stationary=True, prop_decrease=0.85,
                              n_std_thresh_stationary=1.2, time_mask_smooth_ms=200, freq_mask_smooth_hz=500)
              for i in range(a.shape[1])], 1)
sf.write('music_nr.wav', c, sr)
# the music is low/tonal; leftover voice sibilants sit above ~3 kHz -> steep low-pass, then fades
subprocess.run(['ffmpeg','-v','error','-y','-i','music_nr.wav','-af',
  'highpass=f=30,lowpass=f=3000,lowpass=f=3000,lowpass=f=3500,afade=t=in:d=1.0,areverse,afade=t=in:d=1.5,areverse','music_clean.wav'], check=True)
