# Bande-son v5 — tension douce, coups nets au compte à rebours, nappe, groove léger. Volume normalisé ensuite.
import numpy as np, wave
sr=44100; T=18.0; n=int(sr*T)
L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(23)
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*sr)
    if i>=n or i<0: return
    j=min(n,i+len(sig)); s=sig[:j-i]*g; L[i:j]+=s*(1-pan); R[i:j]+=s*(1+pan)
tt=lambda d:np.arange(int(d*sr))/sr
note=lambda m:440*2**((m-69)/12)
def lp(x,a):
    y=np.empty_like(x); acc=0.; A=np.broadcast_to(np.asarray(a,float),x.shape)
    for i in range(len(x)): acc+=A[i]*(x[i]-acc); y[i]=acc
    return y
def env(d,a,r):
    m=int(d*sr); e=np.ones(m); ai=max(1,int(a*sr)); ri=max(1,int(r*sr)); e[:ai]=np.linspace(0,1,ai); e[-ri:]*=np.linspace(1,0,ri); return e
saw=lambda f,t:2*((f*t)%1)-1
def whoosh(d,up=True):
    x=rng.standard_normal(int(d*sr)); t=tt(d); y=lp(x-lp(x,.05),.3); e=(t/d)**2 if up else (1-t/d)**2; return y*e*2
# 0–5 s : tension douce
t=tt(5.1); drone=(.6*np.sin(2*np.pi*note(38)*t)+.5*np.sin(2*np.pi*note(45)*t+.3*np.sin(t*.6))+.3*np.sin(2*np.pi*note(50)*t))*env(5.1,1.0,.1)*(.5+.5*t/5.1)
add(drone,0,g=.25)
t=tt(4.6); cl=sum(saw(note(m)*(1+d),t) for m in (62,63,69) for d in (-.004,.004))
add(lp(cl/6,.06)*(.6+.4*np.sin(2*np.pi*9*t))*env(4.6,1.5,.1)*(t/4.6),.4,g=.22,pan=.1)
def thump(f=60):
    t=tt(.22); return np.sin(2*np.pi*(f+50*np.exp(-t*30))*t)*np.exp(-t*18)
for s in (.5,1.4,2.15,2.7):
    add(thump(),s,g=.45); add(thump(52),s+.16,g=.3)
add(whoosh(.3),1.5,g=.25)
# compte à rebours : coup net et clair
def hit(f):
    t=tt(.45)
    kick=np.sin(2*np.pi*np.cumsum(60+220*np.exp(-t*45))/sr)*np.exp(-t*12)
    x=rng.standard_normal(len(t)); crack=(x-lp(x,.35))*np.exp(-t*40)
    stab=(np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*1.5*t))*np.exp(-t*14)
    return kick*.8+crack*.7+stab*.6
for s,f in ((3.0,880),(3.667,988),(4.333,1175)):
    add(hit(f),s,g=.7); add(whoosh(.15),s-.15,g=.2)
t=tt(.6); add(np.sin(2*np.pi*np.cumsum(400+1600*(t/.6)**2)/sr)*(t/.6)**2*.3+whoosh(.6)*.5,4.4,g=.35)
# 5 s : révélation douce (pas de gros boom)
t=tt(2.5); sw=rng.standard_normal(len(t)); sw=(sw-lp(sw,.2))*np.exp(-t*2.5)*.5
add(sw,5.0,g=.3); t=tt(1.2); add(np.sin(2*np.pi*55*t)*np.exp(-t*3),5.0,g=.35)
# 5–12 s : nappe sans rythme + cloches
t=tt(7.4); d=7.4
pad=sum(saw(note(m)*(1+det),t)*(.5 if m<50 else .3) for m in (41,53,57,60,65,69,72) for det in (-.005,0,.005))
pad=lp(pad/12,.035+.03*np.minimum(1,t/4))*env(d,.4,.8)
add(pad,5.0,g=.55)
choir=sum(np.sin(2*np.pi*note(m)*t*(1+.003*np.sin(2*np.pi*5*t)))/(i+1) for i,m in enumerate([65,69,72,77]))
add(choir*env(d,.8,.8)*.5,5.0,g=.25)
for i,m in enumerate([84,88,91,89,86,93,96]):
    tb=tt(1.6); add((np.sin(2*np.pi*note(m)*tb)+.4*np.sin(2*np.pi*note(m)*2.76*tb))*np.exp(-tb*2.5),5.2+i*.95,g=.06,pan=-.4+.13*i)
add(whoosh(.5),8.6,g=.2)
# 12–17.5 s : groove léger
b=.5; prog=[[53,57,60,65],[48,52,55,60],[50,53,57,62],[46,50,53,58]]
def kick4():
    t=tt(.25); return np.sin(2*np.pi*np.cumsum(55+140*np.exp(-t*40))/sr)*np.exp(-t*13)
def clap():
    t=tt(.18); x=rng.standard_normal(len(t)); x=x-lp(x,.25); return x*np.exp(-t*28)*.5
def hat():
    t=tt(.04); x=rng.standard_normal(len(t)); return (x-lp(x,.5))*np.exp(-t*90)
def pluck(m,d=.3):
    t=tt(d); return (saw(note(m),t)*.4+np.sin(2*np.pi*note(m)*t))*np.exp(-t*9)
for k in range(int((17.5-12.0)/b)):
    s=12.0+k*b; ch=prog[int(k//4)%4]
    add(kick4(),s,g=.45)
    if k%2==1: add(clap(),s,g=.35)
    add(hat(),s+b/2,g=.1,pan=.25)
    for m in ch[1:]: add(pluck(m+12),s+.25,g=.06,pan=.15)
    add(pluck([ch[3]+12,ch[2]+12,ch[3]+12,ch[1]+24][k%4],.4),s,g=.08,pan=-.15)
    t=tt(.4); add(np.sin(2*np.pi*note(ch[0]-12)*t)*env(.4,.005,.15),s,g=.18)
# fin
t=tt(1.8)
for i,m in enumerate([77,81,84,89]): add(np.sin(2*np.pi*note(m)*t)*np.exp(-t*2),16.0+i*.06,g=.07,pan=-.3+.2*i)
# réverb légère
for D,gn in [(.11,.22),(.19,.17),(.29,.12)]:
    kk=int(D*sr); L2=L.copy(); R2=R.copy(); L[kk:]+=gn*R2[:-kk]; R[kk:]+=gn*L2[:-kk]
mix=np.stack([L,R],1)
# coupe-bas 35 Hz (évite les basses qui saturent les téléphones)
for ch in range(2): mix[:,ch]=mix[:,ch]-lp(mix[:,ch],2*np.pi*35/sr)
f=np.ones(n); fo=int(.6*sr); f[-fo:]=np.linspace(1,0,fo); mix*=f[:,None]
mix/=np.abs(mix).max()/0.7
w=wave.open('music7_raw.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
