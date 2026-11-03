"""Independently composed 59.000 s / 25 fps films: landscape, portrait, square.

Storyboard data and captions: timeline.py. All product UI panels below are
unmodified screenshots of the supplied application, not reconstructed screens.
Photographs are fictional, freshly generated for this preview. Graphic marks,
prices, captions and branding placeholders are editable Pillow primitives.
The headline figures and third-party poster rights require client validation.

Preview shots:
 python3 projects/missa-tv-360-diversite/film.py --ratio landscape --at 1.2,6.5,14,19,22,25,32,39,44,51,56
Full silent edit:
 python3 projects/missa-tv-360-diversite/film.py --ratio landscape --output .cache/diversite-video/landscape.mp4
"""
from __future__ import annotations

import argparse
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from timeline import SCENES,CAPTIONS,DURATION,FPS

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CLIENT=ROOT/'projects/missa-tv-360-ton-ecran/assets/app'
CACHE=ROOT/'.cache/diversite-video'
CACHE.mkdir(parents=True,exist_ok=True)
FONTS={
    'display':ROOT/'projects/missa-tv-360-ton-ecran/fonts/Montserrat-Black.ttf',
    'bold':ROOT/'projects/missa-tv-360-ton-ecran/fonts/Montserrat-ExtraBold.ttf',
    'body':ROOT/'projects/missa-tv-360-ton-ecran/fonts/Nunito-Variable.ttf',
}
SIZES={'landscape':(1920,1080),'portrait':(1080,1920),'square':(1080,1080)}
INK=(7,13,19)
WHITE=(251,250,242)
MUTED=(180,197,197)
LIME=(245,192,14) # moodboard sampled from customer screenshot; NOT official color
CYAN=(85,216,203)

@lru_cache(maxsize=100)
def f(kind,size):return ImageFont.truetype(str(FONTS[kind]),int(size))

@lru_cache(maxsize=20)
def source(path):return Image.open(path).convert('RGB')

@lru_cache(maxsize=70)
def screenshot(name,w,h):
    src=source(CLIENT/name)
    # Original pixels only. Letterbox, don't fabricate missing catalogue pages.
    return ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)

@lru_cache(maxsize=28)
def photo(name,w,h):
    path=HERE/'assets/photos'/name
    # Additional margin permits gentle movement without scaling each frame.
    return ImageOps.fit(source(path),(w+36,h+36),method=Image.Resampling.LANCZOS,centering=(.45,.5))

@lru_cache(maxsize=30)
def mask(w,h,r):
    im=Image.new('L',(w,h),0)
    ImageDraw.Draw(im).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255)
    return im


def clamp(v,lo=0,hi=1):return min(hi,max(lo,v))
def ease(v):v=clamp(v);return v*v*(3-2*v)


