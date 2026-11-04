#!/usr/bin/env python3
"""Génère index.html : version d'ÉVALUATION (WIP) du film 59 s, rendue par HyperFrames 0.8.82.

Ce N'EST PAS le film final :
  - voix = assets/audio/voix-temporaire.mp3 (repère), pas voix.mp3 ;
  - pas de musique (2 pistes CC0 attendues) ;
  - [CAPTURES_APP], [QR_CODE], [LIEN_TELECHARGEMENT], [MODES_DE_PAIEMENT],
    [CONDITIONS_OFFRE] restent des PLACEHOLDERS visibles ;
  - onsets.json est provisoire (répartition déterministe, pas Whisper) ;
  - animation simplifiée : transform/opacity/scale uniquement, caméra en dérive.

Tout est vectoriel / typographique : aucune photo, aucune image IA.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONS = json.loads((ROOT / "onsets.json").read_text())
WORDS = ONS["words"]

# --- séquences (recalage provisoire, somme = 59,00 s) -----------------------
S = [
    ("F01", 0.00, 4.00), ("F02", 4.00, 6.52), ("F03", 6.52, 11.07),
    ("F04", 11.07, 14.48), ("F05", 14.48, 16.53), ("F06", 16.53, 22.11),
    ("F07", 22.11, 27.80), ("F08", 27.80, 34.55), ("F09", 34.55, 40.62),
    ("F10", 40.62, 43.07), ("F11", 43.07, 48.38), ("F12", 48.38, 55.16),
    ("F13", 55.16, 59.00),
]
NO_CAPTION = [(4.00, 6.52), (14.48, 16.53), (40.62, 43.07), (55.16, 59.00)]

KEYWORDS = {
    "paies": "neg", "mêmes": "neg", "pubs": "neg", "seule": "acc",
    "milliers": "acc", "centaines": "acc", "deux": "acc", "mille": "acc",
    "offerts": "acc",
}
UNDERLINE = {"chose", "vues", "trente", "mérites"}

JS: list[str] = []
def j(s: str) -> None: JS.append(s)

def pop(sel, at, dur=0.20, scale=1.6, blur=0, ease="power3.out"):
    f = f'{{opacity:0, scale:{scale}' + (f', filter:"blur({blur}px)"' if blur else '') + '}'
    t = '{opacity:1, scale:1' + (', filter:"blur(0px)"' if blur else '')
    t += f', duration:{dur}, ease:"{ease}"}}'
    j(f'tl.fromTo("{sel}", {f}, {t}, {at:.3f});')

def fade(sel, at, dur=0.18, to=1):
    j(f'tl.to("{sel}", {{opacity:{to}, duration:{dur}, ease:"power2.out"}}, {at:.3f});')

def move(sel, at, dur, frm, to, ease="power2.inOut"):
    j(f'tl.fromTo("{sel}", {frm}, {{{to}, duration:{dur}, ease:"{ease}"}}, {at:.3f});')

def hide(sel, at, dur=0.16):
    j(f'tl.to("{sel}", {{opacity:0, duration:{dur}}}, {at:.3f});')

HTML: list[str] = []

def scene(fid, a, b, bg, inner, track):
    HTML.append(
        f'<div class="clip scene" id="s-{fid.lower()}" data-start="{a:.2f}" '
        f'data-duration="{b-a:.2f}" data-track-index="{track}" '
        f'style="position:absolute;inset:0;background:{bg};overflow:hidden">{inner}</div>')

# ---------------------------------------------------------------------------
# MONDE 1 — papier / ardoise, aucun jaune
# ---------------------------------------------------------------------------
lines = ["ABONNEMENT RENOUVELÉ", "1er DU MOIS", "CHAÎNES : LES MÊMES",
         "FILMS : LES MÊMES", "PUBS : INCLUSES", "TOTAL XAF ••••"]
li = "".join(
    f'<div class="h tk" id="f01-l{i}" style="position:absolute;left:60px;top:{230+i*115}px;'
    f'font-size:30px;font-weight:700;letter-spacing:.04em">{t}</div>'
    for i, t in enumerate(lines))
inner = f'''
<div style="position:absolute;left:0;right:0;top:0;height:170px;background:linear-gradient(#0c0e10,#30343a)"></div>
<div style="position:absolute;left:150px;top:150px;width:780px;height:26px;background:#0a0b0d;border-radius:0 0 14px 14px"></div>
<div id="f01-ticket" style="position:absolute;left:220px;top:120px;width:640px;height:1700px;
     background:#E9E4D6;border-radius:4px;box-shadow:0 24px 80px rgba(0,0,0,.55)">
  <div style="padding:70px 0 0 60px;font-family:'Space Mono';font-size:22px;letter-spacing:.3em">REÇU / ABONNEMENT</div>
  {li}
  <div id="f01-repeat" style="position:absolute;left:60px;top:960px;font-family:'Space Mono';font-size:26px">
     <div class="h" id="f01-r1">MÊME FILM</div><div class="h" id="f01-r2" style="margin-top:22px">MÊME FILM</div>
     <div class="h" id="f01-r3" style="margin-top:22px">MÊME FILM</div></div>
</div>
<div id="f01-stamp" class="h" style="position:absolute;left:600px;top:790px;width:230px;height:230px;
     border:9px solid #B5473A;border-radius:50%;display:flex;align-items:center;justify-content:center;
     font-family:'Space Mono';font-weight:700;font-size:26px;color:#B5473A;transform:rotate(-14deg)">RENOUVELÉ</div>
<div class="h" id="f01-lune" style="position:absolute;left:760px;top:430px;font-size:56px">☾</div>
'''
scene("F01", 0, 4.00, "#1B1E22", inner, 10)
for i, t in enumerate([0.12, 0.30, 0.45, 0.60, 0.75, 0.90]):
    pop(f"#f01-l{i}", t, 0.16, 1.15, 5)
pop("#f01-stamp", 1.00, 0.20, 2.2, 10)
pop("#f01-lune", 2.10, 0.20, 2.0, 6)
for i, t in enumerate([2.40, 2.62, 2.84]):
    pop(f"#f01-r{i+1}", t, 0.18, 1.3, 5)
move("#f01-ticket", 0, 4.0, "{y:0}", "y:-150", "none")

# F02 — gag muet ------------------------------------------------------------
tiles2 = "".join(
    f'<div class="h" id="f02-t{i}" style="width:150px;height:110px;background:#8d8b84;border-radius:8px;'
    f'border:3px solid #6e6c66"></div>' for i in range(6))
inner = f'''
<div style="position:absolute;left:330px;top:420px;width:420px;height:760px;background:#2b2f33;
     border-radius:60px;box-shadow:inset 0 0 0 8px #3a3f44">
  <div id="f02-ok" style="position:absolute;left:130px;top:210px;width:160px;height:160px;border-radius:50%;
       background:#B5473A;display:flex;align-items:center;justify-content:center;
       font-family:'Big Shoulders';font-size:52px;color:#fff;font-weight:800">OK</div>
  <div style="position:absolute;left:70px;top:70px;width:280px;height:70px;background:#1c2023;border-radius:12px"></div>
</div>
<div id="f02-counter" class="h mono" style="position:absolute;left:790px;top:470px;font-size:96px;font-weight:700;color:#F4F1EA">x1</div>
<div style="position:absolute;left:80px;top:1280px;display:flex;gap:14px">{tiles2}</div>
<div id="f02-load" class="h" style="position:absolute;left:410px;top:1330px;width:90px;height:90px;
     border:9px solid #5b5f63;border-top-color:#F4F1EA;border-radius:50%"></div>
<div id="f02-face" class="h" style="position:absolute;left:440px;top:1350px;font-size:54px;color:#1A1815">• •<br>━</div>
'''
scene("F02", 4.00, 6.52, "#1B1E22", inner, 11)
pop("#f02-ok", 4.05, 0.15, 1.0, 0)
j('tl.to("#f02-ok", {scale:0.9, duration:0.08, yoyo:true, repeat:1}, 4.20);')
for i in range(6):
    pop(f"#f02-t{i}", 4.22 + i * 0.16, 0.14, 1.4, 4)
for i, t in enumerate([4.20, 4.70, 5.00, 5.30, 5.60, 5.75, 5.90]):
    j(f'tl.set("#f02-counter", {{opacity:1, innerHTML:"x{i+1}"}}, {t:.3f});')
pop("#f02-load", 5.60, 0.18, 1.8, 6)
j('tl.to("#f02-load", {rotation:180, duration:0.5, ease:"none"}, 5.60);')
pop("#f02-face", 6.00, 0.16, 1.5, 4)

# F03 — mêmes chaînes / séries ---------------------------------------------
t3 = "".join(
    f'<div class="h" id="f03-t{i}" style="position:absolute;left:{90+(i%2)*470}px;top:{300+(i//2)*215}px;'
    f'width:430px;height:180px;background:#8d8b84;border:3px solid #6e6c66;border-radius:10px">'
    f'<span class="mono" style="font-size:22px;color:#1A1815;padding:10px">CHAÎNE {i+1:02d}</span></div>'
    for i in range(12))
inner = f'''{t3}
<div id="f03-vu" class="h mono" style="position:absolute;left:700px;top:1700px;font-size:44px;color:#F4F1EA">VU x10</div>
''' + "".join(
    f'<div class="h mono" id="f03-r{i}" style="position:absolute;left:{120+i*300}px;top:{1120+i*60}px;'
    f'font-size:32px;color:#B5473A;border:5px solid #B5473A;padding:6px 14px;transform:rotate(-8deg)">REDIFFUSION</div>'
    for i in range(3))
scene("F03", 6.52, 11.07, "#1B1E22", inner, 12)
for i in range(12):
    pop(f"#f03-t{i}", 6.60 + i * 0.09, 0.16, 1.5, 5)
for i, t in enumerate([9.00, 9.22, 9.44]):
    pop(f"#f03-r{i}", t, 0.18, 2.0, 6)
pop("#f03-vu", 9.85, 0.20, 1.8, 5)
move("#s-f03", 6.52, 4.55, "{scale:1.04}", "scale:1", "none")

# F04 — pubs / argent -------------------------------------------------------
pubs = "".join(
    f'<div class="h mono" id="f04-p{i}" style="position:absolute;left:70px;top:{300+i*180}px;'
    f'width:940px;height:96px;background:#5f6266;display:flex;align-items:center;justify-content:center;'
    f'font-size:44px;font-weight:700;color:#E9E4D6;letter-spacing:.3em">PUB</div>' for i in range(7))
coins = "".join(
    f'<div class="h" id="f04-c{i}" style="position:absolute;left:{280+i*70}px;top:1000px;width:64px;height:64px;'
    f'border-radius:50%;background:radial-gradient(circle at 30% 30%,#d8d5cc,#8b8880);border:3px solid #6e6c66"></div>'
    for i in range(8))
inner = f'''<div id="f04-ticket" style="position:absolute;left:220px;top:150px;width:640px;height:1500px;background:#E9E4D6;border-radius:4px">
  <div class="h mono" id="f04-total" style="position:absolute;left:60px;top:780px;font-size:52px;color:#1A1815">TOTAL XAF ••••</div></div>
{pubs}{coins}'''
scene("F04", 11.07, 14.48, "#1B1E22", inner, 13)
for i in range(7):
    pop(f"#f04-p{i}", 11.10 + i * 0.15, 0.16, 1.2, 4)
pop("#f04-total", 12.50, 0.18, 1.4, 6)
for i in range(8):
    t = 13.00 + i * 0.06
    pop(f"#f04-c{i}", t, 0.18, 1.8, 5)
    move(f"#f04-c{i}", t, 0.9, "{y:0}", f"y:{560+i*30}, x:{-260-i*40}, rotation:{180+i*25}", "power2.in")
hide("#f04-ticket", 14.10, 0.30)

# F05 — pivot sur noir ------------------------------------------------------
inner = '''
<div id="f05-on" class="h big" style="position:absolute;left:0;right:0;top:840px;text-align:center;font-size:84px;color:#F4F1EA">ON</div>
<div id="f05-merite" class="h big" style="position:absolute;left:0;right:0;top:940px;text-align:center;font-size:84px;color:#F4F1EA">MÉRITE</div>
<div id="f05-mieux" class="h big" style="position:absolute;left:0;right:0;top:1040px;text-align:center;font-size:84px;color:#F4F1EA">MIEUX.</div>
<div id="f05-trait" class="h" style="position:absolute;left:390px;top:1140px;width:300px;height:5px;background:#F5BB00"></div>
<div id="f05-black" class="h" style="position:absolute;inset:0;background:#0B0B0C"></div>
<div id="f05-dot" class="h" style="position:absolute;left:536px;top:956px;width:8px;height:8px;border-radius:50%;background:#F5BB00"></div>
'''
scene("F05", 14.48, 16.53, "#1B1E22", inner, 14)
for i, (sel, t) in enumerate([("#f05-on", 14.48), ("#f05-merite", 14.73), ("#f05-mieux", 14.98)]):
    pop(sel, t, 0.18, 2.5, 8)
pop("#f05-trait", 15.20, 0.16, 1.0, 0)
fade("#f05-black", 16.00, 0.02)
pop("#f05-dot", 16.20, 0.20, 1.0, 0)
j('tl.to("#f05-dot", {scale:3, duration:0.3, ease:"none"}, 16.25);')

# ---------------------------------------------------------------------------
# MONDE 2 — noir MISSA, jaune #F5BB00 réservé
# ---------------------------------------------------------------------------
def pill(label, i, active=False):
    col, bg = ("#0B0B0C", "#F5BB00") if active else ("#F4F1EA", "#1f2022")
    return (f'<div class="h" id="f06-p{i}" style="display:inline-block;margin:7px;padding:14px 24px;'
            f'border-radius:999px;background:{bg};color:{col};font-family:Instrument Sans;'
            f'font-size:26px;font-weight:600;white-space:nowrap">{label}</div>')
UNIV = ["Accueil", "Films & Mangas", "Séries", "Documentaires", "Courts", "Enfants",
        "TV Direct", "Sports", "Musiques", "Podcasts", "Radio", "Jeux rétro"]
pills = "".join(pill(u, i, i == 1) for i, u in enumerate(UNIV))
inner = f'''
<div id="f06-tri" class="h" style="position:absolute;left:470px;top:880px;width:0;height:0;
     border-left:90px solid #F5BB00;border-top:55px solid transparent;border-bottom:55px solid transparent"></div>
<img id="f06-logo" class="h" src="assets/img/logo-officiel.png" alt="MISSA TV 360"
     style="position:absolute;left:290px;top:560px;width:500px;height:500px;border-radius:36px">
<div id="f06-pills" style="position:absolute;left:80px;top:1120px;width:920px;text-align:center">{pills}</div>
<div class="h mono" id="f06-ph" style="position:absolute;left:80px;top:1700px;width:920px;text-align:center;
     font-size:22px;color:#8d8b86">INTERFACES : [CAPTURES_APP] · [MUSIQUE ELAN] — placeholder</div>
'''
scene("F06", 16.53, 22.11, "#0B0B0C", inner, 20)
pop("#f06-tri", 16.53, 0.20, 6.0, 12)
hide("#f06-tri", 16.85, 0.12)
pop("#f06-logo", 16.90, 0.22, 1.6, 8)
for i in range(12):
    pop(f"#f06-p{i}", 17.75 + i * 0.12, 0.16, 1.4, 5)
pop("#f06-ph", 20.20, 0.16, 1.0, 0)
move("#f06-logo", 17.40, 4.5, "{scale:1}", "scale:0.82", "none")

# F07 — films / séries / docs / mangas -------------------------------------
posters = "".join(
    f'<div class="h" id="f07-a{i}" style="position:absolute;left:{90+i*160}px;top:360px;width:140px;height:210px;'
    f'border-radius:10px;background:linear-gradient({140+i*25}deg,#12303a,#2b1d4a,#6b4a12)"></div>'
    for i in range(6))
eps = "".join(
    f'<div class="h mono" id="f07-e{i}" style="position:absolute;left:{90+(i%4)*240}px;top:{680+(i//4)*70}px;'
    f'font-size:26px;color:#F4F1EA">S01 É{i+1:02d}</div>' for i in range(12))
panels = "".join(
    f'<div class="h" id="f07-m{i}" style="position:absolute;left:{90+(i%2)*470}px;top:{1000+(i//2)*230}px;'
    f'width:430px;height:200px;border:4px solid #F4F1EA;border-radius:6px;'
    f'background:repeating-linear-gradient(115deg,#141416 0 14px,#232326 14px 20px)"></div>'
    for i in range(4))
inner = f'''{posters}{eps}{panels}
<div id="f07-btn" class="h big" style="position:absolute;left:390px;top:580px;padding:16px 42px;border-radius:999px;
     background:#F5BB00;color:#0B0B0C;font-size:38px;font-weight:800">Regarder</div>
<div id="f07-kw" class="h mono" style="position:absolute;left:80px;top:230px;font-size:46px;color:#F5BB00;letter-spacing:.16em">MILLIERS</div>
<div class="h mono" id="f07-ph" style="position:absolute;left:80px;top:1700px;font-size:22px;color:#8d8b86">[CAPTURES_APP] — vignettes fictives</div>'''
scene("F07", 22.11, 27.80, "#0B0B0C", inner, 21)
pop("#f07-kw", 22.11, 0.18, 1.5, 5)
for i in range(6):
    pop(f"#f07-a{i}", 22.20 + i * 0.10, 0.18, 1.6, 6)
pop("#f07-btn", 23.00, 0.18, 1.8, 6)
for i in range(12):
    pop(f"#f07-e{i}", 23.80 + i * 0.07, 0.14, 1.2, 4)
for i in range(4):
    pop(f"#f07-m{i}", 25.70 + i * 0.12, 0.18, 1.5, 5)
pop("#f07-ph", 26.60, 0.16, 1.0, 0)
move("#s-f07", 22.11, 5.69, "{x:60}", "x:-60", "none")

# F08 — chaînes en direct ---------------------------------------------------
ch = "".join(
    f'<div class="h" id="f08-c{i}" style="position:absolute;left:{70+(i%5)*190}px;top:{300+(i//5)*205}px;'
    f'width:170px;height:175px;border-radius:12px;background:#1a1b1e;border:2px solid #33343a;'
    f'display:flex;align-items:center;justify-content:center"><div style="width:60px;height:60px;border-radius:50%;'
    f'background:hsl({i*29} 65% 52%)"></div></div>' for i in range(40))
live = "".join(
    f'<div class="h mono" id="f08-l{i}" style="position:absolute;left:{80+(i%5)*190}px;top:{300+(i//5)*205+130}px;'
    f'background:#E53935;color:#0B0B0C;font-size:18px;padding:3px 8px;border-radius:4px;font-weight:700">LIVE</div>'
    for i in range(6))
inner = f'''{ch}{live}
<div id="f08-kw" class="h mono" style="position:absolute;left:80px;top:200px;font-size:46px;color:#F5BB00;letter-spacing:.16em">CENTAINES</div>
<div id="f08-sport" class="h big" style="position:absolute;left:70px;top:1400px;font-size:44px;color:#F4F1EA">SPORT · INFO · ENFANTS</div>
<div id="f08-pin" class="h mono" style="position:absolute;left:70px;top:1500px;font-size:34px;color:#2FD37A">PIN • • • •</div>'''
scene("F08", 27.80, 34.55, "#0B0B0C", inner, 22)
pop("#f08-kw", 27.80, 0.18, 1.5, 5)
for i in range(40):
    pop(f"#f08-c{i}", 28.00 + i * 0.045, 0.14, 1.6, 6)
for i in range(6):
    pop(f"#f08-l{i}", 28.70 + i * 0.10, 0.14, 1.4, 4)
pop("#f08-sport", 32.30, 0.18, 1.4, 4)
pop("#f08-pin", 33.30, 0.18, 1.4, 4)
move("#s-f08", 27.80, 6.75, "{y:40}", "y:-40", "none")

# F09 — podcasts / radios / musique ----------------------------------------
bars = "".join(
    f'<div class="h" id="f09-b{i}" style="position:absolute;left:{90+i*38}px;top:{520+(i%5)*18}px;'
    f'width:20px;height:{60+(i*37)%160}px;background:#2FD37A;border-radius:6px"></div>' for i in range(24))
dots = "".join(
    f'<div class="h" id="f09-d{i}" style="position:absolute;left:{80+(i%20)*48}px;top:{760+(i//20)*44}px;'
    f'width:9px;height:9px;border-radius:50%;background:{"#F5BB00" if i < 70 else "#F4F1EA"}"></div>'
    for i in range(120))
inner = f'''{bars}{dots}
<div id="f09-kw" class="h mono" style="position:absolute;left:80px;top:210px;font-size:46px;color:#F5BB00;letter-spacing:.16em">MILLIERS DE RADIOS</div>
<div id="f09-mic" class="h" style="position:absolute;left:500px;top:300px;width:70px;height:130px;
     border-radius:40px;background:#F4F1EA"></div>
<div id="f09-player" class="h" style="position:absolute;left:80px;top:1480px;width:920px;height:150px;
     background:#141416;border-radius:20px;border:2px solid #33343a;display:flex;align-items:center;gap:26px;padding:0 30px">
   <div style="width:70px;height:70px;border-radius:12px;background:#2FD37A"></div>
   <div><div class="sans" style="font-size:30px;color:#F4F1EA">RADIO SAVANE</div>
   <div class="mono" style="font-size:20px;color:#8d8b86">station fictive · En direct</div></div>
   <div style="margin-left:auto;font-size:40px;color:#F4F1EA">❚❚ ▶</div></div>
<div id="f09-casque" class="h" style="position:absolute;left:390px;top:1650px;font-size:70px;color:#F4F1EA">⌒ ◯ ◯</div>'''
scene("F09", 34.55, 40.62, "#0B0B0C", inner, 23)
pop("#f09-kw", 34.55, 0.18, 1.5, 5)
pop("#f09-mic", 34.70, 0.18, 2.0, 6)
for i in range(24):
    pop(f"#f09-b{i}", 34.70 + i * 0.025, 0.14, 1.2, 3)
for i in range(120):
    pop(f"#f09-d{i}", 35.55 + (i // 20) * 0.30, 0.18, 1.0, 0)
pop("#f09-player", 38.55, 0.20, 1.2, 5)
pop("#f09-casque", 39.35, 0.18, 1.4, 4)

# F10 — une seule application ----------------------------------------------
def device(kind, left, w, h, top):
    return (f'<div class="h" id="f10-{kind}" style="position:absolute;left:{left}px;top:{top}px;'
            f'width:{w}px;height:{h}px;border:8px solid #3a3b40;border-radius:26px;background:#141416;'
            f'display:flex;align-items:center;justify-content:center;text-align:center">'
            f'<div class="mono" style="font-size:22px;color:#8d8b86;padding:16px">[CAPTURES_APP]<br>{kind.upper()}</div></div>')
inner = (device("phone", 90, 250, 460, 520) + device("tablette", 380, 320, 430, 535) +
         device("tv", 740, 250, 420, 540) +
         '<div id="f10-type" class="h big" style="position:absolute;left:0;right:0;top:1080px;'
         'text-align:center;font-size:84px;color:#F4F1EA;line-height:1.05">UNE SEULE<br>APPLICATION.</div>'
         '<div id="f10-check" class="h" style="position:absolute;left:490px;top:1320px;font-size:70px;color:#2FD37A">0 ✓</div>')
scene("F10", 40.62, 43.07, "#0B0B0C", inner, 24)
for i, k in enumerate(["phone", "tablette", "tv"]):
    pop(f"#f10-{k}", 40.62 + i * 0.55, 0.18, 1.5, 6)
pop("#f10-type", 41.80, 0.20, 1.4, 6)
pop("#f10-check", 42.60, 0.16, 1.6, 4)
for k in ["phone", "tablette", "tv"]:
    hide(f"#f10-{k}", 41.75, 0.25)

# F11 — prix mensuel --------------------------------------------------------
inner = '''
<div id="f11-ticket" class="h" style="position:absolute;left:190px;top:430px;width:700px;height:900px;
     background:#141416;border:2px solid #2b2c30;border-radius:12px"></div>
<div id="f11-q" class="h big" style="position:absolute;left:0;right:0;top:500px;text-align:center;
     font-size:200px;color:#F5BB00;font-weight:800">?</div>
<div id="f11-prix" class="h big" style="position:absolute;left:0;right:0;top:620px;text-align:center;
     font-size:150px;color:#F5BB00;font-weight:800;line-height:1">XAF 2 000</div>
<div id="f11-mois" class="h sans" style="position:absolute;left:0;right:0;top:800px;text-align:center;
     font-size:52px;color:#F4F1EA;font-weight:600">/ mois</div>
<div id="f11-stamp" class="h mono" style="position:absolute;left:330px;top:960px;padding:16px 38px;
     border:6px solid #009E49;border-radius:10px;color:#2FD37A;font-size:38px;transform:rotate(-8deg)">ACTIVÉ</div>
'''
scene("F11", 43.07, 48.38, "#0B0B0C", inner, 25)
pop("#f11-ticket", 43.07, 0.18, 1.1, 5)
pop("#f11-q", 43.40, 0.18, 2.0, 8)
hide("#f11-q", 44.00, 0.15)
pop("#f11-prix", 44.00, 0.22, 1.8, 8)
pop("#f11-mois", 44.90, 0.18, 1.3, 5)
pop("#f11-stamp", 46.60, 0.20, 2.2, 6)
move("#f11-prix", 47.70, 0.60, "{y:0}", "y:-160, opacity:0", "power2.in")

# F12 — prix annuel, 7 mois offerts ----------------------------------------
cal = ""
for i in range(12):
    bg = "#F5BB00" if i < 5 else "#009E49"
    label = f"M{i+1}" if i < 5 else "OFFERT"
    fg = "#0B0B0C" if i < 5 else "#ffffff"
    size = 42 if i < 5 else 30
    cal += (f'<div class="h" id="f12-c{i}" style="position:absolute;left:{90+(i%3)*310}px;'
            f'top:{720+(i//3)*170}px;width:280px;height:145px;border-radius:14px;background:{bg};'
            f'display:flex;align-items:center;justify-content:center;font-family:Big Shoulders;'
            f'font-size:{size}px;font-weight:800;color:{fg}">{label}</div>')
inner = f'''
<div id="f12-prix" class="h big" style="position:absolute;left:0;right:0;top:300px;text-align:center;
     font-size:150px;color:#F5BB00;font-weight:800;line-height:1">XAF 10 000</div>
<div id="f12-an" class="h sans" style="position:absolute;left:0;right:0;top:470px;text-align:center;
     font-size:52px;color:#F4F1EA;font-weight:600">/ an</div>
{cal}
<div id="f12-7" class="h big" style="position:absolute;left:0;right:0;top:1440px;text-align:center;
     font-size:76px;color:#F5BB00;font-weight:800">7 MOIS OFFERTS</div>
<div id="f12-jour" class="h mono" style="position:absolute;left:0;right:0;top:1560px;text-align:center;
     font-size:34px;color:#F4F1EA">moins de XAF 30 / jour</div>'''
scene("F12", 48.38, 55.16, "#0B0B0C", inner, 26)
pop("#f12-prix", 48.38, 0.22, 1.8, 8)
pop("#f12-an", 49.20, 0.18, 1.3, 5)
for i in range(12):
    pop(f"#f12-c{i}", 49.60 + i * 0.05, 0.16, 1.5, 5)
for i in range(7):
    j(f'tl.to("#f12-c{5+i}", {{scale:1.08, duration:0.16, yoyo:true, repeat:1}}, {51.20+i*0.20:.3f});')
pop("#f12-7", 52.80, 0.20, 1.6, 6)
pop("#f12-jour", 53.80, 0.18, 1.3, 5)
j('tl.to("#f12-c7", {scale:1.08, duration:0.3, yoyo:true, repeat:1}, 54.80);')

# F13 — CTA -----------------------------------------------------------------
inner = '''
<img id="f13-logo" class="h" src="assets/img/logo-officiel.png" alt="MISSA TV 360"
     style="position:absolute;left:390px;top:170px;width:300px;height:300px;border-radius:24px">
<div id="f13-btn" class="h big" style="position:absolute;left:240px;top:560px;width:600px;height:130px;
     border-radius:999px;background:#F5BB00;color:#0B0B0C;font-size:56px;font-weight:800;
     display:flex;align-items:center;justify-content:center">Télécharger</div>
<div id="f13-ok" class="h big" style="position:absolute;left:390px;top:560px;width:300px;height:130px;
     border-radius:999px;background:#009E49;color:#fff;font-size:76px;font-weight:800;
     display:flex;align-items:center;justify-content:center">✓</div>
<div id="f13-qr" class="h mono" style="position:absolute;left:90px;top:760px;width:260px;height:260px;
     border:3px dashed #8d8b86;color:#8d8b86;font-size:22px;display:flex;align-items:center;
     justify-content:center;text-align:center">[QR_CODE]</div>
<div id="f13-lien" class="h mono" style="position:absolute;left:400px;top:800px;width:600px;font-size:24px;
     color:#F4F1EA">[LIEN_TELECHARGEMENT]</div>
<div id="f13-type" class="h big" style="position:absolute;left:0;right:0;top:1090px;text-align:center;
     font-size:84px;color:#F4F1EA;line-height:1.05">TON ÉCRAN<br>MÉRITE MIEUX.</div>
<div id="f13-chœur" class="h sans" style="position:absolute;left:0;right:0;top:1310px;text-align:center;
     font-size:38px;color:#F5BB00;font-weight:600">On est ensemble !</div>
<div id="f13-micro" class="h mono" style="position:absolute;left:240px;top:1420px;width:600px;padding:20px;
     background:#E9E4D6;color:#1A1815;border-radius:8px;text-align:center;font-size:26px">MISSA TV 360 · ACTIVÉ</div>
<div id="f13-conditions" class="h mono" style="position:absolute;left:80px;top:1620px;width:920px;
     text-align:center;font-size:19px;color:#8d8b86">[CONDITIONS_OFFRE] · [MODES_DE_PAIEMENT] · [MUSIQUE ELAN]</div>
<div id="f13-black" class="h" style="position:absolute;inset:0;background:#0B0B0C"></div>'''
scene("F13", 55.16, 59.00, "#0B0B0C", inner, 27)
pop("#f13-logo", 55.16, 0.18, 1.4, 5)
pop("#f13-btn", 55.30, 0.18, 1.6, 6)
hide("#f13-btn", 56.10, 0.12)
pop("#f13-ok", 56.10, 0.18, 1.6, 5)
pop("#f13-qr", 56.40, 0.18, 1.3, 4)
pop("#f13-lien", 56.40, 0.18, 1.3, 4)
pop("#f13-type", 56.60, 0.20, 1.5, 6)
pop("#f13-chœur", 57.60, 0.18, 1.4, 4)
pop("#f13-micro", 58.00, 0.18, 1.2, 4)
pop("#f13-conditions", 58.10, 0.16, 1.0, 0)
fade("#f13-black", 58.70, 0.30)
move("#f13-logo", 57.60, 1.3, "{scale:1}", "scale:1.03", "none")

# --- sous-titres mot à mot --------------------------------------------------
caps = []
for k, p in enumerate(ONS["phrases"]):
    if not p["text"]:
        continue
    a, b = p["start"], min(p["end"], 58.70)
    if any(x <= a < y for x, y in NO_CAPTION):
        continue
    spans = []
    for wi, w in enumerate(p["words"]):
        key = re.sub(r"[^\wÀ-ÿ]", "", w["w"]).lower()
        cls = ""
        if key in KEYWORDS:
            cls = "kw-neg" if KEYWORDS[key] == "neg" else "kw-acc"
        if key in UNDERLINE:
            cls += " u"
        spans.append(f'<span id="w-{k}-{wi}" class="h {cls}" style="margin:0 8px">{w["w"]}</span>')
        t = min(max(w["s"], a), b - 0.01)
        j(f'tl.fromTo("#w-{k}-{wi}", {{opacity:0, y:8}}, '
          f'{{opacity:1, y:0, duration:0.14, ease:"power3.out"}}, {t:.3f});')
    caps.append(
        f'<div id="cap-{k}" class="h" style="position:absolute;left:80px;top:1280px;width:920px;'
        f'height:120px;display:flex;align-items:center;justify-content:center;flex-wrap:wrap;'
        f'background:rgba(11,11,12,.78);border-radius:16px">{"".join(spans)}</div>')
    j(f'tl.set("#cap-{k}", {{opacity:1}}, {a:.3f});')
    j(f'tl.to("#cap-{k}", {{opacity:0, duration:0.14}}, {max(a+0.1,b-0.14):.3f});')

caps_html = (f'<div class="clip" id="caps" data-start="0" data-duration="59" '
             f'data-track-index="60" style="position:absolute;inset:0;pointer-events:none">'
             + "".join(caps) + "</div>")

# --- document final ---------------------------------------------------------
CSS = """
@font-face{font-family:'Instrument Sans';src:url('assets/fonts/InstrumentSans-400.woff2') format('woff2');font-weight:400}
@font-face{font-family:'Instrument Sans';src:url('assets/fonts/InstrumentSans-500.woff2') format('woff2');font-weight:500}
@font-face{font-family:'Instrument Sans';src:url('assets/fonts/InstrumentSans-600.woff2') format('woff2');font-weight:600}
@font-face{font-family:'Instrument Sans';src:url('assets/fonts/InstrumentSans-700.woff2') format('woff2');font-weight:700}
@font-face{font-family:'Space Mono';src:url('assets/fonts/SpaceMono-400.woff2') format('woff2');font-weight:400}
@font-face{font-family:'Space Mono';src:url('assets/fonts/SpaceMono-700.woff2') format('woff2');font-weight:700}
@font-face{font-family:'Big Shoulders';src:url('assets/fonts/BigShoulders-800.woff2') format('woff2');font-weight:800}
*{box-sizing:border-box}html,body{margin:0;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0B0B0C;
      font-family:'Instrument Sans',sans-serif;-webkit-font-smoothing:antialiased}
