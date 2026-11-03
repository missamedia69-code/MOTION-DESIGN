"""59-second mux: keep the approved soundtrack, replace only two spoken lines.

This edit preserves the previously appreciated narration/music elsewhere. The
old mixed soundtrack is retrieved from commit c7ee4ad if the temporary cache
has been reset; no old video remains in today's livrables/ directory.

Inputs: .cache/rendus/missa-tv-360-portail-product-silent.mp4,
        .cache/vo59-revision/{s4a-short,s4b-short}.mp3,
        .cache/portail-audio/{music,sfx-bed}.wav (from sound.py).
Output: livrables/missa-tv-360-portail.mp4 (exactly 59.000 seconds).
"""
from pathlib import Path
import subprocess
import sys

repo=Path(__file__).resolve().parents[2]
cache=repo/'.cache/revision-tele-doc'
cache.mkdir(parents=True,exist_ok=True)
video=repo/'.cache/rendus/missa-tv-360-portail-product-silent.mp4'
old_audio=cache/'voice-and-music-before.wav'
voice_docs=repo/'.cache/vo59-revision/s4a-short.mp3'
voice_tv=repo/'.cache/vo59-revision/s4b-short.mp3'
music=repo/'.cache/portail-audio/music.wav'
sfx=repo/'.cache/portail-audio/sfx-bed.wav'
out=repo/'livrables/missa-tv-360-portail.mp4'

if not old_audio.exists():
    # Exact predecessor master; retrieved locally from Git history, never from a
    # second file in livrables/. Run from any cwd, using the repository worktree.
    source=cache/'predecessor-master.mp4'
    with source.open('wb') as f:
        subprocess.run(['git','-C',str(repo),'show',
                        'c7ee4ad:livrables/missa-tv-360-portail.mp4'],stdout=f,check=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
                    '-i',str(source),'-vn','-c:a','pcm_s16le',str(old_audio)],check=True)

missing=[str(p.relative_to(repo)) for p in (video,old_audio,voice_docs,voice_tv,music,sfx) if not p.exists()]
if missing:
    sys.exit('Sources manquantes :\n'+'\n'.join(missing))

# Short complementary fades keep the original mix intact outside 29–40.6 s.
# Previous spoken lines start at 29.13 / 35.23 and finish before 40.27; the
# unchanged s4c voice starts at 40.64, once the old mix is fully restored.
old_gain="if(lt(t,28.94),1,if(lt(t,29.11),(29.11-t)/0.17,if(lt(t,40.27),0,if(lt(t,40.60),(t-40.27)/0.33,1))))"
new_gain="if(lt(t,28.94),0,if(lt(t,29.11),(t-28.94)/0.17,if(lt(t,40.27),1,if(lt(t,40.60),(40.60-t)/0.33,0))))"
fx_gain="if(lt(t,28.94),0,if(lt(t,29.11),(t-28.94)/0.17,if(lt(t,40.28),1,if(lt(t,40.49),(40.49-t)/0.21,0))))"
filters=[
    f"[1:a]volume='{old_gain}':eval=frame[aold]",
    '[2:a]highpass=f=77,volume=1.3312,adelay=29130|29130,aformat=channel_layouts=stereo[doc] ',
    '[3:a]highpass=f=77,volume=1.3312,adelay=35230|35230,aformat=channel_layouts=stereo[tv] ',
    f"[4:a]volume=1.4464,volume='{new_gain}':eval=frame[bed]",
    f"[5:a]volume=.9088,volume='{fx_gain}':eval=frame[fx]",
    '[aold][doc][tv][bed][fx]amix=inputs=5:normalize=0,'
    'alimiter=limit=.72:attack=5:release=80:level=0,'
    'apad,afade=t=out:st=58.72:d=0.28,atrim=0:59,asetpts=PTS-STARTPTS[aout]'
]
inputs=[video,old_audio,voice_docs,voice_tv,music,sfx]
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
for p in inputs: cmd.extend(['-i',str(p)])
cmd.extend(['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[aout]',
            '-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-ac','2',
            '-movflags','+faststart','-metadata','title=Missa TV 360 — L’appli en vrai',
            '-metadata','comment=59 s · TV Direct et documentaires · sans images de stock',
            '-t','59',str(out)])
out.parent.mkdir(parents=True,exist_ok=True)
print('Mixage du master révisé 59 s :',out,flush=True)
subprocess.run(cmd,check=True)
print('OK —',round(out.stat().st_size/1024/1024,1),'Mo')
