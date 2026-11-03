"""Mux the five frame-exact video masters with the measured −14 LUFS mixes."""
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.cache/ton-ecran-video'
AUDIO=ROOT/'.cache/ton-ecran-audio'
OUT=ROOT/'livrables'
EXPORTS=[
    ('59','portrait','9x16'),('59','landscape','16x9'),('59','square','1x1'),
    ('30','portrait','9x16'),('15','portrait','9x16'),
]


def cmdout(args):return subprocess.check_output(args,text=True)


def main():
    report=[]
    for duration,ratio,label in EXPORTS:
        silent=CACHE/f'{duration}-{ratio}-silent.mp4'
        mix=AUDIO/f'mix_{duration}.wav'
        out=OUT/f'MISSA_TV_360_PUB_{duration}S_{label}.mp4'
        if not silent.is_file() or not mix.is_file():
            raise FileNotFoundError(f'Video/audio missing for {duration} {ratio}: {silent}, {mix}')
        ff=['ffmpeg','-hide_banner','-v','error','-y','-i',str(silent),'-i',str(mix),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k',
            '-ar','48000','-ac','2','-af',f'atrim=0:{duration},asetpts=PTS-STARTPTS',
            '-t',duration,'-movflags','+faststart',
            '-metadata',f'title=Missa TV 360 — Ton écran mérite mieux ({duration} s, {label})',
            '-metadata','comment=Maquette : lien, QR, identité, conditions et droits des voix à confirmer',
            str(out)]
        subprocess.run(ff,check=True)
        streams=json.loads(cmdout(['ffprobe','-v','error','-show_entries',
            'format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,bit_rate',
            '-of','json',str(out)]))
        video=next(s for s in streams['streams'] if s['codec_name']=='h264')
        audio=next(s for s in streams['streams'] if s['codec_name']=='aac')
        assert video['nb_frames']==str(int(duration)*30), (out,video)
        assert video['r_frame_rate']=='30/1', (out,video)
        assert audio['sample_rate']=='48000', (out,audio)
        assert abs(float(streams['format']['duration'])-int(duration))<.001,(out,streams['format'])
        report.append({'file':str(out.relative_to(ROOT)),
                       'duration':float(streams['format']['duration']),
                       'frames':video['nb_frames'],'video':f"{video['width']}×{video['height']}",
                       'video_bitrate_bps':int(video.get('bit_rate',0)),
                       'audio_bitrate_bps':int(audio.get('bit_rate',0)),
                       'bytes':int(streams['format']['size'])})
        print(f"{out.name}: {report[-1]['duration']:.3f}s · {report[-1]['frames']} frames · "
              f"{video['width']}×{video['height']} · {report[-1]['bytes']/1e6:.1f} MB")
    path=ROOT/'.cache/ton-ecran-video/exports.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':main()
