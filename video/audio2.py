# Bande-son v2 (style pop / motion design) — 20 s, 120 BPM
import numpy as np, wave
sr=44100; T=20.0; n=int(sr*T); t=np.arange(n)/sr
L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(5)
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*sr)
    if i>=n: return
    j=min(n,i+len(sig)); s=sig[:j-i]*g; L[i:j]+=s*(1-pan); R[i:j]+=s*(1+pan)
def env(d,a=.01,r=.3):
    m=int(d*sr); e=np.ones(m); ai=max(1,int(a*sr)); ri=max(1,int(r*sr))
    e[:ai]=np.linspace(0,1,ai); e[-ri:]*=np.linspace(1,0,ri); return e
note=lambda m:440*2**((m-69)/12)
b=0.5
# chords: C G Am F (2 s each)
prog=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]]
def chord_at(s): return prog[int(s//2)%4]
# soft pluck pad (sidechained)
for k in range(int(T/2)):
    st=k*2; ch=chord_at(st); d=2.2; tt=np.arange(int(d*sr))/sr; sig=np.zeros_like(tt)
    for m in ch:
        for det in (-.08,.08):
            ph=2*np.pi*note(m+det)*tt; sig+=np.sin(ph)+.25*np.sin(2*ph)
    duck=1-.6*np.exp(-((tt%b))*9) if st>=3 else 1
    add(sig*env(d,.08,.4)*duck/10,st,pan=.2*(1 if k%2 else -1),g=.9)
# kick + clap + hats from 3.0 (break at 8.4-9.0 and final hit 16.8)
def kick():
    d=.4; tt=np.arange(int(d*sr))/sr; f=50+140*np.exp(-tt*30); return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tt*8)
def clap():
    d=.25; x=rng.standard_normal(int(d*sr)); tt=np.arange(len(x))/sr
    e=np.exp(-tt*25)+.6*np.exp(-np.maximum(0,tt-.012)*25)*(tt>.012); x=np.diff(x,prepend=0); return x*e*.5
def hat():
    d=.05; x=np.diff(rng.standard_normal(int(d*sr)),prepend=0); return x*np.exp(-np.arange(len(x))/sr*70)
K=kick()
for k in range(int(T/b)):
    s=k*b
    if s<3.0 or 8.4<=s<9.0 or s>=16.8: continue
    add(K,s,g=.6)
    if k%2==1: add(clap(),s,g=.35,pan=.05)
    add(hat(),s+b/2,g=.12,pan=.3)
    if s>=9.0: add(hat(),s+b/4,g=.06,pan=-.3); add(hat(),s+3*b/4,g=.06,pan=-.3)
    # bass
    m=chord_at(s)[0]-24; d=.45; tt=np.arange(int(d*sr))/sr
    add(np.tanh(2.5*np.sin(2*np.pi*note(m)*tt))*env(d,.005,.15),s,g=.15)
    add(np.tanh(2.5*np.sin(2*np.pi*note(m)*tt))*env(d,.005,.15),s+b*.75,g=.08)
# lead arpeggio from 9.0
for k in range(int((16.8-9.0)/(b/2))):
    s=9.0+k*b/2; ch=chord_at(s); m=ch[[0,1,2,3,2,1,3,2][k%8]]+12; d=.2; tt=np.arange(int(d*sr))/sr
    sq=np.sign(np.sin(2*np.pi*note(m)*tt))*.3+np.sin(2*np.pi*note(m)*tt)
    add(sq*np.exp(-tt*16),s,pan=(.35 if k%2 else -.35),g=.07)
# pops (notifications) and click
def pop(f):
    d=.15; tt=np.arange(int(d*sr))/sr; ff=f*(1+1.2*np.exp(-tt*40)); return np.sin(2*np.pi*np.cumsum(ff)/sr)*np.exp(-tt*22)
for i,s in enumerate([.08,.55,.8,1.05,1.3]): add(pop(700+i*140),s,g=.3,pan=(-.4+.2*i))
cl=np.diff(rng.standard_normal(int(.02*sr)),prepend=0)*np.exp(-np.arange(int(.02*sr))/sr*300)
add(cl,4.25,g=.6); add(pop(320),4.27,g=.4)
# whooshes & impacts
def whoosh(d,up=True):
    m=int(d*sr); x=rng.standard_normal(m); tt=np.arange(m)/sr; y=np.zeros(m); acc=0
    for i in range(m):
        a=.02+.35*((tt[i]/d) if up else 1-tt[i]/d); acc+=a*(x[i]-acc); y[i]=acc
    e=np.sin(np.pi*tt/d)**2; return y*e*3
def impact():
    d=1.4; tt=np.arange(int(d*sr))/sr
    return np.sin(2*np.pi*(40+60*np.exp(-tt*8))*tt)*np.exp(-tt*3)+rng.standard_normal(len(tt))*np.exp(-tt*14)*.35
for c in [3.0,4.6,5.6,8.4,11.6,14.6,16.8]:
    add(whoosh(.5),c-.45,g=.35,pan=0); add(impact(),c,g=.45)
for c in [6.2,7.55,13.05,15.15,16.35]: add(whoosh(.35,False),c-.1,g=.3,pan=.3)
# riser into 4.6 and into 16.8
for st,d in [(3.6,1.0),(15.6,1.2)]:
    tt=np.arange(int(d*sr))/sr; f=300+1500*(tt/d)**2
    add(np.sin(2*np.pi*np.cumsum(f)/sr)*(tt/d)**2*.4+whoosh(d)*.5,st,g=.25)
# end chime (logo) + sustain chord
for i,m in enumerate([72,76,79,84,88]):
    d=3.0; tt=np.arange(int(d*sr))/sr
    add((np.sin(2*np.pi*note(m)*tt)+.35*np.sin(2*np.pi*note(m)*3.01*tt))*np.exp(-tt*1.4),17.6+i*.07,pan=-.5+.25*i,g=.08)
d=3.2; tt=np.arange(int(d*sr))/sr; sig=sum(np.sin(2*np.pi*note(m)*tt) for m in [48,60,64,67])
add(sig*env(d,.05,1.5)/4,16.8,g=.35)
# reverb-ish
for D,gn in [(.113,.3),(.187,.25),(.271,.18),(.353,.12)]:
    k=int(D*sr); L2=L.copy(); R2=R.copy(); L[k:]+=gn*R2[:-k]; R[k:]+=gn*L2[:-k]
mix=np.stack([L,R],1)
f=np.ones(n); fo=int(1.0*sr); f[-fo:]=np.linspace(1,0,fo)**2; f[:int(.03*sr)]=np.linspace(0,1,int(.03*sr)); mix*=f[:,None]
mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()/0.9
w=wave.open('music2.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
