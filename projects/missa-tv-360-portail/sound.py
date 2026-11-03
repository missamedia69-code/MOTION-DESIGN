"""Original, light editorial soundtrack for 'Ton envie fait le programme' (59 s).

Only NumPy/wave: deterministic warm plucks, hand percussion and paper/UI foley.
Run from repo root: python3 projects/missa-tv-360-portail/sound.py
Outputs .cache/portail-audio/{music,sfx-bed}.wav; final voice mix is in mix.py.
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
rng = np.random.default_rng(36059)
BEAT = 60 / 110  # buoyant 110 BPM, with spaces left for conversational VO
music = np.zeros((N, 2), dtype=np.float32)


def seconds(duration: float) -> np.ndarray:
    return np.arange(round(duration * SR), dtype=np.float64) / SR


def add(target: np.ndarray, start: float, sound: np.ndarray,
        gain: float = 1, pan: float = 0) -> None:
    """Clamp at 59.2 seconds and place a mono hit with equal-power stereo pan."""
    a = max(0, round(start * SR))
    b = min(len(target), a + len(sound))
    if b <= a:
        return
    sig = sound[:b-a].astype(np.float32, copy=False)
    if sig.ndim == 1:
        target[a:b, 0] += sig * gain * math.sqrt((1-pan)/2)
        target[a:b, 1] += sig * gain * math.sqrt((1+pan)/2)
    else:
        target[a:b] += sig * gain


def kick() -> np.ndarray:
    t = seconds(.36)
    phase = 2 * np.pi * np.cumsum(52 + 87*np.exp(-t*35)) / SR
    click = rng.standard_normal(len(t)) * np.exp(-t*110)
    return np.sin(phase) * np.exp(-t*12) + .07 * click


def clap() -> np.ndarray:
    t = seconds(.23)
    noise = rng.standard_normal(len(t))
    high = noise - np.convolve(noise, np.ones(12)/12, mode='same')
    bursts = np.exp(-t*47) + .56*np.exp(-np.maximum(0,t-.023)*76)*(t>.023)
    return high * bursts * .42


def shaker() -> np.ndarray:
    t = seconds(.105)
    noise = rng.standard_normal(len(t))
    return (noise - np.convolve(noise, np.ones(7)/7, mode='same'))*np.exp(-t*48)*.18


def conga(freq=187) -> np.ndarray:
    t = seconds(.26)
    freq_curve = freq*(1+.18*np.exp(-t*31))
    phase = 2*np.pi*np.cumsum(freq_curve)/SR
    return (np.sin(phase)+.19*np.sin(2.1*phase))*np.exp(-t*21)


def pluck(freq: float, dur=.76) -> np.ndarray:
    t = seconds(dur)
    rise = np.minimum(1, t*430)
    body = np.sin(2*np.pi*freq*t) + .26*np.sin(2*np.pi*2.92*freq*t)*np.exp(-t*18)
    body += .13*np.sin(2*np.pi*4.02*freq*t)*np.exp(-t*30)
    return body*np.exp(-t*4.9)*rise


def soft_bass(freq: float) -> np.ndarray:
    t = seconds(.68)
    return (np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*2*freq*t))*np.exp(-t*5)*np.minimum(1,t*270)


def air_pad(freq: float) -> np.ndarray:
    t = seconds(2.10)
    env = np.sin(np.pi*np.minimum(t,2.10)/2.10)**1.65
    return (np.sin(2*np.pi*freq*t)+.17*np.sin(2*np.pi*(freq*2.003)*t))*env


# Four-bar G / Em / C / D loop, bright rather than ominous; the light syncopation
# is an original synthesis, not a copied track or a prerecorded music sample.
chords = [
    (49.00, (196.00,246.94,293.66), (392.00,493.88,587.33)),
    (41.20, (164.81,196.00,246.94), (392.00,493.88,659.25)),
    (32.70, (130.81,164.81,196.00), (392.00,523.25,659.25)),
    (36.71, (146.83,185.00,220.00), (440.00,587.33,739.99)),
]
for bar in range(math.ceil(DUR/(4*BEAT))):
    base = bar*4*BEAT
    root, chord, high = chords[bar % len(chords)]
    # Music starts immediately, before VO, with a friendly hand-clap invitation.
    for off, strength in ((0,.48),(1.5*BEAT,.30),(2.75*BEAT,.43)):
        add(music,base+off,kick(),strength)
    for off in (BEAT,3*BEAT):
        add(music,base+off,clap(),.25,pan=.09)
    for h in range(8):
        add(music,base+h*BEAT/2+(.013 if h%2 else 0),shaker(),
            .19 if h%2 else .11,pan=(-.22 if h%2 else .24))
    for off,gain,pan in ((.37,.18,-.35),(1.25,.22,.28),(1.83,.14,-.18)):
        add(music,base+off,conga(182 if bar%2 else 223),gain,pan=pan)
    for off,note,gain in ((0,root,.27),(1.28,root*1.5,.13),(1.69,root,.21)):
        add(music,base+off,soft_bass(note),gain)
    for j,off in enumerate((.11,.67,1.23,1.79)):
        add(music,base+off,pluck(high[(j+bar//3)%3]),.077 if j%2 else .09,
            pan=(-.34 if j%2 else .33))
    for j,off in enumerate((.01,.83,1.42)):
        add(music,base+off,pluck(chord[j],.58),.062,pan=(-.22,0,.22)[j])
    for j,note in enumerate(chord):
        add(music,base,air_pad(note),.018,pan=(-.45,0,.45)[j])

# A short warm 3-note answer brings the ending home without a hard audio cut.
for j,(note,at) in enumerate(((587.33,53.10),(659.25,53.30),(783.99,53.51))):
    add(music,at,pluck(note,1.25),.12+j*.02,pan=(-.25,0,.25)[j])

s = np.arange(N)/SR
section = np.interp(s,
    [0,.4,5.8,6.1,13.7,15.9,16.3,28.9,29.2,40.4,45.9,46.3,49.2,52.9,53.2,56,58.5,59.2],
    [.78,.94,.87,.67,.66,.78,.92,.87,1,1,.94,.48,.48,.58,.90,.95,.58,0])
# Duck beneath each new conversational sentence with smooth edges, preserving
# hand percussion between phrases rather than pumping on every transient.
duck = np.ones(N,dtype=np.float32)
for start,end in ((.30,4.70),(6.48,15.10),(16.28,22.29),(22.55,28.96),
                  (29.13,35.01),(35.23,40.27),(40.64,45.85),
                  (46.28,52.36),(53.28,58.68)):
    a,b=round(start*SR),round(end*SR)
    duck[a:b]=.36
    r=round(.24*SR)
    x=max(0,a-r); duck[x:a]=np.minimum(duck[x:a],np.linspace(1,.36,a-x,endpoint=False))
    y=min(N,b+r); duck[b:y]=np.minimum(duck[b:y],np.linspace(.36,1,y-b,endpoint=False))
music *= (section*duck)[:,None]
music = np.tanh(music*1.33)


def save(name: str, signal: np.ndarray, peak: float) -> None:
    signal=np.asarray(signal,dtype=np.float32)
    if signal.ndim==1:
        signal=signal[:,None]
    sig=signal / max(1e-9,float(np.max(np.abs(signal)))) * peak
    with wave.open(str(OUT/name),'wb') as f:
        f.setnchannels(sig.shape[1]);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes((np.clip(sig,-1,1)*32767).astype('<i2').tobytes())


save('music.wav',music,.61)

# Paper slip/shuffle: short stereo noise waves with a low thump, more tactile
# than the former cinematic whoosh/glitch aesthetic.
t=seconds(.55);n=rng.standard_normal(len(t));high=n-np.convolve(n,np.ones(27)/27,mode='same')
shape=(np.sin(np.pi*t/.55)**1.25)*np.exp(-t*2)
paper=np.stack((high*shape*np.sqrt(1-t/.55),high*shape*np.sqrt(t/.55)),axis=1)*.35
save('paper.wav',paper,.48)

t=seconds(.18);n=rng.standard_normal(len(t))
tap=np.sin(2*np.pi*np.cumsum(492+340*np.exp(-t*35))/SR)*np.exp(-t*31)
tap += .13*n*np.exp(-t*90)
save('tap.wav',tap,.44)

t=seconds(.45);phase=2*np.pi*np.cumsum(64+130*np.exp(-t*29))/SR
stamp_sound=np.sin(phase)*np.exp(-t*12)+.18*rng.standard_normal(len(t))*np.exp(-t*73)
save('stamp.wav',stamp_sound,.54)

t=seconds(.73);n=rng.standard_normal(len(t));high=n-np.convolve(n,np.ones(23)/23,mode='same')
sw=np.sin(np.pi*t/.73)**1.9 * high * .38
swipe=np.stack((sw*np.sqrt(np.maximum(0,1-t/.73)),sw*np.sqrt(t/.73)),axis=1)
save('swipe.wav',swipe,.46)

t=seconds(1.13);bell=np.zeros(len(t))
for j,note in enumerate((493.88,587.33,783.99)):
    dt=.12*j;idx=round(dt*SR);tt=t[:len(t)-idx]
    bell[idx:] += (np.sin(2*np.pi*note*tt)+.18*np.sin(2*np.pi*2*note*tt))*np.exp(-tt*5.1)
save('chime.wav',bell,.47)


def load(name: str) -> np.ndarray:
    with wave.open(str(OUT/f'{name}.wav'),'rb') as f:
        return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32).reshape(-1,f.getnchannels())/32768

sfx=np.zeros((N,2),dtype=np.float32)
fx={name:load(name) for name in ('paper','tap','stamp','swipe','chime')}
beats=[
    ('stamp',.10,.34),('tap',1.42,.22),('swipe',3.04,.43),('paper',3.13,.18),
    ('stamp',6.00,.46),('paper',8.11,.39),('paper',9.72,.36),('paper',11.35,.37),('stamp',13.90,.43),
    ('stamp',16.00,.47),('tap',17.25,.31),('tap',19.12,.32),('paper',22.31,.35),
    ('tap',25.53,.27),('tap',25.92,.25),('tap',26.31,.24),
    ('stamp',29.00,.49),('paper',30.40,.35),('swipe',31.60,.43),('tap',33.32,.24),
    ('stamp',35.05,.43),('paper',37.30,.38),('tap',37.91,.29),
    ('stamp',40.55,.45),('tap',41.90,.27),('tap',42.63,.26),('tap',43.36,.26),
    ('stamp',46.00,.40),('chime',49.13,.49),('paper',49.72,.23),
    ('stamp',53.00,.49),('chime',55.30,.52),('tap',56.55,.23),
]
for name,at,gain in beats:
    add(sfx,at,fx[name],gain)
save('sfx-bed.wav',sfx,.64)
print('59.2 s: warm hand-percussion bed and paper/UI effects →',OUT)
