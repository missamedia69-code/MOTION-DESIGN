"""Produce ORIGINAL 120 BPM score, foley, and edited voice stems (48 kHz/24-bit).

All instrumental waveforms are synthesized here. No third-party song/sample. The
voices come from selected synthetic takes in assets/voice; commercial rights
are NOT asserted by this script. Run from repo root:
    python3 projects/missa-tv-360-ton-ecran/audio.py
The 59-second three separate stems go to livrables/PISTES_SEPAREES_59S/;
non-deliverable short stems and normalized mixes go to .cache/ton-ecran-audio/.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parent
SR = 48000
CACHE = ROOT / '.cache/ton-ecran-audio'
STEMS = ROOT / 'livrables/PISTES_SEPAREES_59S'
CACHE.mkdir(parents=True, exist_ok=True)
STEMS.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261102)


def load_tts(name: str) -> np.ndarray:
    path = PROJECT / 'assets/voice' / f'{name}.mp3'
    if not path.exists():
        raise FileNotFoundError(f'Prise vocale manquante : {path}; voir les droits / SPEC-H-N.md')
    cmd = ['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','1','-ar',str(SR),'pipe:1']
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype='<f4').copy()


def tempo(sound: np.ndarray, factor: float) -> np.ndarray:
    """Rubber Band pitch-preserving tempo for *small* textual timing corrections."""
    if abs(factor-1) < .002:
        return sound
    args = ['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0',
            '-af',f'rubberband=tempo={factor:.5f}:transients=crisp',
            '-ar',str(SR),'-ac','1','-f','f32le','pipe:1']
    p = subprocess.run(args, input=sound.astype('<f4').tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout,dtype='<f4').copy()


def add(target: np.ndarray, at: float, sound: np.ndarray, gain: float = 1, pan: float = 0) -> None:
    if at < 0:
        sound = sound[-round(at*SR):]
        at = 0
    a = round(at*SR)
    b = min(len(target),a+len(sound))
    if b <= a: return
    s = sound[:b-a]
    if target.ndim == 1:
        target[a:b] += s*gain
    elif s.ndim == 1:
        target[a:b,0] += s*gain*math.sqrt((1-pan)/2)
        target[a:b,1] += s*gain*math.sqrt((1+pan)/2)
    else:
        target[a:b] += s*gain


def fade(s: np.ndarray, attack=.012, release=.020) -> np.ndarray:
    s = s.copy()
    a = min(len(s)//2, round(SR*attack))
    b = min(len(s)//2, round(SR*release))
    if a: s[:a] *= np.linspace(0,1,a)
    if b: s[-b:] *= np.linspace(1,0,b)
    return s


def edit_voice(version: str) -> np.ndarray:
    n = int(version)*SR
    out = np.zeros(n,dtype=np.float32)
    source = {key:load_tts(key) for key in (
        ['n1-intro','n2-univers','n3-ecrans-prix','n4-annuel','n5-cta','papa','maman','kevin']
        if version=='59' else [f'short{version}'])}

    def place(name, at, lo=0, hi=None, speed=1, gain=1):
        s = source[name]
        s = s[round(lo*SR):round(hi*SR) if hi is not None else None]
        if speed!=1: s=tempo(s,speed)
        s=fade(s)
        add(out,at,s,gain)
        print(f'  {version}s voice {name:17} {at:5.2f}–{at+len(s)/SR:5.2f} tempo {speed:.2f}')

    if version=='59':
        # A two-sentence take is divided so Papa can answer naturally between clauses.
        place('n1-intro',.05,0,4.26,1.16,.92)
        place('papa',3.72,.08,2.06,1,1.03)
        place('n1-intro',5.74,4.84,9.0,1.17,.92)
        place('maman',9.34,.23,3.19,1,1.13)
        # Three different selected synthetic speakers, 0.35 s complete silence before 14.
        place('papa',12.58,2.52,3.46,1,.48)
        place('maman',12.55,3.60,4.66,1,.50)
        place('kevin',12.56,.22,1.25,1,.48)
        place('n2-univers',14.08,0,2.98,.92,.93)
        place('n2-univers',18.49,3.16,5.71,.85,.93)
        place('n2-univers',23.71,6.26,8.08,.90,.93)
        place('n2-univers',28.48,8.27,12.53,.83,.93)
        place('n3-ecrans-prix',35.28,0,2.78,1,.93)
        place('n3-ecrans-prix',38.13,3.17,7.31,1,.93)
        place('n3-ecrans-prix',42.28,7.57,9.76,1,.93)
        place('papa',45.10,3.90,4.58,1,1.05)
        place('n4-annuel',46.35,0,6.14,.95,.93)
        place('n5-cta',54.06,0,3.67,1,.96)
        place('papa',57.81,5.09,6.13,1,.45)
        place('maman',57.80,5.27,6.42,1,.45)
        place('kevin',57.82,1.82,2.70,1,.50)
        out[round(13.64*SR):round(14.00*SR)] = 0
    elif version=='30':
        # Bespoke short-read, with authored pauses between its clauses.
        place('short30',.20,0,2.56,.91,.93)
        place('short30',3.31,3.12,7.24,.85,.93)
        place('short30',9.79,7.46,9.11,.91,.93)
        place('short30',11.99,9.55,12.69,.82,.93)
        place('short30',18.01,12.93,14.33,.90,.93)
        place('short30',20.80,14.58,16.95,.88,.93)
        place('short30',26.55,17.26,19.26,.92,.93)
    elif version=='15':
        place('short15',.15,0,5.94,.96,.93)
        place('short15',7.68,6.27,7.51,.93,.93)
        place('short15',9.15,7.72,8.85,.93,.93)
        place('short15',12.27,9.06,10.12,.92,.93)
    return out


def seconds(dur):
    return np.arange(round(dur*SR),dtype=np.float64)/SR


def kick():
    t=seconds(.40)
    hz=52+85*np.exp(-t*48)
    phase=2*np.pi*np.cumsum(hz)/SR
    click=RNG.standard_normal(len(t))*np.exp(-t*110)
    return .91*np.sin(phase)*np.exp(-t*10)+.05*click


def hand(low=181):
    t=seconds(.24)
    phase=2*np.pi*np.cumsum(low*(1+.23*np.exp(-t*36)))/SR
    return (np.sin(phase)+.20*np.sin(2*phase))*np.exp(-t*24)


def shaker():
    t=seconds(.13)
    noise=RNG.standard_normal(len(t))
    return (noise-np.convolve(noise,np.ones(9)/9,mode='same'))*np.exp(-t*46)*.18


def clap():
    t=seconds(.20)
    noise=RNG.standard_normal(len(t))
    bursts=np.exp(-t*55)+.65*np.exp(-np.maximum(0,t-.022)*77)*(t>.022)
    return noise*bursts*.30


def bass(note):
    t=seconds(.52)
    ph=2*np.pi*note*t
    return (np.sin(ph)+.22*np.sin(2*ph))*np.exp(-t*5)*np.minimum(1,t*230)


def guitar(note):
    """Detuned nylon-ish pluck with a very short percussive attack, not a sample."""
    t=seconds(.44)
    env=np.exp(-t*10)*np.minimum(1,t*360)
    ph=2*np.pi*note*t
    return (.8*np.sin(ph)+.20*np.sin(2.004*ph)+.09*np.sin(3.01*ph))*env


def pad(note):
    t=seconds(1.95)
    env=np.sin(np.pi*t/1.95)**2
    return (np.sin(2*np.pi*note*t)+.1*np.sin(2*np.pi*note*1.997*t))*env*.22


def make_music(dur: int, drop: float, end: float) -> np.ndarray:
    n=round(dur*SR)
    track=np.zeros((n,2),dtype=np.float32)
    # Original four-bar turnaround with syncopated hand percussion and plucks.
    changes=[(55.0,[220.0,261.63,329.63]),(43.65,[174.61,220.0,261.63]),
             (65.41,[261.63,329.63,392.00]),(49.0,[196.0,246.94,293.66])]
    for bar in range(math.ceil(dur/2)):
        at=2*bar
        root,chord=changes[bar%len(changes)]
        full=(at+.02 >= drop)
        for beat in range(4):
            tick=at+beat*.5
            if tick>=dur: continue
            if full:
                if beat in (0,2): add(track,tick,kick(),.42 if beat==0 else .28)
                if beat in (1,3): add(track,tick,clap(),.29,pan=.08)
                add(track,tick+.35,hand(183+bar%3*12),.16,pan=(-.22 if beat%2 else .18))
            elif beat==0: add(track,tick,kick(),.12)
            for half in range(2):
                if full or half==0:
                    add(track,tick+half*.25+.014*(half==1),shaker(),
                        .17 if full else .05,pan=(-.25 if half==0 else .26))
        for off,g in ((0,.33),(.74,.16),(1.25,.26),(1.74,.15)):
            add(track,at+off,bass(root*(2 if off==.74 else 1)),g if full else g*.23,pan=-.06)
        if full:
            for i,off in enumerate((.10,.38,.86,1.12,1.63)):
                add(track,at+off,guitar(chord[(i+bar)%3]*(2 if i==4 else 1)),
                    .19 if i%2==0 else .13,pan=(-.36 if i%2 else .31))
            for j,note in enumerate(chord):
                add(track,at,pad(note/2),.024,pan=(-.3,0,.3)[j])
    # Luminous full band entry, final original chord and punctual sting.
    add(track,drop,kick(),.48)
    for i,note in enumerate((392.0,493.88,587.33)):
        add(track,end-.60+i*.09,guitar(note),.23+i*.05,pan=(-.35,0,.35)[i])
    sec=np.arange(n)/SR
    env=np.ones(n,dtype=np.float32)
    env[sec<drop] *= .58
    env[sec>=drop] *= 1.0
    env*=np.clip((sec-drop)/.035,0,1).astype(np.float32) if drop<.1 else 1
    silence=(sec>=drop-.37)&(sec<drop)
    env[silence]=0
    env[sec>=end] *= np.maximum(0,1-(sec[sec>=end]-end)/max(.01,dur-end))
    return np.tanh(track*1.45)*env[:,None]


def click(freq=1380,dur=.17):
    t=seconds(dur)
    return .55*np.sin(2*np.pi*freq*t)*np.exp(-t*34)


def swoosh(dur=.39,up=True):
    t=seconds(dur)
    n=RNG.standard_normal(len(t))
    high=n-np.convolve(n,np.ones(21)/21,mode='same')
    x=np.sin(np.pi*t/dur)**2
    if not up: x=x[::-1]
    return high*x*.24


def make_sfx(dur:int, drop:float, price:float, end:float) -> np.ndarray:
    out=np.zeros((int(dur*SR),2),dtype=np.float32)
    # TV snow and low phone vibration start on frame zero; no licensed foley.
    t=seconds(min(1.15,dur))
    noise=RNG.standard_normal(len(t))*.045*(1-t/max(1.15,dur))
    add(out,0,noise,1,pan=-.18)
    add(out,.12,np.sin(2*np.pi*96*t)*np.sin(2*np.pi*33*t)*np.exp(-t*3),.065,pan=.42)
    events=( [(5.0,1200),(5.24,1550),(8.1,900),(12.0,450),(13.25,220)]
             if dur==59 else [(1.6,1250),(2.4,1700)] )
    for when,f in events:
        add(out,when,click(f),.55,pan=(-.32 if int(when*10)%2 else .32))
    add(out,drop,swoosh(.50),.55,pan=0)
    add(out,drop,kick(),.74)
    add(out,drop+.10,click(2500),.32)
    add(out,price,click(1160,.44),.80,pan=.15)
    if dur==59:
        add(out,26.0,click(870,.23),.29)
        for when in (18.5,23.7,28.5,33.2,35.3):
            add(out,when,swoosh(.25),.25,pan=.27)
        add(out,12.12,hand(110),.31)
        for i in range(7): add(out,48.10+i*.32,click(650+i*35,.12),.22,pan=(-.35 if i%2 else .35))
    elif dur==30:
        for when in (6.7,9.8,12,20.8): add(out,when,swoosh(.25),.25)
        for i in range(7): add(out,21.3+i*.33,click(780,.12),.19)
    else:
        for when in (2.8,7.7,9.15): add(out,when,swoosh(.25),.25)
    for when in (end-.60,end-.01): add(out,when,click(690 if when<end-.05 else 1100,.19),.31)
    if dur==59:
        out[round(13.64*SR):round(14.00*SR)] = 0
    return np.tanh(out)


def write24(path:Path, sound:np.ndarray):
    path.parent.mkdir(parents=True,exist_ok=True)
    ac=1 if sound.ndim==1 else sound.shape[1]
    cmd=['ffmpeg','-hide_banner','-v','error','-y','-f','f32le','-ar',str(SR),
         '-ac',str(ac),'-i','pipe:0','-c:a','pcm_s24le',str(path)]
    subprocess.run(cmd,input=np.asarray(sound,dtype='<f4').tobytes(),check=True)


def normalize_mix(raw:Path, result:Path):
    base='loudnorm=I=-14:TP=-1.6:LRA=9'
    cmd=['ffmpeg','-hide_banner','-v','info','-i',str(raw),'-af',base+':print_format=json',
         '-f','null','-']
    probe=subprocess.run(cmd,capture_output=True,text=True,check=True)
    match=re.findall(r'\{\s*"input_i".*?\}',probe.stderr,re.S)
    if not match: raise RuntimeError('EBU R128 data missing: '+probe.stderr[-1300:])
    stats=json.loads(match[-1])
    options=(base+':'+':'.join(f'{k}={stats[v]}' for k,v in [
        ('measured_I','input_i'),('measured_TP','input_tp'),
        ('measured_LRA','input_lra'),('measured_thresh','input_thresh'),
        ('offset','target_offset')])+':linear=true')
    cmd=['ffmpeg','-hide_banner','-v','error','-y','-i',str(raw),'-af',options,
         '-ar',str(SR),'-ac','2','-c:a','pcm_s24le',str(result)]
    subprocess.run(cmd,check=True)
    return stats


def main():
    summary={}
    for version,drop,price,end in [('59',14.0,42.0,58.40),('30',3.31,17.70,29.36),('15',2.80,7.70,14.42)]:
        length=int(version)
        voice=edit_voice(version)
        music=make_music(length,drop,end)
        effects=make_sfx(length,drop,price,end)
        # Set the un-ducked musical bed close to speech in perceived energy,
        # then duck around spoken words by ~10–12 dB (measured/R128 later).
        t0=14*SR if version=='59' else max(0,round(drop*SR))
        rms=np.sqrt(np.mean(music[t0:]**2))+.00001
        music *= .085/rms
        music=np.clip(music,-.95,.95)
        # Smooth music ducking in 20-ms blocks from actual edited speech.
        block=round(.02*SR)
        levels=np.array([np.sqrt(np.mean(voice[i:i+block]**2)) for i in range(0,len(voice),block)])
        threshold=np.clip(levels/.022,0,1)
        kernel=np.ones(17)/17
        duck=1-np.convolve(threshold,kernel,mode='same')*.50
        duck=np.repeat(duck,block)[:len(voice)]
        music*=duck[:,None]*.52
        effects*=.45
        if version=='59':
            write24(STEMS/'VOIX_59S.wav',voice)
            write24(STEMS/'MUSIQUE_59S.wav',music)
            write24(STEMS/'EFFETS_59S.wav',effects)
        else:
            write24(CACHE/f'voix_{version}.wav',voice)
            write24(CACHE/f'musique_{version}.wav',music)
            write24(CACHE/f'effets_{version}.wav',effects)
        mixed=np.repeat(voice[:,None],2,axis=1)*.83+music+effects
        mixed=np.tanh(mixed*1.07)/1.07
        raw=CACHE/f'mix_{version}_raw.wav'
        normalized=CACHE/f'mix_{version}.wav'
        write24(raw,mixed)
        stats=normalize_mix(raw,normalized)
        summary[version]={'duration':length,'normalized_wav':str(normalized.relative_to(ROOT)),
                          'measured_input':stats,'voice_peak':float(np.max(np.abs(voice))),
                          'music_rms':float(np.sqrt(np.mean(music**2)))}
        print(f'Normalized {version}s -> {normalized}  (input {stats["input_i"]} LUFS / TP {stats["input_tp"]})')
    (CACHE/'report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
