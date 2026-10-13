# Bande-son v3 (style trailer) — 18 s
import numpy as np, wave
sr=44100; T=18.0; n=int(sr*T)
L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(9)
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*sr)
    if i>=n: return
    j=min(n,i+len(sig)); s=sig[:j-i]*g; L[i:j]+=s*(1-pan); R[i:j]+=s*(1+pan)
tt_=lambda d:np.arange(int(d*sr))/sr
note=lambda m:440*2**((m-69)/12)
def lp(x,a):
    y=np.empty_like(x); acc=0.
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def boom(d=2.2,f0=34):
    t=tt_(d); return np.sin(2*np.pi*(f0+90*np.exp(-t*7))*t)*np.exp(-t*1.6)+lp(rng.standard_normal(len(t)),.08)*np.exp(-t*5)*1.5
def clang(f=220):
    t=tt_(1.2); s=sum(np.sin(2*np.pi*f*k*t+k)*np.exp(-t*(2+k)) for k in (1,2.76,5.4,8.9))/3
    return s+boom(1.2,40)*.8
def whoosh(d,up=True):
    x=rng.standard_normal(int(d*sr)); t=tt_(d)
    y=x-lp(x,.05); e=(t/d)**2 if up else (1-t/d)**2; return lp(y,.3)*e*2
def stat(d):
    x=rng.standard_normal(int(d*sr)); return x*(rng.random(len(x))<.3)*.6
# drone (intro + countdown)
t=tt_(7.6); drone=(np.sin(2*np.pi*note(28)*t)+.5*np.sin(2*np.pi*note(40)*t+np.sin(t*.7))+.3*np.sin(2*np.pi*note(47)*t))*np.minimum(1,t/1.0)*np.minimum(1,(7.6-t)/.4)
add(drone,0,g=.18)
add(boom(),0.0,g=.9); add(whoosh(.6,False),0,g=.5)
for a,b in [(1.35,1.62),(2.62,2.9)]: add(stat(b-a),a,g=.35)
t=tt_(.75); buzz=(np.sign(np.sin(2*np.pi*120*t))*.3+rng.standard_normal(len(t))*.6)*(rng.random(len(t))<.5)*np.sin(np.pi*t/.75)
add(buzz,1.75,g=.35,pan=.2)
for h,f in [(3.2,196),(4.2,220),(5.2,247)]: add(clang(f),h,g=.7); add(whoosh(.35),h-.35,g=.3)
# fire riser into reveal
d=1.45; t=tt_(d); riser=np.sin(2*np.pi*np.cumsum(120+900*(t/d)**2)/sr)*(t/d)**2*.4
crackle=(rng.random(len(t))<.004)*rng.standard_normal(len(t))*3
add(riser+whoosh(d)*.8+crackle,6.05,g=.5)
add(boom(3.0,30),7.5,g=1.0); add(clang(110),7.5,g=.4)
# rock groove 8.9 – 17.25 (120 BPM)
b=.5; prog=[40,40,43,38]   # E E G D
def kick():
    t=tt_(.35); return np.sin(2*np.pi*np.cumsum(50+150*np.exp(-t*30))/sr)*np.exp(-t*9)
def snare():
    t=tt_(.3); return (rng.standard_normal(len(t))*.7+np.sin(2*np.pi*190*t)*.5)*np.exp(-t*14)
def hat():
    t=tt_(.05); x=rng.standard_normal(len(t)); return (x-lp(x,.3))*np.exp(-t*80)
def power(m,d):
    t=tt_(d); s=sum(np.sign(np.sin(2*np.pi*note(mm)*t+ph))*.5+np.sin(2*np.pi*note(mm)*t) for mm,ph in [(m,0),(m+7,.3),(m+12,.7)])
    s=np.tanh(lp(s,.25)*1.5); return s*np.minimum(1,t/.01)*np.minimum(1,(d-t)/.03)
gaps=[(11.45,11.6),(12.45,12.52),(14.0,14.25)]
k=0; s0=8.9
while s0+k*b<17.25:
    st=s0+k*b
    if not any(a-.02<=st<g for a,g in gaps):
        add(kick(),st,g=.75)
        if k%2==1: add(snare(),st,g=.45)
        add(hat(),st+b/2,g=.15,pan=.3); add(hat(),st,g=.08,pan=-.3)
        m=prog[(k//4)%4]; add(power(m,b*.92),st,g=.12,pan=(.25 if k%2 else -.25))
    k+=1
for a,g in gaps: add(stat(g-a),a,g=.2)
add(whoosh(.7),14.5,g=.4); add(boom(1.5,45),15.2,g=.5)
add(whoosh(.5),8.4,g=.3)
# glitch stutter
for i in range(6): add(stat(.04)+power(52,.04),16.7+i*.09,g=.4)
# TV off zap
t=tt_(.55); zap=np.sin(2*np.pi*np.cumsum(2400*np.exp(-t*6)+60)/sr)*np.exp(-t*4)
add(zap,17.3,g=.35); add(boom(.6,60),17.3,g=.3)
# master
for D,gn in [(.09,.25),(.15,.2),(.23,.15)]:
    kk=int(D*sr); L2=L.copy(); R2=R.copy(); L[kk:]+=gn*R2[:-kk]; R[kk:]+=gn*L2[:-kk]
mix=np.stack([L,R],1); mix=np.tanh(mix*1.4); mix/=np.abs(mix).max()/0.9
f=np.ones(n); f[int(17.85*sr):]=0; mix*=f[:,None]
w=wave.open('music3.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix*32767).astype('<i2').tobytes()); w.close()
a=(mix[:,0]*32767); print([int(np.sqrt((a[i*sr:(i+1)*sr]**2).mean())) for i in range(18)])
