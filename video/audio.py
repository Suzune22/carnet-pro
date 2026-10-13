import numpy as np, wave
sr=44100; T=19.0; n=int(sr*T); t=np.arange(n)/sr
L=np.zeros(n); R=np.zeros(n)
rng=np.random.default_rng(3)
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*sr); j=min(n,i+len(sig)); s=sig[:j-i]*g
    L[i:j]+=s*(1-pan)/1; R[i:j]+=s*(1+pan)/1
def env(d,a=.01,r=.3):
    m=int(d*sr); e=np.ones(m); ai=int(a*sr); ri=int(r*sr)
    e[:ai]=np.linspace(0,1,ai); e[-ri:]*=np.linspace(1,0,ri); return e
def note(f): return 440*2**((f-69)/12)
def lp(x,a): # one-pole lowpass, a in (0,1)
    y=np.zeros_like(x); acc=0
    for k in range(len(x)): acc+=a*(x[k]-acc); y[k]=acc
    return y
# pad: Am F C G, 4s each (shifted to start at 0)
chords=[[57,60,64,69],[53,57,60,65],[48,55,60,64],[55,59,62,67],[57,60,64,69]]
for ci,ch in enumerate(chords):
    st=ci*4; d=min(4.4,T-st)
    if d<=0: continue
    tt=np.arange(int(d*sr))/sr; sig=np.zeros_like(tt)
    for m in ch:
        for det in (-0.12,0.12):
            ph=2*np.pi*note(m+det)*tt
            sig+=np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph)
    sig*=env(d,.6,.8)*(0.6+0.4*np.sin(2*np.pi*0.25*tt))
    add(sig/len(ch)/2,st,pan=(-.3 if ci%2 else .3),g=.11)
# arpeggio from 7.5 on
bpm=120; b=60/bpm
for k in range(int((T-7.5-1)/(b/2))):
    st=7.5+k*b/2; ci=min(int(st//4),4); ch=chords[ci]; m=ch[k%4]+12
    d=.22; tt=np.arange(int(d*sr))/sr
    s=np.sin(2*np.pi*note(m)*tt)*np.exp(-tt*14)
    add(s,st,pan=(.4 if k%2 else -.4),g=.10)
# kick
def kick():
    d=.45; tt=np.arange(int(d*sr))/sr
    f=45+110*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/sr
    return np.sin(ph)*np.exp(-tt*7)
K=kick()
for k in range(int((T-3.0)/b)):
    st=3.0+k*b
    if st>17.9: break
    add(K,st,g=.55)
# hats offbeat
for k in range(int((T-7.5)/b)):
    st=7.5+k*b+b/2
    if st>17.9: break
    d=.06; h=rng.standard_normal(int(d*sr)); h=np.diff(h,prepend=0)*np.exp(-np.arange(len(h))/sr*60)
    add(h,st,pan=.2,g=.07)
# bass
for k in range(int((T-3.0)/b)):
    st=3.0+k*b
    if st>17.9: break
    ci=min(int(st//4),4); m=chords[ci][0]-24
    d=.42; tt=np.arange(int(d*sr))/sr
    s=np.tanh(2*np.sin(2*np.pi*note(m)*tt))*env(d,.005,.2)
    add(s,st,g=.16)
# risers before transitions & impacts
def riser(d):
    m=int(d*sr); x=rng.standard_normal(m)
    tt=np.arange(m)/sr; a=0.02+0.5*(tt/d)**2
    y=x-lp(x,0.05+0.4*(tt/d).mean()); return y*(tt/d)**2
def impact():
    d=1.6; tt=np.arange(int(d*sr))/sr
    boom=np.sin(2*np.pi*(38+40*np.exp(-tt*6))*tt)*np.exp(-tt*2.5)
    nz=rng.standard_normal(len(tt))*np.exp(-tt*9)*.4
    return boom+nz
for c in [3.0,7.5,11.5,15.0]:
    add(riser(1.2),c-1.2,g=.22); add(impact(),c,g=.5)
add(riser(2.6),0.3,g=.15)
# final chime
for i,m in enumerate([81,84,88,93]):
    d=3.0; tt=np.arange(int(d*sr))/sr
    s=(np.sin(2*np.pi*note(m)*tt)+.4*np.sin(2*np.pi*note(m)*2.01*tt))*np.exp(-tt*1.6)
    add(s,15.05+i*.09,pan=(-.5+i*.33),g=.09)
# simple reverb (feedback delays)
for D,gn in [(0.137,.35),(0.211,.28),(0.293,.22)]:
    k=int(D*sr); L2=L.copy(); R2=R.copy()
    L[k:]+=gn*R2[:-k]; R[k:]+=gn*L2[:-k]
mix=np.stack([L,R],1)
fade=np.ones(n); fo=int(1.2*sr); fade[-fo:]=np.linspace(1,0,fo)**2; fade[:int(.05*sr)]=np.linspace(0,1,int(.05*sr))
mix*=fade[:,None]; mix=np.tanh(mix*1.2); mix/=np.abs(mix).max()/0.89
w=wave.open('music.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
