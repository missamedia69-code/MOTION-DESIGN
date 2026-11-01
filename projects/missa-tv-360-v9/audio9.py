import numpy as np, wave
SR=44100
def save(name, sig, norm=.9):
    sig=np.asarray(sig,dtype=np.float64)
    sig=sig/max(1e-9,np.max(np.abs(sig)))*norm
    w=wave.open(name,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((sig*32767).astype('<i2').tobytes()); w.close()
rng=np.random.default_rng(7)
DUR=52.5; N=int(SR*DUR); t=np.arange(N)/SR
mix=np.zeros(N)
def add(s, x):
    i0=int(s*SR); i1=min(N,i0+len(x))
    if i0<N: mix[i0:i1]+=x[:i1-i0]
BEAT=0.6
for b in range(int(DUR/BEAT)):
    L=int(.28*SR); tt=np.arange(L)/SR
    f=55*np.exp(-tt*14)+40
    add(b*BEAT, np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)*.9)
for b in range(int(DUR/(BEAT/2))):
    L=int(.09*SR); tt=np.arange(L)/SR
    nse=rng.standard_normal(L)
    sh=(nse-np.roll(nse,1))*np.exp(-tt*46)
    add(b*BEAT/2, sh*(.28 if b%2 else .16))
basspat=[(0,55,.55),(.9,55,.25),(1.2,65.4,.4),(1.8,49,.5),(2.4,55,.3),(3.0,73.4,.4),(3.6,65.4,.3)]
for bar in range(int(DUR/2.4)):
    for o,f,d in basspat:
        L=int(d*SR); tt=np.arange(L)/SR
        add(bar*2.4+o, np.sin(2*np.pi*f*tt)*(1+.4*np.sin(4*np.pi*f*tt))*np.exp(-tt*3.2)*.5)
kal=[(0,440),(.3,523.25),(.6,587.33),(1.2,659.25),(1.5,587.33),(2.4,523.25),(2.7,440),(3.3,392),(3.9,440),(4.2,523.25)]
for rep in range(int(DUR/4.8)):
    for o,f in kal:
        L=int(.7*SR); tt=np.arange(L)/SR
        k=(np.sin(2*np.pi*f*tt)+.5*np.sin(4*np.pi*f*tt)*np.exp(-tt*9)+.2*np.sin(2*np.pi*f*3.01*tt))*np.exp(-tt*5.5)
        add(rep*4.8+o, k*.16)
for bar in range(int(DUR/2.4)):
    for o,f in [(0.6,300),(1.5,820),(2.1,300)]:
        L=int(.16*SR); tt=np.arange(L)/SR
        nz=np.diff(np.concatenate(([0],rng.standard_normal(L))))
        c=np.sin(2*np.pi*f*tt)*np.exp(-tt*22)+nz*np.exp(-tt*30)*.3
        add(bar*2.4+o, c*.3)
mix*=np.clip(t/1.5,0,1)*np.clip((DUR-t)/2.5,0,1)
save('.cache/music9.wav', mix)
L=int(.9*SR); tt=np.arange(L)/SR
nse=rng.standard_normal(L)
wh=(nse-np.roll(nse,1))*np.sin(np.pi*tt/.9)**2
save('.cache/sfx-whoosh9.wav', wh*.8)
L=int(.7*SR); tt=np.arange(L)/SR
imp=np.sin(2*np.pi*np.cumsum(90*np.exp(-tt*6)+38)/SR)*np.exp(-tt*5.5)+rng.standard_normal(L)*np.exp(-tt*28)*.4
save('.cache/sfx-impact9.wav', imp)
L=int(1.4*SR); st=np.zeros(L)
for i,f in enumerate([440,523.25,659.25,880]):
    o=int(i*.12*SR); tt=np.arange(L-o)/SR
    st[o:]+=(np.sin(2*np.pi*f*tt)+.4*np.sin(4*np.pi*f*tt)*np.exp(-tt*10))*np.exp(-tt*4)*.5
save('.cache/sfx-sting9.wav', st)
L=int(.12*SR); tt=np.arange(L)/SR
save('.cache/sfx-pop9.wav', np.sin(2*np.pi*np.cumsum(600*np.exp(-tt*30)+180)/SR)*np.exp(-tt*26))
print('music9 + 4 sfx ok')
