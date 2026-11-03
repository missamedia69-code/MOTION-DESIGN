"""Rebuild, mux and QC the new MISSA TV 360 59-second mock-up.

python3 projects/missa-tv-360-diversite/build.py --render  # source → all files
python3 projects/missa-tv-360-diversite/build.py --check   # inspect exports only

Unlike the repository's generic `md` templates, this authored film uses its
own Pillow/Python shot renderer. Video is 59 seconds exactly at 30 fps and
consists of 1,770 individually composed frames in each aspect ratio.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image
from timeline import CAPTIONS,DURATION,FPS,SCENES,write_srt

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CACHE=ROOT/'.cache/diversite-video'
AUDIO=ROOT/'.cache/diversite-audio'
OUT=ROOT/'livrables'
MOVIES={
    'landscape':('MISSA_TV_360_PUB_59S_16x9.mp4',(1920,1080)),
    'portrait':('MISSA_TV_360_PUB_59S_9x16.mp4',(1080,1920)),
    'square':('MISSA_TV_360_PUB_59S_1x1.mp4',(1080,1080)),
    'no_voice':('MISSA_TV_360_PUB_59S_16x9_SANS_VOIX.mp4',(1920,1080)),
}
STEMS=('VOIX_59S.wav','MUSIQUE_59S.wav','EFFETS_59S.wav')


def run(*args):
    print('>',*args,flush=True)
    subprocess.run(args,cwd=ROOT,check=True)


def inspect(path):
    proc=subprocess.run(['ffprobe','-v','error','-show_entries',
        'format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels,duration',
        '-of','json',str(path)],check=True,capture_output=True,text=True)
    return json.loads(proc.stdout)


def mux(video,audio,destination,no_voice=False):
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-i',str(audio),
         '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000']
    # AAC can add about 0.5 dB of inter-sample overshoot to the instrumental
    # mix. Preserve generous peak headroom in the no-voice localisation edit.
    if no_voice:cmd+=['-af','volume=-0.7dB']
    cmd+=['-t','59','-movflags','+faststart',str(destination)]
    run(*cmd)


def rebuild():
    CACHE.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    write_srt(OUT/'MISSA_TV_360_PUB_59S_fr.srt')
    run(sys.executable,str(HERE/'sound.py'))
    for ratio in ('landscape','portrait','square'):
        video=CACHE/f'silent-{ratio}.mp4'
        run(sys.executable,str(HERE/'film.py'),'--ratio',ratio,'--crf','22','--output',str(video))
        mux(video,AUDIO/'mix_59.wav',OUT/MOVIES[ratio][0])
    no_captions=CACHE/'silent-landscape-no-captions.mp4'
    run(sys.executable,str(HERE/'film.py'),'--ratio','landscape','--without-captions',
        '--crf','22','--output',str(no_captions))
    mux(no_captions,AUDIO/'instrumental_59.wav',OUT/MOVIES['no_voice'][0],no_voice=True)
    from film import Film
    Film('landscape',False).render(14.3).save(OUT/'MISSA_TV_360_COUVERTURE_16x9.jpg',quality=93,optimize=True)


def check():
    all_info={}
    for key,(filename,(w,h)) in MOVIES.items():
        path=OUT/filename
        assert path.exists(),f'Missing render: {path}'
        info=inspect(path)
        assert abs(float(info['format']['duration'])-DURATION)<.001,filename
        stream=next(s for s in info['streams'] if s['codec_type']=='video')
        audio=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (stream['width'],stream['height'])==(w,h),filename
        assert stream['r_frame_rate']=='30/1',filename
        assert int(stream['nb_frames'])==1770,filename
        assert stream['codec_name']=='h264' and audio['codec_name']=='aac',filename
        assert abs(float(audio['duration'])-DURATION)<.001,filename
        all_info[key]={'path':str(path.relative_to(ROOT)),'width':w,'height':h,
            'seconds':float(info['format']['duration']),'fps':FPS,'frames':int(stream['nb_frames']),
            'video_codec':stream['codec_name'],'audio_codec':audio['codec_name'],
            'bytes':path.stat().st_size,'burned_subtitles':key!='no_voice'}
    for name in STEMS:
        path=OUT/'PISTES_SEPAREES_59S'/name
        info=inspect(path)
        assert abs(float(info['format']['duration'])-DURATION)<.001,name
        audio=info['streams'][0]
        assert audio['codec_name']=='pcm_s24le' and audio['sample_rate']=='48000',name
        all_info[name]={'seconds':DURATION,'sample_rate':48000,'channels':audio['channels']}
    srt=(OUT/'MISSA_TV_360_PUB_59S_fr.srt').read_text(encoding='utf-8')
    assert len(CAPTIONS['59'])==15 and srt.count(' --> ')==15
    assert not any('XAF' in text or '7 mois' in text for text in srt.splitlines())
    assert [a for a,_,_ in SCENES['59']]==[0,5,11,17,29,37,47,54]
    assert SCENES['59'][-1][1]==DURATION
    with Image.open(OUT/'MISSA_TV_360_COUVERTURE_16x9.jpg') as cover:
        assert cover.size==(1920,1080)
    report={'status':'exports techniquement valides, MAQUETTES NON AUTORISÉES POUR DIFFUSION',
        'duration_seconds':DURATION,'fps':FPS,'scene_boundaries_seconds':[0,5,11,17,29,37,47,54,59],
        'captions':len(CAPTIONS['59']),'srt':'livrables/MISSA_TV_360_PUB_59S_fr.srt',
        'requested_prices':['2 000 FCFA / mois','10 000 FCFA / an'],
        'check_before_publication':['prix et conditions','volumes du catalogue (milliers/centaines)',
            'droits de diffusion des affiches visibles dans les captures','logo et identité graphique officiels',
            'lien/plateformes de téléchargement','licence commerciale de la voix synthétisée et des photographies'],
        'movies':all_info}
    path=OUT/'MISSA_TV_360_VALIDATION_59S.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name in MOVIES:print('VALIDÉ',name,all_info[name]['width'],'×',all_info[name]['height'],'/ 59.000 s / 30 fps')
    print('Rapport QC',path)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--render',action='store_true',help='Build all outputs and verify them')
    mode.add_argument('--check',action='store_true',help='Validate existing media only')
    args=p.parse_args()
    if args.render:rebuild()
    check()
