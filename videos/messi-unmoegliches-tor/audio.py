import json, wave, numpy as np
SR=44100
sj=json.load(open('st3/scenes.json')); T=sj['total']; S={s['id']:s for s in sj['scenes']}
N=int(T*SR)+SR; t=np.arange(N)/SR
rng=np.random.default_rng(7)
def env(n,a,d): 
    e=np.ones(n); a=int(a*SR); d=int(d*SR)
    if a: e[:a]=np.linspace(0,1,a)
    e[-d:]*=np.linspace(1,0,d); return e
def lp(x,k): # simple one-pole lowpass
    y=np.empty_like(x); acc=0.0; a=k
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def add(buf,sig,at):
    i=int(at*SR); j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]
mus=np.zeros(N)
# pad chords (Am F Dm E), 5s each
chords=[[110,130.81,164.81],[87.31,110,130.81],[73.42,87.31,110],[82.41,103.83,123.47]]
seg=5.0
for k in range(int(T/seg)+1):
    f=chords[k%4]; n=int(seg*SR*1.1); tt=np.arange(n)/SR
    sig=sum(np.sin(2*np.pi*fr*tt)*0.5+0.25*np.sin(2*np.pi*fr*2.003*tt)+0.12*np.sin(2*np.pi*fr*3.01*tt) for fr in f)
    sig+=0.6*np.sin(2*np.pi*f[0]/2*tt)
    add(mus,sig*env(n,0.8,1.0)*0.09,k*seg)
# kick pulse 96bpm
beat=60/96
kn=int(0.35*SR); kt=np.arange(kn)/SR
kick=np.sin(2*np.pi*np.cumsum(45+90*np.exp(-kt*30))/SR)*np.exp(-kt*9)
hat=rng.standard_normal(int(0.04*SR))*np.exp(-np.arange(int(0.04*SR))/SR*120)
hat=np.diff(hat,prepend=0)
b=0.0
shot0=S['shot']['start']+2.6; impact=S['shot']['start']+3.99; hook_imp=2.89
while b<T-2.8:
    quiet = shot0<b<impact
    if not quiet:
        add(mus,kick*0.55,b)
        add(mus,hat*0.08,b+beat/2)
    b+=beat
# riser into shot
rn=int((impact-shot0)*SR); rt=np.arange(rn)/SR
riser=rng.standard_normal(rn); riser=lp(riser,0.02)+lp(riser,0.2)*np.linspace(0,1,rn)**2
riser*=np.linspace(0,1,rn)**2*0.5
add(mus,riser,shot0)
# riser into hook goal
rn=int(hook_imp*SR); r2=lp(rng.standard_normal(rn),0.1)*np.linspace(0,1,rn)**2*0.35; add(mus,r2,0)
# impact boom
bn=int(2.5*SR); bt=np.arange(bn)/SR
boom=(np.sin(2*np.pi*np.cumsum(30+70*np.exp(-bt*8))/SR)*np.exp(-bt*2.2)*1.0 + lp(rng.standard_normal(bn),0.3)*np.exp(-bt*6)*0.6)
for at in (hook_imp, impact): add(mus,boom*0.9,at)
# crowd roar after goal
cn=int(4.5*SR); crowd=lp(lp(rng.standard_normal(cn),0.08),0.15)*3.0
crowd*=np.concatenate([np.linspace(0,1,int(0.4*SR)),np.ones(cn-int(0.4*SR))])*np.linspace(1,0,cn)**1.5
for at,g in ((hook_imp,0.5),(impact,0.8)): add(mus,crowd*g,at+0.05)
# whooshes at scene starts
wn=int(0.45*SR); wt=np.linspace(0,1,wn)
wh=lp(rng.standard_normal(wn),0.12)*np.sin(np.pi*wt)**2*0.35
for s in sj['scenes'][1:]: add(mus,wh,s['start']-0.2)
# fade out
fo=int(2.5*SR); mus[int(T*SR)-fo:int(T*SR)]*=np.linspace(1,0,fo); mus[int(T*SR):]=0
# VO
vo=np.zeros(N)
def readwav(p):
    w=wave.open(p); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
    if sr!=SR: x=np.interp(np.arange(int(len(x)*SR/sr))*sr/SR,np.arange(len(x)),x)
    return x
vo_on=np.zeros(N)
for s in sj['scenes']:
    if s['id']=='outro': continue
    x=readwav(f"vo/{s['id']}.wav"); x=x/np.max(np.abs(x))*0.85
    at=s['start']+0.25; add(vo,x,at); i=int(at*SR); vo_on[i:i+len(x)]=1
# ducking
duck=lp(vo_on,0.0005)
mix=vo*1.0 + mus*(1-0.55*duck)*0.9
mix=np.tanh(mix*1.1)/np.tanh(1.1)
mix=mix[:int(T*SR)]
out=(np.clip(mix,-1,1)*32767).astype(np.int16)
st=np.stack([out,out],1)
w=wave.open('mix.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print('ok',T, 'impact',impact)
