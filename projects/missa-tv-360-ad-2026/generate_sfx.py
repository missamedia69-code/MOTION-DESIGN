#!/usr/bin/env python3
"""Original procedural sound effects; no stock recordings or copyrighted music."""
from pathlib import Path
import math, random, struct, wave
ROOT=Path(__file__).resolve().parent/"sfx"; RATE=44100
def write(name,duration,fn,seed):
 random.seed(seed); n=int(RATE*duration); vals=[]; peak=1e-9
 for i in range(n):
  t=i/RATE; v=max(-1,min(1,fn(t,duration))); vals.append(v); peak=max(peak,abs(v))
 gain=.72/peak; ROOT.mkdir(parents=True,exist_ok=True)
 with wave.open(str(ROOT/name),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
  w.writeframes(b"".join(struct.pack("<h",int(v*gain*32767)) for v in vals))
 print(ROOT/name)
def env(t,d,p=1): return max(0,math.sin(math.pi*t/d))**p
def main():
 write("impact.wav",.72,lambda t,d:.78*math.sin(2*math.pi*(58*t-15*t*t))*math.exp(-7*t)+.22*(random.random()*2-1)*math.exp(-75*t),1)
 write("whoosh.wav",.85,lambda t,d:env(t,d,.65)*(.58*math.sin(2*math.pi*(95*t+390*t*t/d))+.32*(random.random()*2-1)+.1*math.sin(2*math.pi*1200*t)),2)
 write("pop.wav",.24,lambda t,d:.8*math.sin(2*math.pi*(920-520*t/d)*t)*math.exp(-12*t)+.15*(random.random()*2-1)*math.exp(-50*t),3)
 write("sparkle.wav",.72,lambda t,d:math.exp(-5*t)*(.45*math.sin(2*math.pi*1480*t)+.33*math.sin(2*math.pi*2140*t)+.22*math.sin(2*math.pi*2870*t)),4)
 write("click.wav",.11,lambda t,d:(math.sin(2*math.pi*1850*t)+.25*math.sin(2*math.pi*3700*t))*math.exp(-110*t),5)
 write("rise.wav",1.05,lambda t,d:env(t,d,1.15)*.78*math.sin(2*math.pi*(180+700*t/d)*t),6)
if __name__=="__main__":main()
