"""59.000 s master (landscape) and reflows. Source: client's new 8-scene brief.

Times / displayed prices differ intentionally from the previous "Ton écran"
version. This file is the editable timeline and source of the SRT captions.
"""
from pathlib import Path

FPS = 30
DURATION = 59.0
SCENES = {
    '59': [
        (0.0, 5.0, 'hook'),
        (5.0, 11.0, 'problem'),
        (11.0, 17.0, 'reveal'),
        (17.0, 29.0, 'content'),
        (29.0, 37.0, 'audio'),
        (37.0, 47.0, 'prices'),
        (47.0, 54.0, 'choice'),
        (54.0, 59.0, 'cta'),
    ]
}

# Same cues for the three 59-s ratios, plus a no-voice (no burned subtitles)
# composition. Two lines maximum; shot / line starts follow the eight voice takes.
CAPTIONS = {'59': [
    (0.20, 2.94, 'Tu cherches toujours quelque chose\nde nouveau à regarder ?'),
    (5.23, 8.90, 'Quand le choix est limité,\nle divertissement perd vite son goût.'),
    (11.08, 13.64, 'Découvre MISSA TV 360 :'),
    (13.64, 16.79, 'ton univers de divertissement,\nà portée de main !'),
    (17.21, 19.58, 'Des milliers de films, séries,'),
    (19.58, 22.04, 'documentaires et mangas,'),
    (25.02, 28.08, 'sans oublier des centaines\nde chaînes télévisées.'),
    (29.20, 32.27, 'Et pour écouter, retrouve aussi\ndes podcasts'),
    (33.06, 35.28, 'et des milliers de stations radio.'),
    (37.24, 39.58, 'Et tout ça, avec une formule'),
    (39.58, 42.26, 'à deux mille francs CFA par mois,'),
    (42.26, 45.36, 'ou dix mille francs CFA\npour toute l’année.'),
    (47.31, 49.28, 'Fais le choix de la diversité.'),
    (50.68, 52.76, 'Ton divertissement mérite mieux !'),
    (54.12, 58.30, 'Télécharge MISSA TV 360\ndès maintenant !'),
]}


def srt_time(t:float)->str:
    ms=round(t*1000)
    h,ms=divmod(ms,3600000)
    m,ms=divmod(ms,60000)
    s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def write_srt(path:Path):
    cues=CAPTIONS['59']
    blocks=[f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}' for i,(a,b,txt) in enumerate(cues,1)]
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n\n'.join(blocks)+'\n',encoding='utf-8')
    print(path,len(cues),'cues')


if __name__=='__main__':
    repo=Path(__file__).resolve().parents[2]
    write_srt(repo/'livrables/MISSA_TV_360_PUB_59S_fr.srt')
