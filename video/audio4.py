# Bande-son v4 — suspense / tension puis révélation épique (20 s)
import numpy as np, wave
sr=44100; T=20.0; n=int(sr*T)
L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(17)
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
def saw(f,t): return 2*((f*t)%1)-1
# 1) drone grave 0 → 10.7 (monte)
t=tt(10.75); g=np.clip(t/10.7,0,1)**1.5*.8+.2
drone=(np.sin(2*np.pi*note(26)*t)+.6*np.sin(2*np.pi*note(38)*t+.4*np.sin(t*.5))+.25*np.sin(2*np.pi*note(45)*t))*g*env(10.75,1.2,.05)
add(drone,0,g=.22)
# 2) cordes trémolo dissonantes 3.5 → 10.7, montée de hauteur
t=tt(7.2); k=t/7.2; trem=.55+.45*np.sin(2*np.pi*(8+6*k)*t)
cl=np.zeros_like(t)
for m in [50,51,57,62,63]:
    f=note(m)*(1+.06*k**2)
    for det in (-.004,.004): cl+=saw(f*(1+det),t)
cl=lp(cl/10,.08)*trem*env(7.2,2.5,.05)*(.3+.7*k)
add(cl,3.5,g=.5,pan=.15); add(cl[::-1]*0,0)
# 3) battements de coeur
def thump(f=55,d=.25):
    t=tt(d); return np.sin(2*np.pi*(f+60*np.exp(-t*30))*t)*np.exp(-t*16)
hb=[]; s=.6
while s<8.0:
    hb.append(s); s+= 1.0 if s<4 else .7 if s<6 else .5
for s in hb: add(thump(),s,g=.8); add(thump(48),s+.17,g=.55)
for s in (8,9,10): add(thump(45,.4),s,g=1.0); add(thump(40,.4),s+.2,g=.6)
# 4) tic-tac 1.5 → 8
def tick(f):
    t=tt(.03); x=rng.standard_normal(len(t)); return (x-lp(x,.4))*np.exp(-t*220)+np.sin(2*np.pi*f*t)*np.exp(-t*150)*.6
for i,s in enumerate(np.arange(1.5,8,.5)): add(tick(2400 if i%2 else 1800),s,g=.28,pan=(.4 if i%2 else -.4))
# 5) mots flash 6.1 6.5 6.9 7.3 : coup sourd + whoosh inversé
def whoosh(d,up=True):
    x=rng.standard_normal(int(d*sr)); t=tt(d); y=lp(x-lp(x,.05),.3); e=(t/d)**2 if up else (1-t/d)**2; return y*e*2
def boom(d=2.0,f0=34):
    t=tt(d); return np.sin(2*np.pi*(f0+80*np.exp(-t*7))*t)*np.exp(-t*1.8)+lp(rng.standard_normal(len(t)),.08)*np.exp(-t*6)*1.3
for s in (6.1,6.5,6.9,7.3): add(boom(.6,50),s,g=.6); add(whoosh(.25),s-.25,g=.3)
# 6) compte à rebours : coup de pioche métallique + boom
def clang(f):
    t=tt(1.4); return sum(np.sin(2*np.pi*f*k*t+k)*np.exp(-t*(1.5+k*.8)) for k in (1,2.76,5.4,8.93))/2.5
for s,f in ((8,330),(9,349),(10,392)): add(clang(f),s,g=.55,pan=.1); add(boom(1.5,38),s,g=.75); add(whoosh(.3),s-.3,g=.25)
# riser + silence avant révélation
t=tt(.72); add(np.sin(2*np.pi*np.cumsum(200+1800*(t/.72)**2)/sr)*(t/.72)**2*.5+whoosh(.72)*.8,10.0,g=.4)
# 7) révélation 11.0
add(boom(3.5,28),11.0,g=1.2)
t=tt(2.5); crash=(rng.standard_normal(len(t)))*np.exp(-t*1.6); crash=crash-lp(crash,.15); add(crash,11.0,g=.35)
# 8) partie épique 11 → 19 : batterie, basse, cuivres
b=.5; prog=[[50,57,62,65],[46,53,58,62],[48,55,60,64],[45,52,57,61]]  # Dm Bb C A
def kick():
    t=tt(.35); return np.sin(2*np.pi*np.cumsum(50+140*np.exp(-t*30))/sr)*np.exp(-t*9)
def snare():
    t=tt(.3); return (rng.standard_normal(len(t))*.7+np.sin(2*np.pi*185*t)*.5)*np.exp(-t*13)
def tom(f):
    t=tt(.4); return np.sin(2*np.pi*(f+40*np.exp(-t*20))*t)*np.exp(-t*7)
def brass(ch,d):
    t=tt(d); s=sum(saw(note(m),t)+saw(note(m)*1.003,t) for m in ch)/len(ch)
    return lp(s,.06+.1*np.minimum(1,t/.3))*env(d,.15,.4)
k=0
while 12.0+k*b<19.0:
    st=12.0+k*b; bar=int(k//4)%4
    add(kick(),st,g=.7)
    if k%2==1: add(snare(),st,g=.4)
    if k%4==3: add(tom(110),st+.25,g=.35,pan=-.3)
    if k%4==0: add(brass(prog[bar],2.0),st,g=.32)
    t=tt(.45); add(np.tanh(2*np.sin(2*np.pi*note(prog[bar][0]-12)*t))*env(.45,.005,.15),st,g=.18)
    k+=1
# ostinato cordes
for i,st in enumerate(np.arange(11.5,19,.25)):
    ch=prog[int((st-12)//2)%4] if st>=12 else prog[0]; m=ch[[0,1,2,1][i%4]]+12
    t=tt(.22); add(saw(note(m),t)*np.exp(-t*10)*.5,st,g=.12,pan=(.3 if i%2 else -.3))
add(whoosh(.8),12.2,g=.35); add(boom(1.2,50),13.0,g=.6); add(whoosh(.5),15.5,g=.3)
# 9) fin
add(boom(3.0,30),19.0,g=.8)
t=tt(1.0); add(np.sin(2*np.pi*note(62)*t)*np.exp(-t*2)*.3,19.0,g=.5)
# master: écho/réverb
for D,gn in [(.11,.3),(.19,.25),(.29,.2),(.41,.14)]:
    kk=int(D*sr); L2=L.copy(); R2=R.copy(); L[kk:]+=gn*R2[:-kk]; R[kk:]+=gn*L2[:-kk]
mix=np.stack([L,R],1)
# silence total juste avant la révélation
i0,i1=int(10.75*sr),int(10.98*sr); mix[i0:i1]*=np.linspace(1,0,i1-i0)[:,None]**4*0
f=np.ones(n); fo=int(.9*sr); f[-fo:]=np.linspace(1,0,fo)**2; mix*=f[:,None]
mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()/0.9
w=wave.open('music4.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
a=mix[:,0]*32767; print([int(np.sqrt((a[int(i*sr/2):int((i+1)*sr/2)]**2).mean())) for i in range(40)])
