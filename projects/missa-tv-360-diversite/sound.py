"""New 59-second female-voice commercial mix with original instrumental music.

Use selected voice-09 takes in assets/voice/. The available TTS model does not
support fr-CM, so neither accent provenance nor commercial voice rights are
asserted. Source score and SFX synthesis reused from the prior editable project,
with NEW timings, new foley events and no savings/low-bandwidth claims.

python3 projects/missa-tv-360-diversite/sound.py
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PROJECT=Path(__file__).resolve().parent
OLD=ROOT/'projects/missa-tv-360-ton-ecran/audio.py'
spec=importlib.util.spec_from_file_location('missa_score_library',OLD)
base=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)
SR=base.SR
DURATION=59
N=DURATION*SR
CACHE=ROOT/'.cache/diversite-audio'
STEMS=ROOT/'livrables/PISTES_SEPAREES_59S'
CACHE.mkdir(parents=True,exist_ok=True)
STEMS.mkdir(parents=True,exist_ok=True)


def decode(name:str)->np.ndarray:
    p=PROJECT/'assets/voice'/f'{name}.mp3'
    if not p.exists():raise FileNotFoundError(p)
    proc=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(p),
        '-ac','1','-ar',str(SR),'-f','f32le','pipe:1'],capture_output=True,check=True)
    return np.frombuffer(proc.stdout,dtype='<f4').copy()


def make_voice()->np.ndarray:
    voice=np.zeros(N,dtype=np.float32)
    filenames=('01-accroche','02-probleme','03-revelation','04-contenus',
               '05-audio','06-prix','07-conversion','08-cta')
    sources={name:decode(name) for name in filenames}
    schedule=[]

    def place(name:str,at:float,lo:float=0,hi:float|None=None,
              speed:float=1,gain:float=1.0):
        src=sources[name]
        clip=src[round(lo*SR):round(hi*SR) if hi is not None else None]
        if speed!=1:clip=base.tempo(clip,speed)
        clip=base.fade(clip)
        base.add(voice,at,clip,gain)
        end=at+len(clip)/SR
        schedule.append({'name':name,'at':round(at,3),'end':round(end,3),'tempo':speed})
        print(f'  {name:<18} {at:5.2f}–{end:5.2f}  speed {speed:.2f}')

    # Deliberate breathing spaces and a brisk, confident opening. All words
    # remain the owner's supplied script, with 360 pronounced as spoken French.
    place('01-accroche',.20,gain=1.0)
    place('02-probleme',5.24,gain=1.0)
    place('03-revelation',11.06,speed=1.055,gain=1.02)
    # Cut only on silence between "mangas" and "sans oublier", so TV Direct
    # has its own 25–28 s beat, rather than being spoken over documentary tabs.
    place('04-contenus',17.22,0,3.72,speed=.88,gain=1.03)
    place('04-contenus',25.02,4.12,6.49,speed=.88,gain=1.03)
    place('05-audio',29.20,0,2.78,gain=1.0)
    place('05-audio',33.04,3.12,4.78,speed=.90,gain=1.0)
    place('06-prix',37.23,gain=1.04)
    place('07-conversion',47.31,0,1.79,gain=1.03)
    place('07-conversion',50.62,2.55,4.31,speed=.90,gain=1.07)
    place('08-cta',54.12,gain=1.10)
    # Musical pickup before the reveal, not a hard truncation of speech.
    (CACHE/'voix-placement.json').write_text(json.dumps(schedule,ensure_ascii=False,indent=2),encoding='utf-8')
    return voice


def make_music()->np.ndarray:
    track=base.make_music(DURATION,11.0,58.45)
    sec=np.arange(N)/SR
    # New narrative arc: search → pause → bright full ensemble → prices/CTA.
    dynamics=np.interp(sec,[0,.75,4.6,5.0,9.7,10.63,10.98,11.20,17,29,37,42,47,53,54,57.5,58.45,59],
        [.14,.43,.64,.56,.67,0,0,1.05,.98,1.05,1.09,1.12,1.03,1.14,1.20,1.23,.96,0])
    track*=dynamics[:,None]
    return track


def make_fx()->np.ndarray:
    track=np.zeros((N,2),dtype=np.float32)
    def hit(at,freq,level=.45,pan=0):base.add(track,at,base.click(freq,.20),level,pan)
    def sweep(at,level=.28):base.add(track,at,base.swoosh(.31),level)
    # Genuine foley synthesis: zapping, search, reveal, chapter swipes and price.
    for i,at in enumerate((.02,.58,1.14,2.10,3.02,4.04)):
        hit(at,780+(i%3)*270,.14,pan=-.38 if i%2 else .38)
    hit(5.06,1020,.30)
    sweep(10.84,.33)
    base.add(track,11.00,base.swoosh(.54),.62)
    base.add(track,11.00,base.kick(),.60)
    hit(11.07,1670,.41)
    for at in (17.00,20.80,23.90,26.20,29.00,33.10,47.0,50.65):sweep(at,.23)
    for at,f in ((37.0,1040),(42.0,1320)):
        hit(at,f,.62)
        base.add(track,at+.06,base.guitar(f*.38),.18)
    # Soft radio tuning and original, brief final sonic signature.
    hit(29.14,600,.24)
    hit(29.27,850,.17)
    base.add(track,54.00,base.swoosh(.40),.40)
    for i,note in enumerate((587.33,739.99,880.0)):
        base.add(track,58.35+i*.10,base.guitar(note),.24+i*.05)
    return np.tanh(track)


def duck_music(music:np.ndarray,voice:np.ndarray)->np.ndarray:
    music=music.copy()
    rms=np.sqrt(np.mean(music[11*SR:54*SR]**2))+.00001
    music*=.106/rms
    music=np.clip(music,-.92,.92)
    block=round(.02*SR)
    levels=np.array([np.sqrt(np.mean(voice[i:i+block]**2)) for i in range(0,N,block)])
    voiced=np.clip(levels/.023,0,1)
    curve=1-np.convolve(voiced,np.ones(15)/15,mode='same')*.51
    music*=np.repeat(curve,block)[:N,None]*.48
    return music


def main():
    voice=make_voice()
    music_source=make_music()
    fx=make_fx()*.50
    music=duck_music(music_source,voice)
    base.write24(STEMS/'VOIX_59S.wav',voice)
    base.write24(STEMS/'MUSIQUE_59S.wav',music)
    base.write24(STEMS/'EFFETS_59S.wav',fx)
    # Base mix and instrumental localisation mix are independently mastered.
    full=np.tanh((np.repeat(voice[:,None],2,axis=1)*.85+music+fx)*1.06)/1.06
    no_voice=np.tanh((music_source*.58+fx)*1.09)/1.09
    for name,content in (('mix_59',full),('instrumental_59',no_voice)):
        raw=CACHE/f'{name}-raw.wav'
        dest=CACHE/f'{name}.wav'
        base.write24(raw,content)
        info=base.normalize_mix(raw,dest)
        print(name,':',dest,'input loudness',info['input_i'],'LUFS')
    print('59.000 s / 48 kHz / three PCM24 stems + full + instrumental master')

if __name__=='__main__':main()
