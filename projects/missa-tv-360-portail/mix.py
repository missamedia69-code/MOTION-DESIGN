"""Mux du master 59 secondes « Le monde s'ouvre ».

Depuis la racine du dépôt : python3 projects/missa-tv-360-portail/mix.py
Entrées : .cache/rendus/missa-tv-360-portail-silent.mp4,
          .cache/vo59/s1,s2,s3a,s3b,s4a,s4b,s4c,s5,s6.mp3 et
          .cache/portail-audio/{music,sfx-bed}.wav.
Sortie  : livrables/missa-tv-360-portail.mp4 (remplace le master 37 s).
"""
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[2]
video = repo/'.cache/rendus/missa-tv-360-portail-silent.mp4'
stems = ('s1','s2','s3a','s3b','s4a','s4b','s4c','s5','s6')
starts = (300,6200,16350,22450,29080,35520,40640,46200,53220)
voices = [repo/f'.cache/vo59/{stem}.mp3' for stem in stems]
music = repo/'.cache/portail-audio/music.wav'
sfx = repo/'.cache/portail-audio/sfx-bed.wav'
out = repo/'livrables/missa-tv-360-portail.mp4'
missing = [str(p.relative_to(repo)) for p in (video,*voices,music,sfx) if not p.exists()]
if missing:
    sys.exit('Médias absents (générer sound.py et la VO avant le mix) :\n'+'\n'.join(missing))

audio = []
for i,(stem,ms) in enumerate(zip(stems,starts),start=1):
    # The only small tempo adjustment keeps the longer problem sentence in its 10 s chapter.
    tempo = 'atempo=1.12,' if stem == 's2' else ''
    audio.append(f'[{i}:a]{tempo}highpass=f=76,volume=1.02,adelay={ms}|{ms},'
                 f'aformat=channel_layouts=stereo[v{i}]')
audio.append('[10:a]volume=1.12[m]')
audio.append('[11:a]volume=.73[e]')
audio.append(''.join(f'[v{i}]' for i in range(1,len(voices)+1))+
             '[m][e]amix=inputs=11:normalize=0,volume=1.30,'+
             'alimiter=limit=.72:attack=5:release=80:level=0,'+
             'apad,afade=t=out:st=58.72:d=0.28,atrim=0:59,asetpts=PTS-STARTPTS[aout]')
inputs = [video,*voices,music,sfx]
cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y']
for p in inputs:
    cmd += ['-i',str(p)]
cmd += ['-filter_complex',';'.join(audio),'-map','0:v:0','-map','[aout]',
        '-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-ac','2',
        '-movflags','+faststart','-metadata','title=Missa TV 360 — Le monde s’ouvre',
        '-metadata','comment=Portrait · 59 s · 6 chapitres · box NET','-t','59',str(out)]
out.parent.mkdir(parents=True,exist_ok=True)
print('Mixage du master 59 s :',out,flush=True)
subprocess.run(cmd,check=True)
print('OK —',round(out.stat().st_size/1024/1024,1),'Mo')
