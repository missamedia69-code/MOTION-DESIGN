#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"generated"; W,H=1080,1920
Y=(246,190,0); B=(31,52,200); G=(11,154,47); M=(46,204,113); WHITE=(248,250,255); DARK=(11,13,18)
def font(s,b=False):
 p="assets/fonts/Montserrat-Black.ttf" if b else "assets/fonts/Montserrat-Bold.ttf"
 try:return ImageFont.truetype(p,s)
 except OSError:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",s)
def bg(a=(8,14,35),b=(7,9,18)):
 im=Image.new("RGB",(W,H)); px=im.load()
 for y in range(H):
  t=y/(H-1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
  for x in range(W):px[x,y]=c
 return im.convert("RGBA")
def halo(im,cx,cy,r,col,alpha=85):
 l=Image.new("RGBA",im.size,(0,0,0,0));ImageDraw.Draw(l).ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*col,alpha))
 return Image.alpha_composite(im,l.filter(ImageFilter.GaussianBlur(r*.45)))
def panel(im,box,c):
 x0,y0,x1,y1=box;sh=Image.new("RGBA",im.size,(0,0,0,0));ImageDraw.Draw(sh).rounded_rectangle((x0+8,y0+18,x1+8,y1+18),radius=34,fill=(0,0,0,150))
 im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
 ImageDraw.Draw(im).rounded_rectangle(box,radius=34,fill=(17,25,49,242),outline=(*c,170),width=3)
def centered(d,t,y,s,c):
 ff=font(s,True);bb=d.textbbox((0,0),t,font=ff);d.text(((W-bb[2]+bb[0])/2,y),t,font=ff,fill=c)