.h{opacity:0}.tk{font-family:'Space Mono';color:#1A1815}.mono{font-family:'Space Mono'}
.sans{font-family:'Instrument Sans'}.big{font-family:'Big Shoulders'}
.kw-neg{background:#B5473A;color:#E9E4D6;padding:2px 10px;border-radius:4px}
.kw-acc{background:#F5BB00;color:#0B0B0C;padding:2px 10px;border-radius:4px}
.u{border-bottom:4px solid currentColor}
#caps span{font-family:'Instrument Sans';font-size:62px;font-weight:600;color:#F4F1EA;line-height:1.1}
#caps .kw-neg{font-size:62px;padding:0 10px;color:#E9E4D6}
#caps .kw-acc{font-size:62px;padding:0 10px;color:#0B0B0C}
#grain{position:absolute;inset:0;pointer-events:none;opacity:.05;mix-blend-mode:screen;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23g)'/></svg>");
 background-size:200px 200px}
"""

html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>MISSA TV 360 — TON ÉCRAN MÉRITE MIEUX — WIP 59 s</title>
<style>{CSS}</style>
<script src="assets/js/gsap.min.js"></script>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="59"
     data-width="1080" data-height="1920" data-fps="30">
{"".join(HTML)}
<div class="clip" id="grain" data-start="0" data-duration="59" data-track-index="1"></div>
{caps_html}
</div>
<script>
(function(){{
  var tl = gsap.timeline({{paused:true, defaults:{{immediateRender:false}}}});
{chr(10).join("  "+x for x in JS)}
  tl.set("#root", {{opacity:1}}, 58.99);
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
}})();
</script></body></html>'''

(ROOT / "index.html").write_text(html)
print(f"✅ index.html : {len(HTML)} scènes, {len(JS)} tweens, "
      f"{len(caps)} bandeaux de sous-titre, {len(html)//1024} Ko")
