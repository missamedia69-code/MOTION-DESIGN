"""Frame-accurate, reproducible MISSA TV 360 photo + actual-app motion composition.

Generative photography is ONLY the fictional family and unbranded city scenes.
All captions, UI, numbers, brand labels and placeholders are drawn here.
Each ratio is composed independently; no landscape/square centre-crop shortcut.

Examples:
  python3 projects/missa-tv-360-ton-ecran/render.py --ratio portrait --at 0.5,14.5,20,25,42.5,48.5,56
  python3 projects/missa-tv-360-ton-ecran/render.py --ratio portrait --version 59 --output .cache/ton-ecran-video/59-portrait.mp4
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from timeline import SCENES, CAPTIONS

ROOT=Path(__file__).resolve().parents[2]
PROJECT=Path(__file__).resolve().parent
A=PROJECT/'assets'
OUT=ROOT/'.cache/ton-ecran-video'
OUT.mkdir(parents=True,exist_ok=True)
YELLOW=(244,184,0)  # sampled from client screenshot; NOT the missing colors.xml value
GREEN=(0,158,73)
CREAM=(250,247,236)
DARK=(6,10,17)
MUTED=(180,192,194)
RED=(229,57,53)
BASE=Image.Resampling.BILINEAR
SIZES={'portrait':(1080,1920),'square':(1080,1080),'landscape':(1920,1080)}
FONTS={
    'black':PROJECT/'fonts/Montserrat-Black.ttf',
    'bold':PROJECT/'fonts/Montserrat-ExtraBold.ttf',
    'text':PROJECT/'fonts/Nunito-Variable.ttf',
}


@lru_cache(maxsize=160)
def font(kind:str,size:int):
    return ImageFont.truetype(str(FONTS[kind]),size)


@lru_cache(maxsize=50)
def file_image(path:str):
    return Image.open(A/path).convert('RGB')


@lru_cache(maxsize=80)
def scaled_image(path:str,w:int,h:int):
    return file_image(path).resize((w,h),Image.Resampling.LANCZOS)


def clamp(v,lo=0,hi=1):return max(lo,min(hi,v))
def ease(v):
    v=clamp(v)
    return v*v*(3-2*v)


class Film:
    def __init__(self,ratio:str,version:str):
        self.ratio=ratio; self.version=version
        self.w,self.h=SIZES[ratio]
        self.scenes=SCENES[version]; self.cues=CAPTIONS[version]
        self.portrait=ratio=='portrait';self.wide=ratio=='landscape';self.square=ratio=='square'
        self.panelw=1000 if self.wide else self.w
        self.panelh=self.h
        self.pic_cache={}
        # Text has a translucent authored surface, not text baked into AI images.
        self.grade=self._vignette()
        if self.portrait:
            self.left=105;self.right=955;self.header=224
            self.titley=350;self.titlepx=91;self.board=(105,643,850,488)
            self.sub_y=1288;self.subsize=60;self.submax=850
        elif self.square:
            self.left=82;self.right=998;self.header=48
            self.titley=165;self.titlepx=71;self.board=(153,383,774,447)
            self.sub_y=865;self.subsize=56;self.submax=944
        else:
            self.left=907;self.right=1815;self.header=62
            self.titley=200;self.titlepx=87;self.board=(910,438,867,455)
            self.sub_y=922;self.subsize=57;self.submax=1450

    def _vignette(self):
        w,h=self.w,self.h
        yy=np.linspace(0,1,h,dtype=np.float32)[:,None]
        xx=np.linspace(0,1,w,dtype=np.float32)[None,:]
        if self.wide:
            horizontal=np.clip((xx-.34)/.39,0,1)*.60
            alpha=.27+.35*(yy>.78)*(yy-.78)/.22 + horizontal
        elif self.square:
            alpha=.37 + .26*(1-abs(yy-.47)*1.3) + .30*(yy>.73)*(yy-.73)/.27
        else:
            alpha=.28 + .16*(1-abs(yy-.48)) + .33*(yy>.73)*(yy-.73)/.27
            alpha=alpha+.06*np.minimum(1,xx*xx*6)
        alpha=np.broadcast_to(np.clip(alpha,0,.97),(h,w))
        arr=np.zeros((h,w,4),dtype=np.uint8)
        arr[:,:,:3]=[5,9,17]
        arr[:,:,3]=(alpha*255).astype(np.uint8)
        return Image.fromarray(arr,'RGBA')

    def _picture(self,path:str,focus=(.5,.56)):
        key=(path,self.panelw,self.panelh)
        if key not in self.pic_cache:
            src=file_image(path)
            # Oversize once. Each frame crops/resizes a different window (true Ken Burns).
            scale=max(self.panelw*1.28/src.width,self.panelh*1.28/src.height)
            self.pic_cache[key]=src.resize((round(src.width*scale),round(src.height*scale)),BASE)
        return self.pic_cache[key]

    def background(self,photo:str,p:float,focus=(.5,.57)):
        img=self._picture('photos/'+photo+'.jpg',focus)
        zoom=1.04+.12*ease(p)
        cw=int(self.panelw/zoom);ch=int(self.panelh/zoom)
        # Shift crop gently across scene, never a static still.
        drift=.055*(ease(p)-.5)
        x=round((img.width-cw)*clamp(focus[0]+drift,.03,.97))
        y=round((img.height-ch)*clamp(focus[1]-.025*ease(p),.03,.97))
        x=min(img.width-cw,max(0,x));y=min(img.height-ch,max(0,y))
        frame=Image.new('RGBA',(self.w,self.h),DARK+(255,))
        if self.wide:
            frame.paste(img.crop((x,y,x+cw,y+ch)).resize((self.panelw,self.panelh),BASE),(0,0))
        else:
            frame.paste(img.crop((x,y,x+cw,y+ch)).resize((self.w,self.h),BASE),(0,0))
        return Image.alpha_composite(frame,self.grade)

    def txt(self,draw,xy,text,px=50,color=CREAM,kind='bold',anchor=None,stroke=0,fill=None):
        # The bundled display font has no U+202F glyph: PIL would draw a TOFU
        # square in prices. Paint narrow no-break spaces as real visual gaps;
        # the semantic string / the source still contain U+202F.
        if '\u202f' in text:
            x,y=xy
            for piece in text.split('\u202f'):
                draw.text((round(x),y),piece,font=font(kind,px),fill=color,anchor=anchor,
                          stroke_width=stroke,stroke_fill=fill if fill else DARK)
                x+=font(kind,px).getlength(piece)+max(6,px*.15)
            return
        draw.text(xy,text,font=font(kind,px),fill=color,anchor=anchor,
                  stroke_width=stroke,stroke_fill=fill if fill else DARK)

    def round(self,draw,xy,fill,outline=None,width=2,r=25):
        draw.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=width)

    def headerbar(self,im,draw,t,label):
        # The logo is a *reveal*, not visible in the frustration setup. After
        # the musical drop we show faithful screenshot pixels, never an AI logo.
        small=file_image('app/identite-capture-temporaire.png')
        left=self.left;top=self.header
        sf=1.25 if self.wide else (1.20 if self.portrait else 1.05)
        w=round(small.width*sf);h=round(small.height*sf)
        self.round(draw,(left-10,top-9,left+w+11,top+h+10),(0,0,0,215),outline=(58,71,71),r=13)
        reveal={'59':14.00,'30':3.31,'15':2.80}[self.version]
        if t<reveal:
            self.txt(draw,(left+11,top+11),'CE SOIR',px=32 if self.portrait else 29,
                     color=CREAM,kind='bold')
        else:
            im.paste(small.resize((w,h),Image.Resampling.LANCZOS),(left,top))
        ly=top+h+18
        self.txt(draw,(left,ly),label,px=25 if self.portrait else (22 if self.square else 26),color=YELLOW,kind='text')
        # Sober countdown / section marker, stays out of the 9:16 platform chrome.
        if self.portrait:
            draw.line((self.right-6,top+17,self.right-6,top+55),fill=YELLOW,width=7)
        elif self.wide:
            draw.line((self.right,top,self.right,top+49),fill=YELLOW,width=6)
        else:
            draw.line((self.right-6,top,self.right-6,top+40),fill=YELLOW,width=6)

    def heading(self,draw,lines:list[tuple[str,tuple]],p:float=1,sub=False):
        size=self.titlepx-(8 if sub else 0)
        x=self.left; y=self.titley
        enter=ease(clamp(p/.23))
        y+=round((1-enter)*55)
        for i,(text,color) in enumerate(lines):
            tsize=size if len(text)<18 else int(size*.80)
            # Bold headlines have a real shadow/contrast against live-action images.
            self.txt(draw,(x+3,y+5),text,px=tsize,color=(0,0,0,235),kind='black')
            self.txt(draw,(x,y),text,px=tsize,color=color,kind='black')
            y+=round(tsize*1.12)

    def label(self,draw,text,y,highlight=False,px=None):
        if px is None: px=37 if self.portrait else (30 if self.square else 38)
        fg=YELLOW if highlight else CREAM
        self.txt(draw,(self.left+4,y),text,px=px,color=fg,kind='bold')

    def ui_card(self,im,draw,name:str,p:float,tag:str='',highlight:str|None=None,zoom=False):
        x,y,w,h=self.board
        if zoom and p<.52:
            name='app-films.png'
        elif zoom:
            name='app-mangas.png'
        # From a real customer screenshot, no screen reconstruction.
        src=file_image('app/'+name)
        box=Image.new('RGB',(w-22,h-22),(4,5,8))
        ratio=min((w-22)/src.width,(h-22)/src.height)
        rw,rh=round(src.width*ratio),round(src.height*ratio)
        resized=scaled_image('app/'+name,rw,rh)
        box.paste(resized,((box.width-rw)//2,(box.height-rh)//2))
        if self.portrait and not zoom and p>.12:
            # Small vertical UI push-in; sharp enough to recognise original tabs.
            b=round((p-.12)*min(16,(p-.12)*16))
            if b>0:
                box=box.crop((b,b,box.width-b,box.height-b)).resize(box.size,BASE)
        self.round(draw,(x-8,y-8,x+w+8,y+h+8),(3,7,9,240),outline=YELLOW,width=3,r=30)
        # Solid screenshot rectangle (Pillow overlays are not generated images).
        im.paste(box,(x+11,y+11))
        if tag:
            bar_y=y+h+19 if self.portrait else y+h-65
            self.round(draw,(x,bar_y,x+min(w,650),bar_y+54),(0,0,0,232),r=16)
            self.txt(draw,(x+19,bar_y+8),tag,px=27 if self.portrait else (24 if self.square else 28),color=YELLOW,kind='bold')
        if highlight:
            self.ui_nav_crop(im,draw,highlight, y+(h//3) if self.portrait else y+round(h*.43))

    def ui_nav_crop(self,im,draw,which,y):
        nav=file_image('app/ui-nav-'+which+'.png')
        x,bw,by=self.left,self.right-self.left,y
        aspect=nav.width/nav.height
        dw=min(bw-40,745 if self.portrait else (670 if self.square else 765))
        dh=round(dw/aspect)
        if dh>166:
            dh=166;dw=round(dh*aspect)
        px=x+max(0,(bw-dw)//2)
        self.round(draw,(px-13,by-10,px+dw+13,by+dh+10),(0,0,0,246),outline=YELLOW,width=5,r=23)
        im.paste(nav.resize((dw,dh),Image.Resampling.LANCZOS),(px,by))

    def black_label(self,draw,text,top,color=YELLOW,size=None):
        if size is None: size=35 if self.portrait else (25 if self.square else 34)
        tw=font('bold',size).getlength(text)
        x=self.left;w=min(self.right-self.left,max(240,int(tw)+46))
        self.round(draw,(x,top,x+w,top+size+31),(0,0,0,223),outline=(64,70,69),r=17)
        self.txt(draw,(x+22,top+13),text,px=size,color=color,kind='bold')

    def price_card(self,im,draw,annual=False,p=1):
        x=self.left
        if self.wide:
            y=405;w=880;h=420
        elif self.square:
            y=390;w=910;h=350
        else:
            y=648;w=846;h=456
        # Price comes in as one immutable graphic, never an animated number counter.
        pop=.93+.07*ease(p/.38)
        aw=round(w*pop); ah=round(h*pop)
        x+=round((w-aw)/2);y+=round((h-ah)/2)
        self.round(draw,(x,y,x+aw,y+ah),(8,16,21,248),outline=YELLOW,width=5,r=35)
        y0=y+(35 if self.portrait else 29)
        self.txt(draw,(x+45,y0),'L’ANNÉE' if annual else 'LE MOIS',px=32 if self.portrait else 30,color=CREAM,kind='bold')
        # Mandatory on-screen money syntax: prefix XAF, thin grouping space, trailing / an|mois.
        value='XAF 10\u202f000' if annual else 'XAF 2\u202f000'
        size=110 if self.portrait else (94 if self.square else 108)
        while font('black',size).getlength(value)>aw-86: size-=2
        self.txt(draw,(x+42,y0+75),value,px=size,color=YELLOW,kind='black')
        self.txt(draw,(x+48,y0+(218 if self.portrait else 190)),
                 '/ an' if annual else '/ mois',px=59 if self.portrait else (48 if self.square else 57),color=CREAM,kind='bold')
        if annual:
            stamp_y=y+ah-69
            self.round(draw,(x+35,stamp_y,x+aw-35,stamp_y+53),(0,96,55,235),r=14)
            text='7 MOIS OFFERTS  •  < 30 F / JOUR'
            size=35 if self.portrait else (28 if self.square else 33)
            while font('black',size).getlength(text)>aw-85: size-=1
            self.txt(draw,(x+50,stamp_y+7),text,px=size,color=CREAM,kind='black')
            # Seven stamps are overlays, not cycling price numerals.
            if p>.22 and self.portrait:
                count=min(7,int((p-.22)*3.4)+1)
                for i in range(count):
                    xx=x+70+i*(aw-140)/7
                    draw.line((xx,stamp_y-15,xx+35,stamp_y-15),fill=GREEN,width=5)

    def devices(self,im,draw,p):
        x,y,w,h=self.board
        # Real client pixels are placed into vector display frames; no AI-generated UI.
        src=file_image('app/app-films.png')
        if self.wide:
            fx,fy,fw,fh=x+35,y+10,745,400
        elif self.square:
            fx,fy,fw,fh=x+27,y+10,710,365
        else:
            fx,fy,fw,fh=x+40,y+15,765,409
        self.round(draw,(fx-15,fy-15,fx+fw+15,fy+fh+24),(9,11,15,239),outline=YELLOW,width=4,r=23)
        img=scaled_image('app/app-films.png',fw,fh)
        im.paste(img,(fx,fy))
        draw.rounded_rectangle((fx+fw//2-74,fy+fh+26,fx+fw//2+74,fy+fh+38),fill=(51,60,66),radius=6)
        tag_y=y+h+42
        if self.wide: tag_y=848
        if self.square: tag_y=802
        self.black_label(draw,'TÉLÉ ANDROID  ·  TABLETTE  ·  TÉLÉPHONE',tag_y,size=30 if self.portrait else (22 if self.square else 30))
        if self.portrait and p>.40:
            self.black_label(draw,'INTERNET REQUIS · PETIT DÉBIT',578,size=29)

    def cta(self,im,draw,p):
        self.heading(draw,[('TON ÉCRAN',CREAM),('MÉRITE MIEUX.',YELLOW)],p)
        if self.wide: y=450;w=865
        elif self.square:y=368;w=913
        else:y=658;w=850
        x=self.left
        # Both prices are completely fixed and use the mandatory XAF prefix.
        self.round(draw,(x,y,x+w,y+126 if self.portrait else y+104),(6,14,16,245),outline=YELLOW,width=3,r=22)
        s1='XAF 2\u202f000 / mois';s2='XAF 10\u202f000 / an'
        sz=42 if self.portrait else (35 if self.square else 40)
        self.txt(draw,(x+22,y+13),s1,px=sz,color=CREAM,kind='black')
        self.txt(draw,(x+22,y+65 if self.portrait else y+59),s2,px=sz,color=YELLOW,kind='black')
        by=y+(160 if self.portrait else (128 if self.square else 139))
        self.round(draw,(x,by,x+w,by+85),(244,184,0),r=18)
        self.txt(draw,(x+23,by+12),'TÉLÉCHARGER L’APPLI  ↗',px=40 if self.portrait else (36 if self.square else 40),color=DARK,kind='black')
        # Not an ersatz QR pattern: a conspicuously EMPTY, labelled box.
        qy=by+(109 if self.portrait else 94); qsize=125 if self.portrait else (96 if self.square else 92)
        self.round(draw,(x,qy,x+qsize,qy+qsize),(0,0,0,235),outline=YELLOW,width=3,r=14)
        self.txt(draw,(x+11,qy+28),'QR',px=48 if self.portrait else 35,color=YELLOW,kind='bold')
        self.txt(draw,(x+qsize+25,qy+13),'QR À VENIR · LIEN À FOURNIR',px=29 if self.portrait else (25 if self.square else 29),color=CREAM,kind='bold')
        self.txt(draw,(x+qsize+25,qy+55),'LOGO OFFICIEL À FOURNIR',px=26 if self.portrait else (23 if self.square else 27),color=YELLOW,kind='text')
        last=qy+qsize+13
        if self.portrait:txt='OFFRE · PAIEMENT · VOIX · JAUNE : À VALIDER'
        else:txt='OFFRE / PAIEMENT / VOIX / JAUNE À VALIDER'
        self.round(draw,(x-6,last-7,x+w,last+41),(0,0,0,232),r=9)
        self.txt(draw,(x+5,last),txt,px=27 if self.portrait else (22 if self.square else 24),color=CREAM,kind='bold')

    def captions(self,im,draw,t):
        cue=next((text for start,end,text in self.cues if start<=t<end),'')
        if not cue:return
        lines=cue.split('\n')[:2]
        px=self.subsize
        # Enforce mandatory ≥56px for portrait; display unchanged transcript.
        while px>56 and any(font('text',px).getlength(line)>self.submax-24 for line in lines):px-=1
        lineheight=round(px*1.23)
        height=lineheight*len(lines)+32
        if self.wide:
            y=min(self.h-height-25,self.sub_y)
            left=max(180,(self.w-self.submax)//2)
            right=min(self.w-180,(self.w+self.submax)//2)
        elif self.square:
            y=min(self.h-height-20,self.sub_y)
            left=42;right=self.w-42
        else:
            y=min(1440-height,self.sub_y)
            left=80;right=980
        self.round(draw,(left,y,right,y+height),(1,5,9,222),outline=(53,63,62),r=23)
        pattern=re.compile(r'(milliers|centaines|offerts|Missa|deux mille|dix mille)',re.I)
        for i,line in enumerate(lines):
            f=font('text',px)
            width=f.getlength(line)
            x=(self.w-width)/2
            yy=y+12+i*lineheight
            for section in pattern.split(line):
                if not section: continue
                color=YELLOW if pattern.fullmatch(section) else CREAM
                self.txt(draw,(round(x),yy),section,px=px,color=color,kind='text',stroke=3,fill=(0,0,0))
                x+=f.getlength(section)

    def render(self,t:float):
        t=min(max(t,0),float(self.version)-1/30)
        scene=next(((a,b,kind) for a,b,kind in self.scenes if a<=t<b),self.scenes[-1])
        a,b,kind=scene;p=(t-a)/(b-a)
        if self.version=='59' and 13.64<=t<14.0:
            im=Image.new('RGB',(self.w,self.h),DARK)
            return im
        pic={
            'hook':'frustration-salon','repeat':'frustration-salon','zapping':'frustration-salon',
            'mom':'maman-decision','chorus':'famille-enthousiasme','reveal':'famille-enthousiasme',
            'films':'famille-reference','tv':'famille-enthousiasme',
            'audio':'aicha-musique-ville','more':'famille-reference','devices':'famille-enthousiasme',
            'month':'reaction-papa','reaction':'reaction-papa','year':'reaction-papa',
            'cta':'famille-enthousiasme'
        }[kind]
        focus={
            'hook':(.49,.60),'repeat':(.30,.60),'zapping':(.51,.56),'mom':(.50,.58),
            'audio':(.50,.49),'month':(.50,.44),'reaction':(.50,.43),
            'year':(.5,.43),'cta':(.52,.60),
        }.get(kind,(.51,.58))
        im=self.background(pic,p,focus)
        draw=ImageDraw.Draw(im,'RGBA')
        # Motion-design tick and clear creator mark. Nothing comes from generated-photo text.
        labs={
            'hook':'01 / LE DÉCLIC','repeat':'01 / LE DÉCLIC','zapping':'01 / LE DÉCLIC',
            'mom':'01 / LE DÉCLIC','chorus':'01 / LE DÉCLIC',
            'reveal':'02 / L’APPLICATION','films':'03 / FILMS & MANGAS',
            'tv':'04 / TV DIRECT','audio':'05 / AUDIO','more':'06 / POUR TOUS',
            'devices':'07 / TOUS TES ÉCRANS','month':'08 / LE PRIX',
            'reaction':'08 / LE PRIX','year':'09 / L’ANNÉE','cta':'10 / À TOI DE JOUER'
        }
        self.headerbar(im,draw,t,labs[kind])
        if kind=='hook':
            self.heading(draw,[('TU PAIES',CREAM),('ENCORE ?',YELLOW)],p)
            if self.portrait:self.black_label(draw,'ET TU REVOIS LA MÊME CHOSE',715)
            elif self.wide:self.black_label(draw,'LA MÊME CHOSE. ENCORE.',577)
            else:self.black_label(draw,'LA MÊME CHOSE. ENCORE.',490)
        elif kind=='repeat':
            self.heading(draw,[('LES MÊMES',CREAM),('CHAÎNES.',YELLOW)],p)
            self.black_label(draw,'LES MÊMES SÉRIES.',
                             713 if self.portrait else (497 if self.square else 589))
        elif kind=='zapping':
            self.heading(draw,[('ON PAIE.',CREAM),('ON ZAPPE.',YELLOW)],p)
            top=660 if self.portrait else (460 if self.square else 520)
            for i,word in enumerate(('01  UN ABONNEMENT','02  ON CHERCHE','03  ENCORE PAREIL')):
                if p>(i*.11):
                    xx=self.left; yy=top+i*(101 if self.portrait else 77)
                    self.round(draw,(xx,yy,self.right,yy+(79 if self.portrait else 65)),
                               (4,10,13,230),outline=(78,86,81),r=14)
                    self.txt(draw,(xx+24,yy+12),word,px=41 if self.portrait else 32,
                             color=YELLOW if i==2 else CREAM,kind='bold')
        elif kind=='mom':
            self.heading(draw,[('ÇA SUFFIT.',CREAM),('ON MÉRITE',YELLOW),('MIEUX.',CREAM)],p,sub=True)
        elif kind=='chorus':
            self.heading(draw,[('ON MÉRITE',CREAM),('MIEUX !',YELLOW)],p)
            draw.line((self.left,1100 if self.portrait else 710,self.right,
                       1100 if self.portrait else 710),fill=YELLOW,width=8)
        elif kind=='reveal':
            self.heading(draw,[('TON ÉCRAN',CREAM),('MÉRITE MIEUX.',YELLOW)],p)
            self.ui_card(im,draw,'app-films.png',p,'VRAIE INTERFACE DE L’APPLICATION')
            # Official logo placeholder appears on the CTA, not over this UI tag.
        elif kind=='films':
            self.heading(draw,[('MILLIERS',YELLOW),('D’HISTOIRES.',CREAM)],p)
            name='app-films.png' if p<.58 else 'app-mangas.png'
            self.ui_card(im,draw,name,p,
                'CAPTURE RÉELLE · ONGLET DOCUMENTAIRES' if p>.50 else 'CAPTURE RÉELLE · FILMS / SÉRIES',
                highlight='docs' if p>.55 else None)
        elif kind=='tv':
            self.heading(draw,[('LA TÉLÉ',CREAM),('EN DIRECT.',YELLOW)],p)
            self.ui_card(im,draw,'app-music.png',p,'ONGLET TV DIRECT · CAPTURE RÉELLE',highlight='tv')
            # LIVE is authored vector text, NOT a synthetic catalogue.
            if self.portrait: bx,by=self.right-168,544
            elif self.square:bx,by=self.right-145,325
            else:bx,by=self.right-155,309
            self.round(draw,(bx,by,bx+138,by+51),(229,57,53,240),r=11)
            self.txt(draw,(bx+22,by+8),'LIVE',px=32,color=CREAM,kind='black')
        elif kind=='audio':
            self.heading(draw,[('TON RYTHME.',CREAM),('TON CHOIX.',YELLOW)],p)
            # The fourth customer screenshot contributes its faithful player
            # crop, without bringing its unrelated clip title into this scene.
            player=p>.57
            self.ui_card(im,draw,'app-player-focus.png' if player else 'app-music.png',p,
                         'LECTEUR RÉEL · 4E CAPTURE' if player else 'MUSIQUE · PODCASTS · RADIO',
                         highlight='audio' if p>.72 else None)
        elif kind=='more':
            self.heading(draw,[('ET POUR',CREAM),('TOUT LE MONDE.',YELLOW)],p)
            yy=665 if self.portrait else (472 if self.square else 540)
            for i,line in enumerate(('JEUX RÉTRO','SPORTS · COURTS-MÉTRAGES','PROGRAMMES ENFANTS')):
                self.black_label(draw,line,yy+i*(108 if self.portrait else 77),size=33 if self.portrait else 26)
        elif kind=='devices':
            self.heading(draw,[('UNE APPLI.',CREAM),('TOUS TES ÉCRANS.',YELLOW)],p,sub=True)
            self.devices(im,draw,p)
        elif kind=='month':
            self.heading(draw,[('UN PETIT',CREAM),('FORFAIT.',YELLOW)],p)
            self.price_card(im,draw,annual=False,p=p)
        elif kind=='reaction':
            self.heading(draw,[('ET',CREAM),('L’ANNÉE ?',YELLOW)],p)
            self.black_label(draw,'PAPA DEMANDE. ON RÉPOND.',
                             748 if self.portrait else (514 if self.square else 622),size=29)
        elif kind=='year':
            self.heading(draw,[('ENCORE',CREAM),('MIEUX.',YELLOW)],p)
            self.price_card(im,draw,annual=True,p=p)
            if self.portrait:self.black_label(draw,'ÉCONOMIE : XAF 14\u202f000 / AN',1140,size=32)
            elif self.wide:self.black_label(draw,'ÉCONOMIE : XAF 14\u202f000 / AN',854,size=31)
            else:self.black_label(draw,'ÉCONOMIE : XAF 14\u202f000 / AN',768,size=26)
        elif kind=='cta':
            self.cta(im,draw,p)
        self.captions(im,draw,t)
        # Scaled music ruler / visual beat at bottom — only nonessential overflow.
        prog=t/float(self.version)
        if self.portrait:
            draw.rectangle((self.left,1490,self.right,1499),fill=(75,78,77))
            draw.rectangle((self.left,1490,self.left+round((self.right-self.left)*prog),1499),fill=YELLOW)
        elif self.square:
            draw.rectangle((self.left,1046,self.right,1054),fill=(75,78,77))
            draw.rectangle((self.left,1046,self.left+round((self.right-self.left)*prog),1054),fill=YELLOW)
        else:
            draw.rectangle((self.left,1052,self.right,1060),fill=(75,78,77))
            draw.rectangle((self.left,1052,self.left+round((self.right-self.left)*prog),1060),fill=YELLOW)
        return im.convert('RGB')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',choices=('59','30','15'),default='59')
    parser.add_argument('--ratio',choices=tuple(SIZES),default='portrait')
    parser.add_argument('--at',help='Comma-separated times; save screenshots instead of a video')
    parser.add_argument('--output',help='Silent MP4 path (mux with audio.py output separately)')
    parser.add_argument('--crf',type=int,default=24)
    args=parser.parse_args()
    if args.version!='59' and args.ratio!='portrait':parser.error('Shorts are portrait only')
    film=Film(args.ratio,args.version)
    if args.at:
        import time
        starts=time.time()
        for t in [float(x) for x in args.at.split(',')]:
            path=OUT/f'preview-{args.version}-{args.ratio}-{t:.2f}.png'
            film.render(t).save(path)
            print(path)
        print(f'Previews in {time.time()-starts:.1f}s')
        return
    target=Path(args.output) if args.output else OUT/f'{args.version}-{args.ratio}-silent.mp4'
    target.parent.mkdir(parents=True,exist_ok=True)
    w,h=film.w,film.h
    num=int(args.version)*30
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{w}x{h}','-r','30','-i','pipe:0','-an','-c:v','libx264',
         '-preset','veryfast','-crf',str(args.crf),'-maxrate','16M','-bufsize','24M',
         '-pix_fmt','yuv420p','-r','30','-g','60','-movflags','+faststart',str(target)]
    print(f'{args.version}s {args.ratio} → {target} | {w}×{h} @ 30 fps ({num} frames)',flush=True)
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(num):
            frame=film.render(i/30)
            assert proc.stdin is not None
            proc.stdin.write(frame.tobytes())
            if i%150==0:print(' ',i,'/',num,flush=True)
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError(f'ffmpeg exit {proc.returncode}')
    except BaseException:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
        proc.kill();proc.wait()
        raise
    print('OK',target,round(target.stat().st_size/1024/1024,1),'MiB',flush=True)


if __name__=='__main__':main()