def catalogue():
 im=halo(bg(),850,250,520,B);im=halo(im,170,1450,520,G);d=ImageDraw.Draw(im)
 d.text((72,90),"UN SEUL ÉCRAN.",font=font(74,True),fill=WHITE);d.text((72,178),"TOUT UN MONDE.",font=font(74,True),fill=Y)
 names=["FILMS","SÉRIES","MANGAS","TV EN DIRECT","SPORT","RADIOS & JEUX"];cols=[Y,M,G,B,Y,G]
 mx,gx,top,gy=58,28,330,34;cw=(W-2*mx-gx)//2;ch=440
 for i,name in enumerate(names):
  x=mx+(i%2)*(cw+gx);y=top+(i//2)*(ch+gy);c=cols[i];panel(im,(x,y,x+cw,y+ch),c);im=halo(im,x+cw//2,y+210,150,c,50);d=ImageDraw.Draw(im);cx=x+cw//2;cy=y+210
  if i in (0,1,3):
   ww,hh=290,195;d.rounded_rectangle((cx-ww//2,cy-hh//2,cx+ww//2,cy+hh//2),radius=25,fill=(8,16,38),outline=c,width=9)
   for k,col in enumerate((Y,G,B)):
    xx=cx-115+k*85;d.rounded_rectangle((xx,cy-55,xx+60,cy+55),radius=12,fill=col)
   d.polygon([(cx-20,cy-35),(cx+45,cy),(cx-20,cy+35)],fill=WHITE)
  elif i==2:
   d.polygon([(cx,cy-140),(cx-130,cy+150),(cx+130,cy+150)],fill=B);d.ellipse((cx-62,cy-100,cx+62,cy+24),fill=(255,210,135))
   d.polygon([(cx-70,cy-30),(cx-25,cy-155),(cx+40,cy-100),(cx+75,cy-155),(cx+65,cy-15)],fill=DARK)
  elif i==4:
   r=112;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=WHITE,outline=Y,width=8)
   pts=[(cx+42*math.cos(-math.pi/2+k*2*math.pi/5),cy+42*math.sin(-math.pi/2+k*2*math.pi/5)) for k in range(5)];d.polygon(pts,fill=DARK)
   for k in range(5):
    a=-math.pi/2+k*2*math.pi/5;xx=cx+83*math.cos(a);yy=cy+83*math.sin(a);d.ellipse((xx-22,yy-22,xx+22,yy+22),fill=DARK)
  else:
   d.arc((cx-130,cy-145,cx+130,cy+115),190,350,fill=Y,width=19);d.rounded_rectangle((cx-150,cy-10,cx-90,cy+130),radius=18,fill=G);d.rounded_rectangle((cx+90,cy-10,cx+150,cy+130),radius=18,fill=G)
   for k,h in enumerate((40,95,145,70,120,50,90)):
    xx=cx-120+k*40;d.rounded_rectangle((xx,cy+170-h//2,xx+18,cy+170+h//2),radius=8,fill=Y if k%2==0 else M)
  d.rounded_rectangle((x+28,y+ch-82,x+cw-28,y+ch-26),radius=25,fill=(*c,245));ff=font(29,True);bb=d.textbbox((0,0),name,font=ff);d.text((cx-(bb[2]-bb[0])/2,y+ch-77),name,font=ff,fill=(9,15,29))
 im.convert("RGB").save(OUT/"catalogue.png",optimize=True)
def devices():
 im=halo(bg((7,12,30),(8,11,22)),540,650,680,B,90);im=halo(im,860,1480,460,G,65);d=ImageDraw.Draw(im)
 d.text((72,95),"LE DIVERTISSEMENT",font=font(58,True),fill=WHITE);d.text((72,172),"VOYAGE AVEC TOI.",font=font(66,True),fill=Y)
 d.rounded_rectangle((120,340,960,1005),radius=56,fill=(12,18,39),outline=(82,120,255),width=10);d.rounded_rectangle((160,380,920,950),radius=28,fill=(19,38,89))
 for i,c in enumerate((Y,G,B)):
  x=210+i*235;d.rounded_rectangle((x,500,x+190,800),radius=25,fill=c);d.ellipse((x+45,545,x+145,645),fill=(250,250,255,160));d.rounded_rectangle((x+25,682,x+165,715),radius=14,fill=(10,15,34,220))
 d.rounded_rectangle((455,1018,625,1060),radius=16,fill=(70,85,110));d.rounded_rectangle((60,1110,500,1700),radius=48,fill=(4,8,16),outline=(160,180,220),width=8);d.rounded_rectangle((95,1140,465,1655),radius=28,fill=(22,39,86));d.rounded_rectangle((135,1200,425,1435),radius=20,fill=Y);d.polygon([(245,1245),(355,1318),(245,1390)],fill=DARK)
 d.rounded_rectangle((630,1110,990,1790),radius=58,fill=(4,8,16),outline=(160,180,220),width=8);d.rounded_rectangle((660,1160,960,1745),radius=35,fill=(18,35,76));d.rounded_rectangle((710,1260,910,1470),radius=22,fill=G);d.ellipse((770,1320,850,1400),fill=Y)
 im.convert("RGB").save(OUT/"appareils.png",optimize=True)
def network():
 im=halo(bg((8,15,38),(6,11,22)),540,850,720,B,90);im=halo(im,540,1420,460,G,65);d=ImageDraw.Draw(im);d.text((72,105),"MÊME À FAIBLE DÉBIT,",font=font(58,True),fill=WHITE);d.text((72,182),"TU RESTES CONNECTÉ.",font=font(63,True),fill=Y)
 cx,cy=540,850
 for r,a in ((180,170),(300,115),(425,72)):d.arc((cx-r,cy-r,cx+r,cy+r),218,322,fill=(46,204,113,a),width=18)
 d.ellipse((cx-35,cy+105,cx+35,cy+175),fill=Y)
 for i,h in enumerate((90,150,220,300,390)):
  x=170+i*155;c=G if i<3 else (Y if i==3 else M);d.rounded_rectangle((x,1430-h,x+90,1430),radius=22,fill=(*c,235))
 d.rounded_rectangle((190,1530,890,1660),radius=62,fill=(11,154,47,245),outline=(46,204,113,255),width=4);centered(d,"LECTURE STABLE",1550,42,(8,20,22));centered(d,"UNE EXPÉRIENCE FLUIDE",1740,27,(157,174,204),False)
 im.convert("RGB").save(OUT/"faible-debit.png",optimize=True)
def main():
 OUT.mkdir(parents=True,exist_ok=True);catalogue();devices();network();print("Visuels générés",*[p.name for p in sorted(OUT.glob("*.png"))])
if __name__=="__main__":main()
