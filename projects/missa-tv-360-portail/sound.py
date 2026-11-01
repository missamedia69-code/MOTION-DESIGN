"""Bande-son synthétique originale de « Le monde s'ouvre » (59 s).

Depuis la racine du dépôt : python3 projects/missa-tv-360-portail/sound.py
Écrit uniquement dans .cache/portail-audio/ (les médias lourds restent hors Git).
Le mix final des voix et des effets est décrit dans mix.sh.
"""
from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 59.2
N = round(DUR * SR)
OUT = Path('.cache/portail-audio')
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(360)
beat = .6  # 100 BPM, afro-electronic groove
music = np.zeros((N, 2), dtype=np.float32)


def add(start: float, sound: np.ndarray, gain: float = 1, pan: float = 0) -> None:
    """Equal-power stereo pan; clamp notes that approach the render cut."""
    begin = max(0, round(start * SR))
    end = min(N, begin + len(sound))
    if end <= begin:
        return
    s = sound[:end-begin].astype(np.float32, copy=False)
    music[begin:end, 0] += s * gain * math.sqrt((1-pan)/2)
    music[begin:end, 1] += s * gain * math.sqrt((1+pan)/2)


def tarr(duration: float) -> np.ndarray:
    return np.arange(round(duration*SR), dtype=np.float64) / SR


def kick():
    t = tarr(.42)
    f = 46 + 135*np.exp(-t*36)
    phase = 2*np.pi*np.cumsum(f)/SR
    click = rng.standard_normal(len(t))*np.exp(-t*100)
    return (np.sin(phase)*np.exp(-t*10) + .13*click)*np.minimum(1,t*500)


def snare():
    t = tarr(.23)
    n = rng.standard_normal(len(t))
    hp = n - np.convolve(n,np.ones(8)/8,'same')
    return .55*hp*np.exp(-t*28)+.2*np.sin(2*np.pi*185*t)*np.exp(-t*24)


def hat(long=False):
    t = tarr(.13 if long else .069)
    n = rng.standard_normal(len(t))
    hp = n - np.convolve(n,np.ones(6)/6,'same')
    return hp*np.exp(-t*(32 if long else 78))*.27


def conga(freq=207):
    t = tarr(.23)
    f = freq*(1+.17*np.exp(-t*45))
    return (np.sin(2*np.pi*np.cumsum(f)/SR)+.19*np.sin(4*np.pi*freq*t))*np.exp(-t*22)


def pluck(freq, dur=.55):
    t = tarr(dur)
    attack = np.minimum(1, t*600)
    return (np.sin(2*np.pi*freq*t) + .36*np.sin(2*np.pi*2.01*freq*t)*np.exp(-t*16)
            + .15*np.sin(2*np.pi*3.02*freq*t)*np.exp(-t*26))*np.exp(-t*5.2)*attack


def bass(freq, dur=.47):
    t = tarr(dur)
    return (np.sin(2*np.pi*freq*t)+.34*np.sin(2*np.pi*2*freq*t)+
            .12*np.sin(2*np.pi*3*freq*t))*np.exp(-t*4)*np.minimum(1,t*250)


