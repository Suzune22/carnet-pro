# Bande-son v4 — suspense / tension puis révélation épique (20 s)
import numpy as np, wave
sr=44100; T=18.0; n=int(sr*T)
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
# 6) compte à rebours : un coup VIF et sec à chaque chiffre
def hit():
    t=tt(.5)
    kick=np.sin(2*np.pi*np.cumsum(45+260*np.exp(-t*45))/sr)*np.exp(-t*10)
    x=rng.standard_normal(len(t)); crack=(x-lp(x,.35))*np.exp(-t*38)*1.2
    stab=sum(np.sin(2*np.pi*f*t)*np.exp(-t*18) for f in (880,1320,1975))/3
    sub=np.sin(2*np.pi*42*t)*np.exp(-t*5)
    return np.tanh((kick*1.2+crack+stab*.8+sub*.8)*1.6)
for s in (8,9,10):
    add(hit(),s,g=1.0)
    add(whoosh(.18),s-.18,g=.35)          # petite aspiration juste avant
    for j,dt in enumerate((.5,.75)):      # tics rapides entre les chiffres
        add(tick(3000),s+dt,g=.22,pan=(-.3 if j else .3))
# montée + silence avant la révélation
t=tt(.7); add(np.sin(2*np.pi*np.cumsum(300+2200*(t/.7)**2)/sr)*(t/.7)**2*.45+whoosh(.7)*.9,10.05,g=.45)
# 7) révélation 11.0 : impact
add(boom(2.5,30),11.0,g=1.1)
t=tt(2.0); crash=rng.standard_normal(len(t))*np.exp(-t*2.2); crash=crash-lp(crash,.2); add(crash,11.0,g=.3)
# 8) nouvelle musique 11 → 17 : groove vif et festif (120 BPM, Fa majeur)
b=.5; prog=[[53,57,60,65],[48,52,55,60],[50,53,57,62],[46,50,53,58]]   # F C Dm Bb
def kick4():
    t=tt(.3); return np.sin(2*np.pi*np.cumsum(48+170*np.exp(-t*38))/sr)*np.exp(-t*11)
def clap():
    t=tt(.2); x=rng.standard_normal(len(t)); x=x-lp(x,.25)
    return x*(np.exp(-t*30)+.7*np.exp(-np.maximum(0,t-.01)*30)*(t>.01)+.5*np.exp(-np.maximum(0,t-.022)*30)*(t>.022))*.6
def hat(open_=False):
    t=tt(.18 if open_ else .04); x=rng.standard_normal(len(t)); return (x-lp(x,.5))*np.exp(-t*(18 if open_ else 90))
def logdrum(f):
    t=tt(.35); return np.sin(2*np.pi*np.cumsum(f*(1+.5*np.exp(-t*25)))/sr)*np.exp(-t*7)
def pluck(m,d=.3):
    t=tt(d); return (saw(note(m),t)*.5+np.sin(2*np.pi*note(m)*t))*np.exp(-t*9)
st0=11.5
for k in range(int((17.0-st0)/b)):
    s=st0+k*b; bar=int(k//4)%4; ch=prog[bar]
    add(kick4(),s,g=.75)
    if k%2==1: add(clap(),s,g=.5)
    add(hat(True),s+b/2,g=.16,pan=.25)
    for q in range(4): add(hat(),s+q*b/4,g=.07,pan=-.25)
    pat=[0,0,7,0][k%4]; add(logdrum(note(ch[0]-24+pat)),s+(.25 if k%2 else 0),g=.35)
    # accords en plucks sur contretemps
    for m in ch[1:]: add(pluck(m+12),s+.25,g=.07,pan=.15)
    # mélodie
    mel=[ch[3]+12,ch[2]+12,ch[3]+12,ch[1]+24][k%4]; add(pluck(mel,.4),s,g=.09,pan=-.15)
for s in (11.0,11.5): add(whoosh(.4,False),s,g=.3)
add(whoosh(.45),13.55,g=.35); add(boom(1.0,55),14.0,g=.5)   # passage aux infos
# 9) fin
add(boom(2.5,30),17.0,g=.8)
t=tt(1.0); add((np.sin(2*np.pi*note(65)*t)+np.sin(2*np.pi*note(72)*t))*np.exp(-t*2)*.25,17.0,g=.5)
# master: écho/réverb
for D,gn in [(.11,.3),(.19,.25),(.29,.2),(.41,.14)]:
    kk=int(D*sr); L2=L.copy(); R2=R.copy(); L[kk:]+=gn*R2[:-kk]; R[kk:]+=gn*L2[:-kk]
mix=np.stack([L,R],1)
# silence total juste avant la révélation
i0,i1=int(10.75*sr),int(10.98*sr); mix[i0:i1]*=np.linspace(1,0,i1-i0)[:,None]**4*0
f=np.ones(n); fo=int(.9*sr); f[-fo:]=np.linspace(1,0,fo)**2; mix*=f[:,None]
mix=np.tanh(mix*1.3); mix/=np.abs(mix).max()/0.9
w=wave.open('music5.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
a=mix[:,0]*32767; print([int(np.sqrt((a[int(i*sr/2):int((i+1)*sr/2)]**2).mean())) for i in range(36)])