class Film:
    def __init__(self,ratio,subtitles=True):
        self.ratio=ratio;self.w,self.h=SIZES[ratio];self.subtitles=subtitles
        self.wide=ratio=='landscape';self.vertical=ratio=='portrait';self.square=ratio=='square'
        self.m=116 if self.wide else (74 if self.square else 78)
        self.top=73 if self.wide else (54 if self.square else 115)
        self.sub_top=867 if self.wide else (861 if self.square else 1585)
        self.sub_baseline=928 if self.wide else (911 if self.square else 1640)
        self.tag_y=1040 if self.wide else (1040 if self.square else 1840)
        self.base={theme:self._background(theme) for theme in ('search','reveal','content','sound','price','choice','end')}

    def _background(self,theme):
        w,h=self.w,self.h
        palette={
            'search':((6,14,23),(17,61,64),(.25,.47),(.43,.66)),
            'reveal':((6,18,24),(11,100,79),(.61,.38),(.55,.56)),
            'content':((7,14,26),(20,75,89),(.70,.40),(.49,.70)),
            'sound':((9,18,31),(17,63,119),(.36,.55),(.54,.63)),
            'price':((12,15,20),(86,57,14),(.54,.35),(.65,.58)),
            'choice':((6,19,25),(21,91,84),(.27,.51),(.51,.60)),
            'end':((5,14,19),(12,113,85),(.53,.45),(.56,.55)),
        }
        bg,light,center,spread=palette[theme]
        yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
        xx/=w;yy/=h
        glow=np.exp(-(((xx-center[0])/spread[0])**2+((yy-center[1])/spread[1])**2)*2.5)
        glow2=np.exp(-(((xx-.10)/.66)**2+((yy-.96)/.4)**2)*3.5)*.13
        out=np.empty((h,w,3),dtype=np.uint8)
        for i in range(3):out[:,:,i]=np.clip(bg[i]+(light[i]-bg[i])*(glow*.65+glow2),0,255)
        del xx,yy,glow,glow2
        image=Image.fromarray(out,'RGB')
        d=ImageDraw.Draw(image,'RGBA')
        gap=91 if self.wide else 93
        for x in range(gap//2,w,gap):d.line((x,0,x,h),fill=(166,220,213,9),width=1)
        for y in range(gap//2,h,gap):d.line((0,y,w,y),fill=(166,220,213,9),width=1)
        return image

    def t(self,d,xy,text,px,color=WHITE,kind='bold',anchor=None,stroke=0):
        d.text((round(xy[0]),round(xy[1])),text,font=f(kind,px),fill=color,anchor=anchor,
               stroke_width=stroke,stroke_fill=INK)

    def bar(self,d,x,y,width=84,color=LIME,height=6):d.rounded_rectangle((x,y,x+width,y+height),radius=height//2,fill=color)

    def header(self,d,t,section,subsection=''):
        x=self.m;y=self.top
        self.bar(d,x,y,36,LIME,5)
        label='MISSA  /  PROJET DE MAQUETTE' if t>=11 else 'UN NOUVEAU REGARD  /  PROJET DE MAQUETTE'
        self.t(d,(x+52,y-11),label,19 if self.wide else (16 if self.square else 20),MUTED,'body')
        yy=y+51 if self.wide else y+51
        self.t(d,(x,yy),section,20 if self.wide else (18 if self.square else 22),LIME,'bold')
        if subsection:
            self.t(d,(self.w-self.m,yy),subsection,18 if self.wide else 16,MUTED,'body',anchor='ra')

    def footer(self,d,t):
        # Persistent honest disclosure in the mock-up rather than pretending
        # that catalog size, licence, pricing, colour, or logo are approved.
        x=self.m;y=self.tag_y
        d.line((x,y-15,self.w-self.m,y-15),fill=(93,125,125,120),width=1)
        txt='MAQUETTE · TARIFS, CATALOGUE, DROITS & IDENTITÉ À CONFIRMER'
        self.t(d,(x,y),txt,16 if self.wide else (15 if self.square else 18),MUTED,'body')
        self.t(d,(self.w-self.m,y),'%02d / 59'%int(t),16 if self.wide else 15,LIME,'bold',anchor='ra')

    def pic(self,im,d,name,rect,p,outline=CYAN):
        x,y,w,h=[round(v) for v in rect]
        d.rounded_rectangle((x-3,y-3,x+w+3,y+h+3),radius=30,fill=(5,10,14),outline=outline,width=3)
        src=photo(name,w,h)
        s=round(18*(.5-ease(p)))
        tile=src.crop((18+s,18-s,18+s+w,18-s+h))
        im.paste(tile,(x,y),mask(w,h,27))
        d.rounded_rectangle((x,y,x+w,y+h),radius=27,outline=(156,196,188),width=2)

    def still(self,im,d,name,rect,p,caption='CAPTURE FOURNIE · INTERFACE RÉELLE'):
        x,y,w,h=[round(v) for v in rect]
        shift=round((1-ease(p/.24))*31)
        y+=shift
        d.rounded_rectangle((x-3,y-3,x+w+3,y+h+3),radius=31,fill=(3,7,12),outline=(49,104,102),width=3)
        margin=17
        src=screenshot(name,w-2*margin,h-2*margin)
        im.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2))
        d.rounded_rectangle((x,y,x+w,y+h),radius=28,outline=CYAN,width=2)
        label=caption
        ly=y+h-43
        d.rounded_rectangle((x+14,ly-4,min(x+w-14,x+30+int(f('body',20).getlength(label))),ly+31),
            radius=9,fill=(5,12,16,237))
        self.t(d,(x+22,ly),label,20 if self.wide else (16 if self.square else 20),CYAN,'body')

    def chapter(self,d,index,lines,p,detail='',smaller=False):
        # Independent typography settings for each deliverable, not a 16:9 crop.
        x=self.m
        y=(267 if self.wide else (191 if self.square else 255))
        px=(79 if self.wide else (65 if self.square else 91))-(7 if smaller else 0)
        dy=round((1-ease(p/.28))*35)
        self.t(d,(x,y-48+dy),index,21 if self.wide else 20,LIME,'bold')
        for n,(line,colour) in enumerate(lines):
            self.t(d,(x,y+n*(px+3)+dy),line,px,colour,'display')
        if detail:
            self.t(d,(x,y+len(lines)*(px+3)+25+dy),detail,26 if self.wide else (22 if self.square else 25),MUTED,'body')

    def caption(self,im,d,t):
        if not self.subtitles:return
        cue=next((text for a,b,text in CAPTIONS['59'] if a<=t<b),None)
        if not cue:return
        lines=cue.split('\n')
        px=39 if self.wide else (32 if self.square else 43)
        lh=px+12
        max_width=self.w-2*self.m-36
        for line in lines:
            while f('body',px).getlength(line)>max_width and px>26:
                px-=1;lh=px+12
        blockheight=lh*len(lines)+34
        top=self.sub_top if not self.vertical else self.sub_top-(len(lines)-1)*9
        d.rounded_rectangle((self.m,top,self.w-self.m,top+blockheight),radius=18,
                            fill=(3,11,15,238),outline=(58,92,94,180),width=2)
        for i,line in enumerate(lines):
            self.t(d,(self.w//2,top+14+i*lh),line,px,WHITE,'body',anchor='ma')

    def _hook(self,im,d,t,p):
        self.header(d,t,'01 / TON DIVERTISSEMENT', 'TU CHERCHES ?')
        if self.wide:
            self.pic(im,d,'01-attente-salon.jpg',(82,186,980,625),p)
            # In the wide composition the photo and typography occupy distinct
            # columns; there is no duplicate headline over the person's face.
            d.rectangle((1088,215,1818,750),fill=(5,12,17,246))
            self.t(d,(1130,263),'LE DÉCLIC',22,LIME,'bold')
            self.t(d,(1125,323),'ENCORE',86,WHITE,'display')
            self.t(d,(1125,424),'À CHERCHER ?',67,LIME,'display')
            self.t(d,(1130,534),'Une envie de nouveauté.',28,MUTED,'body')
            self.bar(d,1130,607,476,LIME,5)
        elif self.square:
            self.chapter(d,'LE DÉCLIC',[('ENCORE À',WHITE),('CHERCHER ?',LIME)],p)
            self.pic(im,d,'01-attente-salon.jpg',(78,425,924,375),p)
        else:
            self.chapter(d,'LE DÉCLIC',[('ENCORE',WHITE),('À CHERCHER ?',LIME)],p,smaller=True)
            self.pic(im,d,'01-attente-salon.jpg',(76,720,928,757),p)
        # Abstract channel-scan graphic: NOT a mocked product interface.
        if self.wide:x,y=1290,702
        elif self.square:x,y=109,787
        else:x,y=106,1418
        for i in range(6):
            ht=3+(i%3)*2
            if p>i*.08:d.rounded_rectangle((x+i*36,y-ht,x+i*36+24,y+ht),radius=3,fill=CYAN if i==4 else LIME)

    def _problem(self,im,d,t,p):
        self.header(d,t,'02 / LE CONSTAT','5—11 S')
        if self.wide:
            self.pic(im,d,'01-attente-salon.jpg',(90,205,903,594),p,(69,106,103))
            x=1071;y=283;px=83
        elif self.square:
            x=82;y=184;px=70
            self.pic(im,d,'01-attente-salon.jpg',(78,440,924,344),p,(69,106,103))
        else:
            x=80;y=264;px=98
            self.pic(im,d,'01-attente-salon.jpg',(80,855,920,590),p,(69,106,103))
        self.t(d,(x,y),'CHOIX',px,WHITE,'display')
        self.t(d,(x,y+px+14),'LIMITÉ.',px,LIME,'display')
        self.t(d,(x,y+px*2+69),'ET LE PLAISIR S’ÉTEINT.',25 if self.wide else 24,MUTED,'body')
        # Zapping lines intentionally contain no fabricated channel logos.
        vy=(589 if self.wide else (779 if self.square else 660))
        vx=x if self.wide else self.m
        for i in range(3):
            if p<(i*.14):continue
            ty=vy+i*(72 if self.wide else (45 if self.square else 52))
            width=(481 if self.wide else self.w-2*self.m)
            d.rounded_rectangle((vx,ty,vx+width,ty+35),radius=8,fill=(60,75,77,180))
            d.rounded_rectangle((vx+16,ty+14,vx+round(width*(.56+.1*i)),ty+20),radius=3,fill=(110,126,124))
            d.line((vx+width-35,ty+10,vx+width-17,ty+27),fill=(176,190,187),width=2)
        if t>10.65:d.rectangle((0,0,self.w,self.h),fill=(2,5,8,round(240*ease((t-10.65)/.34))))

    def _reveal(self,im,d,t,p):
        self.header(d,t,'03 / LA RÉVÉLATION','11—17 S')
        if self.wide:
            x,y,px=116,285,99
            box=(890,257,915,560)
        elif self.square:
            x,y,px=75,168,71
            box=(75,462,930,375)
        else:
            x,y,px=81,255,96
            box=(76,737,928,710)
        self.t(d,(x,y),'MISSA',px,WHITE,'display')
        self.t(d,(x,y+px+2),'TV 360',px,LIME,'display')
        self.bar(d,x,y+px*2+31,208,CYAN,7)
        self.t(d,(x,y+px*2+72),'TON UNIVERS S’OUVRE.',
               27 if self.wide else (24 if self.square else 27),WHITE,'bold')
        self.still(im,d,'app-films.png',box,p,'CAPTURE CLIENT · FILMS / SÉRIES')
        # Thin orbital lines are abstract illustration, not a new UI.
        ox,oy=(1833,200) if self.wide else (985,368 if self.square else 636)
        d.ellipse((ox-26,oy-26,ox+26,oy+26),outline=LIME,width=4)
        d.arc((ox-67,oy-67,ox+67,oy+67),-70,155,fill=CYAN,width=3)

    def _content(self,im,d,t):
        # Each shot has its own original screenshot crop/actual navigation strip.
        shots=[(17,19.15,'FILMS',('DES','HISTOIRES.'),'app-films.png','CAPTURE CLIENT · FILMS'),
            (19.15,21.28,'SÉRIES',('À SUIVRE','SANS FIN.'),'app-films.png','CAPTURE CLIENT · SÉRIES'),
            (21.28,23.25,'DOCUMENTAIRES',('POUR','DÉCOUVRIR.'),'ui-nav-docs.png','ONGLET DOCUMENTAIRES · PAS DE GRILLE FOURNIE'),
            (23.25,25.02,'MANGAS',('POUR','VIBRER.'),'app-mangas.png','CAPTURE CLIENT · MANGAS'),
            (25.02,29,'TV DIRECT',('ET LA TÉLÉ','EN DIRECT.'),'ui-nav-tv.png','ONGLET TV DIRECT · PAS DE GRILLE FOURNIE')]
        a,b,section,lines,src,label=next(z for z in shots if z[0]<=t<z[1])
        p=(t-a)/(b-a)
        self.header(d,t,'04 / LE CATALOGUE',section)
        if self.wide:
            x,y,px=110,315,66
            box=(726,284,1080,530)
        elif self.square:
            x,y,px=76,183,64
            box=(75,453,930,369)
        else:
            x,y,px=80,273,86
            box=(77,785,924,662)
        self.t(d,(x,y-65),'0'+str(1+shots.index((a,b,section,lines,src,label)))+'   /   '+section,
               22 if self.wide else 20,LIME,'bold')
        for i,line in enumerate(lines):
            self.t(d,(x,y+i*(px+12)),line,px,WHITE if i==0 else LIME,'display')
        if src.startswith('ui-nav-'):
            self.still(im,d,src,box,p,label)
            # The captured navigation tab is deliberately the ONLY screenshot
            # shown: no invented documentary catalogue or live TV grid.
            xx=box[0]+35; yy=box[1]+box[3]//2
            self.t(d,(xx,yy+65),'ONGLET VISIBLE DANS LA CAPTURE',
                   23 if self.wide else (16 if self.square else 19),CYAN,'bold')
        else:self.still(im,d,src,box,p,label)
        if self.wide:
            d.line((x,727,x+480,727),fill=CYAN,width=4)
            self.t(d,(x,750),'CAPTURES FOURNIES / CATALOGUE À VÉRIFIER',21,MUTED,'body')

    def _audio(self,im,d,t):
        a=29.0 if t<33.05 else 33.05
        b=33.05 if t<33.05 else 37.0
        p=(t-a)/(b-a)
        self.header(d,t,'05 / L’UNIVERS AUDIO', 'PODCASTS  /  RADIO')
        if self.wide:
            self.pic(im,d,'02-moment-libre.jpg',(94,202,617,596),p)
            self.still(im,d,'app-music.png',(751,382,1053,433),p,'CAPTURE CLIENT · ONGLETS AUDIO')
            x,y,px=756,214,65
        elif self.square:
            self.pic(im,d,'02-moment-libre.jpg',(74,375,315,450),p)
            self.still(im,d,'app-music.png',(411,407,594,407),p,'CAPTURE CLIENT · AUDIO')
            x,y,px=74,174,62
        else:
            self.pic(im,d,'02-moment-libre.jpg',(77,756,922,600),p)
            self.still(im,d,'app-music.png',(78,1155,922,327),p,'CAPTURE CLIENT · AUDIO')
            x,y,px=79,280,91
        head='PODCASTS' if t<33.05 else 'RADIOS'
        self.t(d,(x,y),head,px,LIME,'display')
        self.t(d,(x,y+px+8),'À ÉCOUTER.',px if self.wide else px-8,WHITE,'display')
        if self.wide:
            ybars=318;xbars=1215
        elif self.square:
            ybars=350;xbars=591
        else:
            ybars=640;xbars=220
        for i in range(20):
            height=round((13+15*abs(math.sin(i*1.65+t*7))) * (1.35 if self.vertical else 1))
            d.rounded_rectangle((xbars+i*22,ybars-height,xbars+i*22+9,ybars+height),radius=4,
                                fill=CYAN if i%3 else LIME)

    def _prices(self,im,d,t):
        monthly=t<42
        p=(t-(37 if monthly else 42))/5
        self.header(d,t,'06 / LES FORMULES','TARIFS À CONFIRMER')
        if self.wide:
            x,y,w,h=210,299,1500,523
            titlepx=76;valuepx=100
        elif self.square:
            x,y,w,h=77,327,926,494
            titlepx=57;valuepx=61
        else:
            x,y,w,h=74,576,932,849
            titlepx=75;valuepx=65
        d.rounded_rectangle((x,y,x+w,y+h),radius=37,fill=(5,13,18),outline=LIME,width=4)
        self.bar(d,x+43,y+45,122,CYAN,8)
        self.t(d,(x+43,y+75),'LE DIVERTISSEMENT',titlepx if self.wide else titlepx-10,WHITE,'display')
        self.t(d,(x+43,y+80+titlepx),'À TON RYTHME.',titlepx if self.wide else titlepx-10,LIME,'display')
        if monthly:
            amount='2 000 FCFA / mois'
            description='FORMULE MENSUELLE'
        else:
            amount='10 000 FCFA / an'
            description='FORMULE ANNUELLE'
        baseline=y+(321 if self.wide else (322 if self.square else 482))
        self.t(d,(x+43,baseline-44),description,22 if self.wide else 23,CYAN,'bold')
        if f('display',valuepx).getlength(amount)>w-83:
            valuepx=int(valuepx*(w-83)/f('display',valuepx).getlength(amount))
        # Keep the precise requested FCFA string on a SINGLE line in every ratio.
        self.t(d,(x+43,baseline),amount,valuepx,LIME,'display')
        d.line((x+43,y+h-80,x+w-43,y+h-80),fill=(99,120,115),width=2)
        self.t(d,(x+43,y+h-62),'TARIF & CONDITIONS : VALIDATION COMMERCIALE REQUISE',
               20 if self.wide else (15 if self.square else 17),MUTED,'body')
        if self.wide:
            self.t(d,(self.m,205),'DU CHOIX.  À TON PRIX.',28,WHITE,'bold')
        elif self.square:self.t(d,(self.m,212),'UN FORMAT POUR TOI.',25,WHITE,'bold')
        else:
            self.t(d,(self.m,342),'PLUS DE CHOIX.',65,WHITE,'display')
            self.t(d,(self.m,417),'PLUS DE PLAISIR.',52,LIME,'display')
        if p<.14:
            # Tiny yellow entry wipe; all prices remain readable after 0.14 s.
            sweep=round(124*(1-ease(p/.14)))
            d.rounded_rectangle((x+w-16,y+52,x+w-11,y+h-110+sweep),radius=3,fill=LIME)

    def _choice(self,im,d,t,p):
        self.header(d,t,'07 / LA PROMESSE','DIVERSITÉ  /  ÉMOTION')
        if self.wide:
            self.pic(im,d,'02-moment-libre.jpg',(88,189,1000,630),p)
            x,y,px=1139,278,74
        elif self.square:
            self.pic(im,d,'02-moment-libre.jpg',(75,431,930,389),p)
            x,y,px=75,164,65
        else:
            self.pic(im,d,'02-moment-libre.jpg',(77,740,925,713),p)
            x,y,px=80,269,91
        for i,(line,col) in enumerate((('FAIS LE',WHITE),('CHOIX DE LA',WHITE),('DIVERSITÉ.',LIME))):
            self.t(d,(x,y+i*(px+6)),line,px,col,'display')
        text='TON DIVERTISSEMENT MÉRITE MIEUX.'
        if self.wide:
            d.rounded_rectangle((1105,629,1818,767),radius=17,fill=(4,14,18,228),outline=CYAN,width=3)
            self.t(d,(1133,658),'TON DIVERTISSEMENT',30,WHITE,'bold')
            self.t(d,(1133,703),'MÉRITE MIEUX.',33,LIME,'bold')
        elif self.square:self.t(d,(self.m,814),text,26,WHITE,'bold')
        else:self.t(d,(self.m,1470),text,32,LIME,'bold')

    def _end(self,im,d,t,p):
        self.header(d,t,'08 / À TOI DE JOUER','54—59 S')
        w,h=self.w,self.h
        # Three orbit circles: abstract motif, not an official brand asset.
        cx,cy=(w*.52,h*.46) if self.wide else ((w*.50,h*.44) if self.square else (w*.5,h*.49))
        for i in range(3):
            r=int((190+i*95)*(1+.10*math.sin(2*math.pi*(t-54)/3)))
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(45,105+i*22,97+i*19),width=2)
        brandpx=136 if self.wide else (80 if self.square else 112)
        self.t(d,(w//2,cy-149 if self.wide else cy-197),'MISSA',brandpx,WHITE,'display',anchor='ma')
        self.t(d,(w//2,cy+6 if self.wide else cy-76),'TV 360',brandpx,LIME,'display',anchor='ma')
        btnw=(760 if self.wide else (835 if self.square else 890))
        bt=int(cy+(183 if self.wide else (129 if self.square else 188)))
        x=int((w-btnw)/2)
        d.rounded_rectangle((x,bt,x+btnw,bt+94 if self.wide else bt+100),radius=22,fill=LIME)
        self.t(d,(w//2,bt+22),'TÉLÉCHARGE DÈS MAINTENANT',
               35 if self.wide else (32 if self.square else 36),INK,'bold',anchor='ma')
        self.t(d,(w//2,bt+(104 if self.wide else 126)),
               'LOGO OFFICIEL & LIEN DE TÉLÉCHARGEMENT À FOURNIR',
               19 if self.wide else (18 if self.square else 21),MUTED,'body',anchor='ma')
        if self.vertical:
            self.t(d,(w//2,1450),'TON DIVERTISSEMENT MÉRITE MIEUX.',27,WHITE,'bold',anchor='ma')
            self.t(d,(w//2,1500),'PASSE À MISSA TV 360 !',32,LIME,'bold',anchor='ma')
        elif self.square:
            self.t(d,(w//2,788),'PASSE À MISSA TV 360 !',27,WHITE,'bold',anchor='ma')
        else:
            self.t(d,(w//2,819),'PASSE À MISSA TV 360 !',30,WHITE,'bold',anchor='ma')

    def render(self,t):
        t=clamp(t,0,DURATION-1/FPS)
        a,b,kind=next((sc for sc in SCENES['59'] if sc[0]<=t<sc[1]),SCENES['59'][-1])
        p=(t-a)/(b-a)
        theme={'hook':'search','problem':'search','reveal':'reveal','content':'content',
               'audio':'sound','prices':'price','choice':'choice','cta':'end'}[kind]
        im=self.base[theme].copy()
        d=ImageDraw.Draw(im,'RGBA')
        if kind=='hook':self._hook(im,d,t,p)
        elif kind=='problem':self._problem(im,d,t,p)
        elif kind=='reveal':self._reveal(im,d,t,p)
        elif kind=='content':self._content(im,d,t)
        elif kind=='audio':self._audio(im,d,t)
        elif kind=='prices':self._prices(im,d,t)
        elif kind=='choice':self._choice(im,d,t,p)
        else:self._end(im,d,t,p)
        self.caption(im,d,t)
        self.footer(d,t)
        return im


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ratio',choices=SIZES,default='landscape')
    parser.add_argument('--at',help='Comma-separated frame timestamps; PNG previews in .cache/diversite-video/')
    parser.add_argument('--output',type=Path,help='Silent H.264 render path')
    parser.add_argument('--crf',type=int,default=23)
    parser.add_argument('--without-captions',action='store_true',help='For the no-voice localisation edit')
    args=parser.parse_args()
    film=Film(args.ratio,not args.without_captions)
    if args.at:
        for at in (float(x) for x in args.at.split(',')):
            file=CACHE/f'preview-{args.ratio}-{at:.2f}.jpg'
            film.render(at).save(file,quality=85)
            print(file,flush=True)
        return
    target=args.output if args.output else CACHE/f'silent-{args.ratio}.mp4'
    target.parent.mkdir(parents=True,exist_ok=True)
    w,h=SIZES[args.ratio];count=int(DURATION*FPS)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo',
         '-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(FPS),'-i','pipe:0','-an',
         '-c:v','libx264','-preset','veryfast','-crf',str(args.crf),
         '-maxrate','18M','-bufsize','36M','-pix_fmt','yuv420p',
         '-r',str(FPS),'-g',str(FPS*2),'-movflags','+faststart',str(target)]
    print(f'Render {args.ratio} {w}×{h} / {count} images @ {FPS} fps → {target}',flush=True)
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(count):
            frame=film.render(n/FPS)
            assert proc.stdin
            proc.stdin.write(frame.tobytes())
            if n%125==0:print(f'  {n}/{count}',flush=True)
        assert proc.stdin
        proc.stdin.close()
        code=proc.wait()
        if code:raise RuntimeError(f'ffmpeg exited {code}')
    except BaseException:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
        proc.kill();proc.wait()
        raise
    print(f'OK {target} {target.stat().st_size/1048576:.1f} MiB',flush=True)

if __name__=='__main__':main()