# A small harmonic loop: D / Bm / G / A, with syncopated kalimba + guitar plucks.
chords = [
    (73.42, (293.66,369.99,440.00), (587.33,659.25,739.99)),
    (61.74, (246.94,293.66,369.99), (493.88,587.33,659.25)),
    (49.00, (196.00,246.94,293.66), (392.00,493.88,587.33)),
    (55.00, (220.00,277.18,329.63), (440.00,554.37,659.25)),
]
for bar in range(math.ceil(DUR/(4*beat))):
    base = bar*4*beat
    root, chord, lead = chords[bar % 4]
    # Intro is sparse; the hook lands before full drums return at the problem beat.
    if base >= 2.0:
        for offset, gain in ((0,.80),(.9,.48),(1.5,.70),(2.1,.38)):
            add(base+offset,kick(),gain)
        for offset, gain in ((.6,.5),(1.8,.62)):
            add(base+offset,snare(),gain,pan=.06)
        for h in range(8):
            t = base+h*.3+(0.025 if h%2 else 0)
            add(t,hat(h%4==3),.38 if h%2 else .28,pan=(-.25 if h%2 else .25))
        for offset in (.37,1.27,1.86):
            add(base+offset,conga(),.16,pan=.24)
    for offset,pitch,gain in ((.0,root,.31),(.88,root*1.122,.18),(1.46,root,.25),(2.04,root*1.334,.18)):
        add(base+offset,bass(pitch),gain)
    for j,offset in enumerate((.0,.9,1.5)):
        add(base+offset,pluck(chord[j],.72),.065,pan=(-.42, .12, .40)[j])
    for j,offset in enumerate((.17,.76,1.1,1.72,2.05)):
        note = lead[(j+bar//2) % 3]
        add(base+offset,pluck(note,.53),.095 if j%2==0 else .068,pan=(-.38 if j%2 else .37))

# A gentle three-note signature makes the CTA feel resolved rather than cut off.
for i,(freq,delay) in enumerate(((587.33,53.11),(739.99,53.29),(880.0,53.49))):
    add(delay,pluck(freq,1.5),.11+i*.025,pan=(-.25,0,.25)[i])

s = np.arange(N)/SR
section = np.interp(s,[0,.8,5.8,6.2,15.8,16.2,28.8,29.2,45.8,46.2,47.5,48.9,52.8,53.2,57.0,58.5,59.2],
                       [.03,.36,.62,.72,.71,.88,.88,1.0,.94,.33,.25,.64,.65,.96,.87,.48,0])
# Keep the voice local, warm and fully intelligible; crossfade ducking at each sentence edge.
duck = np.ones(N,dtype=np.float32)
for start,end in ((.30,4.13),(6.20,15.66),(16.35,20.58),(22.45,28.31),
                  (29.08,34.90),(35.52,39.87),(40.64,45.84),(46.20,51.75),(53.22,57.36)):
    a,b=int(start*SR),int(end*SR)
    duck[a:b]=.35
    r=round(.21*SR)
    duck[max(0,a-r):a] = np.minimum(duck[max(0,a-r):a],np.linspace(1,.35,a-max(0,a-r),endpoint=False))
    duck[b:min(N,b+r)] = np.minimum(duck[b:min(N,b+r)],np.linspace(.35,1,min(N,b+r)-b,endpoint=False))
music *= (section * duck)[:,None]
music = np.tanh(music*1.45)


def save(name: str, signal: np.ndarray, peak: float) -> None:
    signal = np.asarray(signal,dtype=np.float32)
    if signal.ndim == 1:
        signal = signal[:,None]
    signal = signal / max(1e-9,float(np.max(np.abs(signal))))*peak
    signal = np.clip(signal,-1,1)
    with wave.open(str(OUT/name),'wb') as out:
        out.setnchannels(signal.shape[1]); out.setsampwidth(2); out.setframerate(SR)
        out.writeframes((signal*32767).astype('<i2').tobytes())


save('music.wav',music,.63)

# Designed whoosh: filtered noise travelling across the stereo field.
t = tarr(.72)
raw = rng.standard_normal(len(t)); hp = raw-np.convolve(raw,np.ones(20)/20,'same')
shape = np.sin(np.pi*t/.72)**1.8
sweep = (hp*.68 + .15*np.sin(2*np.pi*(210*t+970*t*t)))*shape
whoosh = np.stack((sweep*np.sqrt(np.maximum(0,1-t/.72)),sweep*np.sqrt(t/.72)),axis=1)
save('whoosh.wav',whoosh,.53)

# Round impact for cuts and large title/price reveals.
t = tarr(.75)
f = 52+110*np.exp(-t*25)
noise = rng.standard_normal(len(t))*np.exp(-t*53)
impact = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)+.27*noise
save('impact.wav',impact,.63)

# Soft UI tick for the cards and prices.
t = tarr(.19); f = 370+380*np.exp(-t*27)
tick = (np.sin(2*np.pi*np.cumsum(f)/SR)+.2*np.sin(4*np.pi*np.cumsum(f)/SR))*np.exp(-t*30)
save('tick.wav',tick,.41)

# Signal lock/chime: rising major color, a little sonic brand signature.
chime = np.zeros(round(1.25*SR))
for i,freq in enumerate((440,554.37,659.25,880)):
    offset=round(i*.12*SR)
    tt = np.arange(len(chime)-offset)/SR
    chime[offset:] += (np.sin(2*np.pi*freq*tt)+.2*np.sin(4*np.pi*freq*tt))*np.exp(-tt*4.5)
save('lock.wav',chime,.51)

# A brief sputter before the clean green line arrives.
t=tarr(.48); noise=rng.standard_normal(len(t))
glitch = np.sin(2*np.pi*(96*t+65*t*t))*(np.sin(2*np.pi*18*t)>0)*np.exp(-t*6) + noise*.17*np.exp(-t*7)
save('glitch.wav',glitch,.41)

# Print-safe effects stem. The track is pre-timed so the FFmpeg mix remains small.
def load(name: str) -> np.ndarray:
    with wave.open(str(OUT/name),'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32).reshape(-1,w.getnchannels())/32768

sfx = np.zeros((N,2),dtype=np.float32)
fx_files={name:load(name+'.wav') for name in ('whoosh','impact','tick','lock','glitch')}
events = [
    ('impact',.22,.45),('whoosh',5.92,.46),('glitch',6.14,.23),
    ('tick',7.95,.46),('tick',9.36,.46),('tick',10.82,.44),('impact',14.04,.52),
    ('whoosh',15.92,.56),('tick',17.64,.42),('tick',19.02,.42),
    ('impact',22.35,.38),('tick',24.1,.22),('tick',24.69,.22),('tick',25.28,.22),
    ('whoosh',28.92,.62),('tick',29.63,.23),('whoosh',34.90,.54),
    ('tick',35.82,.22),('whoosh',40.10,.54),('tick',41.04,.22),
    ('whoosh',45.92,.62),('glitch',46.75,.32),('lock',48.65,.57),
    ('whoosh',52.92,.62),('impact',53.21,.53),('lock',55.03,.44),('tick',55.93,.28),
]
for name,start,gain in events:
    sig=fx_files[name]
    a=round(start*SR); b=min(N,a+len(sig))
    sfx[a:b]+=gain*sig[:b-a]
save('sfx-bed.wav',sfx,.68)
print('59.2 s music + designed SFX stem:', OUT)

