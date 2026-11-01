"""Mux du master « Le monde s'ouvre ».

Depuis la racine du dépôt : python3 projects/missa-tv-360-portail/mix.py
Entrées : .cache/rendus/missa-tv-360-portail-silent.mp4,
          .cache/vo10/s1..s6.mp3 et .cache/portail-audio/{music,sfx-bed}.wav.
Sortie  : livrables/missa-tv-360-portail.mp4.
"""
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[2]
video = repo/'.cache/rendus/missa-tv-360-portail-silent.mp4'
voices = [repo/f'.cache/vo10/s{i}.mp3' for i in range(1,7)]
music = repo/'.cache/portail-audio/music.wav'
sfx = repo/'.cache/portail-audio/sfx-bed.wav'
out = repo/'livrables/missa-tv-360-portail.mp4'
missing = [str(p.relative_to(repo)) for p in (video,*voices,music,sfx) if not p.exists()]
if missing:
    sys.exit('Médias absents (générer sound.py et la VO avant le mix) :\n'+'\n'.join(missing))

audio = []
for i,ms in enumerate((110,3310,8230,15240,25360,32280),start=1):
    audio.append(f'[{i}:a]highpass=f=76,volume=1.02,adelay={ms}|{ms},aformat=channel_layouts=stereo[v{i}]')
audio.append('[7:a]volume=1.12[m]')
audio.append('[8:a]volume=.73[e]')
audio.append(''.join(f'[v{i}]' for i in range(1,7))+
             '[m][e]amix=inputs=8:normalize=0,volume=1.30,alimiter=limit=.78:attack=5:release=80:level=0,'+
             'apad,afade=t=out:st=36.72:d=0.28,atrim=0:37,asetpts=PTS-STARTPTS[aout]')
inputs = [video,*voices,music,sfx]
cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y']
for p in inputs:
    cmd += ['-i',str(p)]
cmd += ['-filter_complex',';'.join(audio),'-map','0:v:0','-map','[aout]',
        '-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-ac','2',
        '-movflags','+faststart','-metadata','title=Missa TV 360 — Le monde s’ouvre',
        '-metadata','comment=Portrait · 37 s · 6 séquences · box NET','-t','37',str(out)]
out.parent.mkdir(parents=True,exist_ok=True)
print('Mixage du master :',out,flush=True)
subprocess.run(cmd,check=True)
print('OK —',round(out.stat().st_size/1024/1024,1),'Mo')
