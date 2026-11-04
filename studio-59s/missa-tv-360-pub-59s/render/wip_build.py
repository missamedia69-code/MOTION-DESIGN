#!/usr/bin/env python3
"""Génère index.html — version d'ÉVALUATION (WIP v2, 4 novembre 2026).

Révision visuelle demandée par le propriétaire : « trop touffu », « beaucoup
d'éléments qui se répètent », « pas de trucs vraiment élaborés ». Cette version
applique une cure d'épurement : ~70 éléments visibles au lieu de ~250, une
grille commune (marge 90, colonne 900, contenu 220→1200, sous-titre 1280→1400),
UN point focal par plan, un seul accent coloré par séquence, un filet de
progression continu sur tout le film, et des apparitions uniquement en
transform/opacity. Les transitions (coupes, objet-pont, pivot noir, fondu final)
sont conservées telles quelles, le propriétaire les a jugées cohérentes.

Ce N'EST PAS le film final : VO de travail, aucune musique, placeholders visibles
pour les éléments de la section C, minutage provisoire, aucun calibrage LUFS.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wip_cuts import S  # noqa: E402  (13 fenêtres calées sur les silences)

ONS = json.loads((ROOT / "onsets.json").read_text())
T = {fid: (a, b) for fid, a, b in S}
NO_CAPTION = {1: "gag muet", 4: "pivot typographique",
              9: "moment typographique", 12: "moment typographique"}

# --- charte -----------------------------------------------------------------
INK, DARK, CARD, PAPER, SLATE = "#F4F1EA", "#0B0B0C", "#141416", "#E9E4D6", "#1B1E22"
YELLOW, GREEN, GREEN2, NEG, LIVE = "#F5BB00", "#009E49", "#2FD37A", "#B5473A", "#E53935"
GREY, MUTED, HAIR = "#8d8b86", "#b9b6ae", "rgba(244,241,234,.14)"
M, CW = 90, 900                       # marge / largeur de la grille commune


def at(fid, off=0.0):
    return T[fid][0] + off


def dur(fid):
    return T[fid][1] - T[fid][0]


JS: list[str] = []


def j(s):
    JS.append(s)


def pop(sel, t, d=0.18, scale=1.5, blur=0, rot=None, ease="power3.out"):
    f = f"{{opacity:0, scale:{scale}"
    if rot is not None:
        f += f", rotation:{rot}"
    if blur:
        f += f', filter:"blur({blur}px)"'
    f += "}"
    o = "{opacity:1, scale:1"
    if rot is not None:
        o += f", rotation:{rot}"
    if blur:
        o += ', filter:"blur(0px)"'
    o += f', duration:{d}, ease:"{ease}"}}'
    j(f'tl.fromTo("{sel}", {f}, {o}, {t:.3f});')


def draw(sel, t, d=0.36):
    # opacity:1 dans le "from" : les éléments .h partent à 0, sans fade-in
    # (évite les échecs de contraste transitoires détectés par `validate`).
    j(f'tl.fromTo("{sel}", {{opacity:1, scaleX:0}}, '
      f'{{scaleX:1, duration:{d}, ease:"power3.out"}}, {t:.3f});')


def hide(sel, t, d=0.16):
    j(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t:.3f});')


def fade(sel, t, d=0.18, to=1):
    j(f'tl.to("{sel}", {{opacity:{to}, duration:{d}, ease:"power2.out"}}, {t:.3f});')


def move(sel, t, d, frm, to, ease="power2.inOut"):
    j(f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration:{d}, ease:"{ease}"}}, {t:.3f});')


def drift(fid, frm="scale:1.075,y:26", to="scale:1,y:-26"):
    move(f"#s-{fid.lower()}", at(fid), dur(fid), frm, to, "none")


def lift(sel, t, y=-14, d=0.22):
    j(f'tl.to("{sel}", {{y:{y}, duration:{d}, ease:"power2.out"}}, {t:.3f});')


def sethtml(sel, t, text):
    j(f'tl.set("{sel}", {{opacity:1, innerHTML:"{text}"}}, {t:.3f});')


HTML: list[str] = []


def label(fid, text, x, y, size, color, cls="mono", weight=400,
          ls="0em", w=None, align="left", extra=""):
    width = f"width:{w}px;" if w is not None else ""
    return (f'<div class="h {cls}" id="{fid}" style="position:absolute;left:{x}px;'
            f'top:{y}px;{width}font-size:{size}px;line-height:1.08;color:{color};'
            f'font-weight:{weight};letter-spacing:{ls};text-align:{align};{extra}">'
            f'{text}</div>')


def box(fid, x, y, w, h, fill="transparent", stroke=HAIR, radius=0, sw=2, extra=""):
    return (f'<div class="h" id="{fid}" style="position:absolute;left:{x}px;top:{y}px;'
            f'width:{w}px;height:{h}px;background:{fill};border:{sw}px solid {stroke};'
            f'border-radius:{radius}px;{extra}"></div>')


def hair(fid, x, y, w, color=HAIR, h=2, origin="left center"):
    return (f'<div class="h" id="{fid}" style="position:absolute;left:{x}px;top:{y}px;'
            f'width:{w}px;height:{h}px;background:{color};'
            f'transform-origin:{origin}"></div>')


def kw(fid, text, x, y, color=YELLOW, ink=DARK):
    return (f'<div class="h mono" id="{fid}" style="position:absolute;left:{x}px;top:{y}px;'
            f'padding:8px 18px;border-radius:5px;background:{color};color:{ink};'
            f'font-size:34px;font-weight:700;letter-spacing:.06em">{text}</div>')


def ph(fid, text, y=1490):
    return (f'<div class="h mono" id="{fid}" style="position:absolute;left:{M}px;top:{y}px;'
            f'width:{CW}px;text-align:center;font-size:20px;color:{MUTED};'
            f'letter-spacing:.02em">{text}</div>')


def scene(fid, bg, inner, track):
    a, b = T[fid]
    glow = "#24282d" if bg == SLATE else "#17181b"
    depth = f"radial-gradient(ellipse 82% 58% at 50% 34%, {glow} 0%, {bg} 78%)"
    HTML.append(
        f'<div class="clip scene" id="s-{fid.lower()}" data-start="{a:.2f}" '
        f'data-duration="{b-a:.2f}" data-track-index="{track}" '
        f'style="position:absolute;inset:0;background:{depth};overflow:hidden">'
        f'{inner}</div>')


# ===========================================================================
# MONDE 1 — papier / ardoise. Aucun jaune. Un seul accent : rouge brique.
# ===========================================================================

# F01 — première image = LE TICKET (jamais le logo) ------------------------
lignes = ["1er DU MOIS", "CHAÎNES : LES MÊMES", "TOTAL XAF ••••"]
f01 = (
    box("f01-card", 140, 300, 800, 760, fill=PAPER, stroke="transparent", radius=6, sw=0,
        extra="box-shadow:0 30px 90px rgba(0,0,0,.45)") +
    label("f01-head", "REÇU / ABONNEMENT", 200, 372, 22, "#6b6860", weight=700, ls=".28em") +
    hair("f01-rule", 200, 438, 680, "rgba(26,24,21,.22)", 2) +
    "".join(label(f"f01-l{i}", t, 200, 500 + i * 130, 30, "#1A1815",
                  weight=700, ls=".04em")
            for i, t in enumerate(lignes)) +
    f'<div class="h mono" id="f01-stamp" style="position:absolute;left:640px;top:820px;'
    f'width:220px;height:220px;border:6px solid {NEG};border-radius:50%;display:flex;'
    f'align-items:center;justify-content:center;font-size:24px;font-weight:700;'
    f'color:{NEG}">RENOUVELÉ</div>'
)
scene("F01", SLATE, f01, 10)
pop("#f01-card", at("F01", 0.04), 0.22, 1.10, 8)
pop("#f01-head", at("F01", 0.18), 0.16, 1.2, 0)
draw("#f01-rule", at("F01", 0.22), 0.40)
for i, t in enumerate([0.32, 0.52, 0.72]):
    pop(f"#f01-l{i}", at("F01", t), 0.16, 1.2, 5)
pop("#f01-stamp", at("F01", 1.05), 0.20, 2.0, 10, rot=-12)

# F02 — gag muet : une seule touche, une seule tuile, un compteur -----------
f02 = (
    box("f02-screen", M, 330, CW, 300, fill="#22262a", stroke=HAIR, radius=8) +
    box("f02-tile", 465, 405, 150, 150, fill="#8d8b84", stroke="#6e6c66", radius=8, sw=3) +
    hair("f02-rule", M, 680, CW, "rgba(244,241,234,.10)", 1) +
    box("f02-remote", 390, 770, 300, 500, stroke="#5b5f63", radius=48, sw=3) +
    f'<div class="h" id="f02-ok" style="position:absolute;left:490px;top:900px;'
    f'width:100px;height:100px;border-radius:50%;background:{NEG};display:flex;'
    f'align-items:center;justify-content:center;color:#fff;font-family:Space Mono;'
    f'font-size:30px;font-weight:700">OK</div>' +
    label("f02-count", "x1", M, 1140, 54, INK, weight=700)
)
scene("F02", SLATE, f02, 11)
pop("#f02-screen", at("F02", 0.02), 0.18, 1.1, 6)
pop("#f02-tile", at("F02", 0.16), 0.16, 1.3, 5)
pop("#f02-remote", at("F02", 0.10), 0.18, 1.15, 6)
pop("#f02-ok", at("F02", 0.22), 0.16, 1.4, 4)
draw("#f02-rule", at("F02", 0.30), 0.45)
pop("#f02-count", at("F02", 0.28), 0.16, 1.3, 4)
for i, t in enumerate([0.50, 1.20, 1.90]):
    j(f'tl.to("#f02-ok", {{scale:0.88, duration:0.07, yoyo:true, repeat:1}}, '
      f'{at("F02", t):.3f});')
    sethtml("#f02-count", at("F02", t + 0.06), f"x{i + 2}")

# F03 — mêmes chaînes : 3 cartes identiques, une seule étiquette ------------
f03 = ""
for i in range(3):
    x = M + i * 310
    f03 += (box(f"f03-c{i}", x, 430, 280, 420, fill="#22262a", stroke="#6e6c66", radius=10, sw=3) +
            box(f"f03-i{i}", x + 90, 520, 100, 100, fill="#8d8b84", stroke="transparent",
                radius=6, sw=0))
f03 += (hair("f03-rule", M, 940, CW, "rgba(244,241,234,.12)", 1) +
        label("f03-tag", "REDIFFUSION", M, 1000, 28, NEG, weight=700, ls=".18em"))
scene("F03", SLATE, f03, 12)
for i in range(3):
    pop(f"#f03-c{i}", at("F03", 0.10 + i * 0.14), 0.18, 1.4, 6)
    pop(f"#f03-i{i}", at("F03", 0.18 + i * 0.14), 0.16, 1.3, 4)
draw("#f03-rule", at("F03", 2.05), 0.45)
pop("#f03-tag", at("F03", 2.25), 0.18, 1.5, 5)

# F04 — une seule barre PUB, une seule pièce qui s'en va --------------------
f04 = (
    box("f04-pub", M, 430, CW, 130, fill="#5f6266", stroke="transparent", radius=6, sw=0) +
    label("f04-pubtxt", "PUB", M, 466, 54, PAPER, weight=700, ls=".4em", w=CW, align="center") +
    hair("f04-rule", 240, 660, 600, "rgba(244,241,234,.12)", 1) +
    box("f04-coin", 490, 780, 100, 100,
        fill="radial-gradient(circle at 30% 30%,#d8d5cc,#8b8880)",
        stroke="#6e6c66", radius=50, sw=3) +
    label("f04-total", "TOTAL XAF ••••", M, 1080, 34, MUTED, weight=700, w=CW, align="center")
)
scene("F04", SLATE, f04, 13)
draw("#f04-pub", at("F04", 0.05), 0.30)
pop("#f04-pubtxt", at("F04", 0.28), 0.16, 1.2, 4)
draw("#f04-rule", at("F04", 0.55), 0.40)
pop("#f04-coin", at("F04", 1.55), 0.18, 1.7, 6)
j(f'tl.to("#f04-coin", {{y:230, x:-300, rotation:220, duration:1.25, '
  f'ease:"power2.in"}}, {at("F04", 1.70):.3f});')
pop("#f04-total", at("F04", 2.20), 0.18, 1.3, 4)

# F05 — pivot sur noir, un seul moment typographique -----------------------
f05 = (
    label("f05-a", "ON MÉRITE", 0, 820, 84, INK, cls="big", weight=800, w=1080, align="center") +
    label("f05-b", "MIEUX.", 0, 910, 84, INK, cls="big", weight=800, w=1080, align="center") +
    hair("f05-rule", 390, 1030, 300, YELLOW, 4, "center center") +
    '<div class="h" id="f05-black" style="position:absolute;inset:0;background:#0B0B0C"></div>' +
    f'<div class="h" id="f05-dot" style="position:absolute;left:535px;top:955px;'
    f'width:10px;height:10px;border-radius:50%;background:{YELLOW}"></div>'
)
scene("F05", SLATE, f05, 14)
pop("#f05-a", at("F05", 0.00), 0.18, 2.0, 8)
pop("#f05-b", at("F05", 0.22), 0.18, 2.0, 8)
draw("#f05-rule", at("F05", 0.50), 0.26)
fade("#f05-black", at("F05", 1.52), 0.02)
pop("#f05-dot", at("F05", 1.72), 0.18, 1.0, 0)
j(f'tl.to("#f05-dot", {{scale:5, duration:0.32, ease:"none"}}, {at("F05", 1.92):.3f});')

# ===========================================================================
# MONDE 2 — noir MISSA. Jaune #F5BB00 = unique accent.
# ===========================================================================
UNIV = ["Films & Mangas", "Séries", "Documentaires",
        "TV Direct", "Podcasts", "Radio"]

# F06 — révélation : logo + LA GRILLE (un seul objet, 6 univers réels) ------
cells = ""
for i, u in enumerate(UNIV):
    x = M + (i % 3) * 300
    y = 880 + (i // 3) * 160
    active = (i == 0)
    cells += (f'<div class="h" id="f06-g{i}" style="position:absolute;left:{x}px;top:{y}px;'
              f'width:300px;height:160px;border-right:1px solid {HAIR};'
              f'border-bottom:1px solid {HAIR};display:flex;align-items:center;'
              f'justify-content:center;font-family:Space Mono;font-size:28px;'
              f'color:{YELLOW if active else INK};'
              f'{"background:rgba(245,187,0,.07);" if active else ""}">{u}</div>')
f06 = (
    '<img id="f06-logo" class="h" src="assets/img/logo-officiel.png" alt="MISSA TV 360" '
    'style="position:absolute;left:340px;top:330px;width:400px;height:400px;border-radius:24px">' +
    hair("f06-top", M, 878, CW, HAIR, 1) + cells +
    ph("f06-ph", "[CAPTURES_APP] · [MUSIQUE ELAN]")
)
scene("F06", DARK, f06, 20)
pop("#f06-logo", at("F06", 0.30), 0.22, 1.5, 8)
draw("#f06-top", at("F06", 0.95), 0.45)
for i in range(6):
    pop(f"#f06-g{i}", at("F06", 1.05 + i * 0.08), 0.16, 1.15, 3)
pop("#f06-ph", at("F06", 3.30), 0.16, 1.0, 0)

# F07 — MILLIERS : une pile de 3 cartes, un mot-clé en petite boîte --------
f07 = kw("f07-kw", "MILLIERS", M, 300)
for i in range(3):
    y = 780 - i * 165
    f07 += (box(f"f07-c{i}", 190, y, 620, 300,
                fill=["#15171a", "#202327", "#2c2f34"][i], stroke=HAIR,
                radius=10, sw=2,
                extra="border-top:4px solid #F5BB00;" if i == 2 else "") +
            hair(f"f07-l{i}", 230, y + 52, 540, HAIR, 1))
f07 += (f'<div class="h" id="f07-play" style="position:absolute;left:468px;top:565px;'
        f'width:0;height:0;border-left:42px solid {INK};'
        f'border-top:26px solid transparent;border-bottom:26px solid transparent"></div>' +
        hair("f07-rule", M, 1150, CW, HAIR, 1) +
        ph("f07-ph", "[CAPTURES_APP] — interfaces vectorielles fictives"))
scene("F07", DARK, f07, 21)
pop("#f07-kw", at("F07", 0.05), 0.18, 1.4, 4)
for i in range(3):
    pop(f"#f07-c{i}", at("F07", 0.35 + i * 0.28), 0.20, 1.25, 5)
    draw(f"#f07-l{i}", at("F07", 0.50 + i * 0.28), 0.30)
pop("#f07-play", at("F07", 1.55), 0.18, 1.6, 4)
draw("#f07-rule", at("F07", 1.60), 0.55)
pop("#f07-ph", at("F07", 4.20), 0.16, 1.0, 0)

# F08 — CENTAINES : un seul écran, un seul badge LIVE, 3 lignes -------------
f08 = (kw("f08-kw", "CENTAINES", M, 300) +
       box("f08-tv", M, 400, CW, 520, fill=CARD, stroke=HAIR, radius=10) +
       f'<div class="h mono" id="f08-live" style="position:absolute;left:120px;top:430px;'
       f'padding:6px 14px;border-radius:4px;background:{LIVE};color:#0B0B0C;'
       f'font-size:24px;font-weight:700">LIVE</div>' +
       box("f08-dot", 490, 590, 100, 100, fill=GREEN2, stroke="transparent", radius=50, sw=0))
for i in range(3):
    f08 += (hair(f"f08-r{i}", M, 1000 + i * 72, CW,
                 YELLOW if i == 1 else HAIR, 2) +
            f'<div class="h" id="f08-d{i}" style="position:absolute;left:{M}px;'
            f'top:{985 + i * 72}px;width:12px;height:12px;border-radius:50%;'
            f'background:{YELLOW if i == 1 else GREY}"></div>')
scene("F08", DARK, f08, 22)
pop("#f08-kw", at("F08", 0.05), 0.18, 1.4, 4)
pop("#f08-tv", at("F08", 0.25), 0.20, 1.12, 6)
pop("#f08-live", at("F08", 0.75), 0.16, 1.4, 4)
pop("#f08-dot", at("F08", 1.00), 0.20, 1.6, 6)
for i in range(3):
    draw(f"#f08-r{i}", at("F08", 2.20 + i * 0.18), 0.40)
    pop(f"#f08-d{i}", at("F08", 2.25 + i * 0.18), 0.16, 1.3, 0)

# F09 — podcasts / radios : un cadran, une seule onde de 12 barres ---------
f09 = (kw("f09-kw", "MILLIERS", M, 300) +
       box("f09-dial", 290, 400, 500, 500, stroke="rgba(244,241,234,.30)",
           radius=250, sw=3) +
       f'<div class="h" id="f09-arc" style="position:absolute;left:350px;top:460px;'
       f'width:380px;height:380px;border:3px solid transparent;'
       f'border-top-color:rgba(245,187,0,.55);'
       f'border-right-color:rgba(245,187,0,.55);'
       f'border-radius:50%;transform:rotate(-35deg)"></div>' +
       f'<div class="h" id="f09-hand" style="position:absolute;left:290px;top:400px;'
       f'width:500px;height:500px;transform-origin:50% 50%">'
       f'<div style="position:absolute;left:245px;top:18px;width:10px;height:10px;'
       f'border-radius:50%;background:{YELLOW}"></div></div>')
for i in range(12):
    h = 80 + (i * 37) % 150
    f09 += (f'<div class="h" id="f09-b{i}" style="position:absolute;'
            f'left:{122 + i * 70}px;top:{1000 - h}px;width:44px;height:{h}px;'
            f'background:rgba(47,211,122,.72);border-radius:4px;'
            f'transform-origin:bottom center"></div>')
f09 += (hair("f09-rule", M, 1010, CW, HAIR, 1) +
        ph("f09-ph", "[MUSIQUE ELAN] — en attente des 2 pistes CC0"))
scene("F09", DARK, f09, 23)
pop("#f09-kw", at("F09", 0.05), 0.18, 1.4, 4)
pop("#f09-dial", at("F09", 0.25), 0.22, 1.3, 6)
pop("#f09-arc", at("F09", 0.35), 0.20, 1.15, 0)
j(f'tl.to("#f09-arc", {{rotation:55, duration:{dur("F09") - 0.6:.2f}, '
  f'ease:"none"}}, {at("F09", 0.55):.3f});')
pop("#f09-hand", at("F09", 0.50), 0.18, 1.0, 0)
j(f'tl.to("#f09-hand", {{rotation:42, duration:{dur("F09") - 0.5:.2f}, '
  f'ease:"none"}}, {at("F09", 0.50):.3f});')
for i in range(12):
    j(f'tl.fromTo("#f09-b{i}", {{opacity:1, scaleY:0.15}}, '
      f'{{scaleY:1, duration:0.26, ease:"power3.out"}}, {at("F09", 0.90 + i * 0.055):.3f});')
draw("#f09-rule", at("F09", 1.70), 0.55)
pop("#f09-ph", at("F09", 4.20), 0.16, 1.0, 0)

# F10 — une seule application : 3 écrans → 1, moment typographique ---------
f10 = (box("f10-p", 170, 380, 220, 380, stroke="#5b5f63", radius=24, sw=3) +
       box("f10-t", 430, 340, 220, 420, stroke="#5b5f63", radius=20, sw=3) +
       box("f10-v", 690, 400, 220, 340, stroke="#5b5f63", radius=16, sw=3) +
       box("f10-one", 430, 340, 220, 420, stroke=YELLOW, radius=20, sw=3) +
       label("f10-type", "UNE SEULE<br>APPLICATION.", 0, 900, 84, INK,
             cls="big", weight=800, w=1080, align="center") +
       ph("f10-ph", "[CAPTURES_APP] — téléphone portrait + Android TV"))
scene("F10", DARK, f10, 24)
for i, k in enumerate(["p", "t", "v"]):
    pop(f"#f10-{k}", at("F10", 0.02 + i * 0.22), 0.18, 1.3, 5)
for k in ["p", "t", "v"]:
    hide(f"#f10-{k}", at("F10", 1.15), 0.22)
pop("#f10-one", at("F10", 1.15), 0.18, 1.2, 4)
pop("#f10-type", at("F10", 1.35), 0.20, 1.4, 6)
pop("#f10-ph", at("F10", 1.75), 0.16, 1.0, 0)

# F11 — prix mensuel : XAF 1 000 / mois ------------------------------------
f11 = (
    box("f11-card", M, 400, CW, 560, fill=CARD, stroke=HAIR, radius=12) +
    label("f11-q", "?", M, 470, 100, YELLOW, cls="big", weight=800, w=CW, align="center") +
    label("f11-prix", "XAF 1&#8239;000", M, 610, 132, YELLOW,
          cls="big", weight=800, w=CW, align="center") +
    label("f11-mois", "/ mois", M, 790, 46, INK, cls="sans", weight=600, w=CW, align="center") +
    hair("f11-rule", 240, 890, 600, GREEN, 3)
)
scene("F11", DARK, f11, 25)
pop("#f11-card", at("F11", 0.02), 0.20, 1.06, 6)
pop("#f11-q", at("F11", 0.25), 0.18, 1.8, 6)
hide("#f11-q", at("F11", 0.95), 0.14)
pop("#f11-prix", at("F11", 0.95), 0.22, 1.5, 8)
pop("#f11-mois", at("F11", 1.75), 0.18, 1.2, 4)
draw("#f11-rule", at("F11", 2.10), 0.45)

# F12 — prix annuel : 12 segments = 10 payés + 2 offerts -------------------
f12 = (
    label("f12-prix", "XAF 10&#8239;000", M, 300, 132, YELLOW,
          cls="big", weight=800, w=CW, align="center") +
    label("f12-an", "/ an", M, 470, 46, INK, cls="sans", weight=600, w=CW, align="center") +
    hair("f12-rule", M, 660, CW, HAIR, 1)
)
for i in range(12):
    col = GREEN if i >= 10 else YELLOW
    f12 += (f'<div class="h" id="f12-s{i}" style="position:absolute;left:{124 + i * 70}px;'
            f'top:700px;width:62px;height:56px;border-radius:4px;background:{col};'
            f'transform-origin:left center"></div>')
f12 += (
    label("f12-off", "2 MOIS OFFERTS", M, 850, 72, YELLOW,
          cls="big", weight=800, w=CW, align="center") +
    label("f12-jour", "moins de XAF 30 / jour", M, 970, 30, INK, w=CW, align="center")
)
scene("F12", DARK, f12, 26)
pop("#f12-prix", at("F12", 0.02), 0.22, 1.5, 8)
pop("#f12-an", at("F12", 0.75), 0.18, 1.2, 4)
draw("#f12-rule", at("F12", 1.10), 0.50)
for i in range(12):
    draw(f"#f12-s{i}", at("F12", 1.30 + i * 0.055), 0.22)
for i in (10, 11):
    lift(f"#f12-s{i}", at("F12", 3.30 + (i - 10) * 0.12))
pop("#f12-off", at("F12", 3.70), 0.20, 1.5, 6)
pop("#f12-jour", at("F12", 4.50), 0.18, 1.2, 4)

# F13 — CTA : un logo, un bouton, UNE zone de placeholders -----------------
f13 = (
    '<img id="f13-logo" class="h" src="assets/img/logo-officiel.png" alt="MISSA TV 360" '
    'style="position:absolute;left:420px;top:210px;width:240px;height:240px;border-radius:18px">' +
    label("f13-type", "TON ÉCRAN<br>MÉRITE MIEUX.", 0, 520, 84, INK,
          cls="big", weight=800, w=1080, align="center") +
    f'<div class="h big" id="f13-btn" style="position:absolute;left:240px;top:850px;'
    f'width:600px;height:120px;border-radius:999px;background:{YELLOW};color:{DARK};'
    f'font-size:56px;font-weight:800;display:flex;align-items:center;'
    f'justify-content:center">Télécharger</div>' +
    f'<div class="h mono" id="f13-ph" style="position:absolute;left:{M}px;top:1080px;'
    f'width:{CW}px;height:290px;border:2px dashed {GREY};border-radius:10px;'
    f'padding:22px;color:{MUTED};font-size:21px;line-height:1.9;text-align:center">'
    '[VOIX] · [MUSIQUE TENSION] · [MUSIQUE ELAN]<br>'
    '[QR_CODE] · [LIEN_TELECHARGEMENT]<br>'
    '[MODES_DE_PAIEMENT] · [CONDITIONS_OFFRE]<br>'
    '[CAPTURES_APP]</div>' +
    '<div class="h" id="f13-black" style="position:absolute;inset:0;background:#0B0B0C"></div>'
)
scene("F13", DARK, f13, 27)
pop("#f13-logo", at("F13", 0.02), 0.18, 1.3, 5)
pop("#f13-type", at("F13", 0.25), 0.20, 1.5, 6)
pop("#f13-btn", at("F13", 0.75), 0.20, 1.4, 6)
pop("#f13-ph", at("F13", 1.15), 0.18, 1.0, 0)
j(f'tl.to("#f13-logo", {{scale:1.03, duration:2.6, ease:"none"}}, '
  f'{at("F13", 0.40):.3f});')
fade("#f13-black", at("F13", 3.10), 0.29)

# dérive continue : caméra jamais à l'arrêt (grille de contrôle N.2)
for fid, a, b in S:
    drift(fid)

# --- rail de progression : UN seul objet sur tout le film -----------------
rail = (
    f'<div class="clip" id="rail" data-start="0" data-duration="59" '
    f'data-track-index="62" style="position:absolute;inset:0;pointer-events:none">'
    f'<div style="position:absolute;left:{M}px;top:150px;width:{CW}px;height:2px;'
    f'background:rgba(244,241,234,.14)"></div>'
    + f'<div style="position:absolute;left:{M}px;top:240px;width:56px;height:2px;'
    f'background:rgba(244,241,234,.22)"></div>' \
    + f'<div style="position:absolute;left:{M}px;top:240px;width:2px;height:56px;'
    f'background:rgba(244,241,234,.22)"></div>' \
    + f'<div style="position:absolute;left:{M + CW - 56}px;top:1200px;width:56px;'
    f'height:2px;background:rgba(244,241,234,.22)"></div>' \
    + f'<div style="position:absolute;left:{M + CW - 2}px;top:1144px;width:2px;'
    f'height:56px;background:rgba(244,241,234,.22)"></div>' \
    f'<div id="rail-fill" style="position:absolute;left:{M}px;top:150px;width:{CW}px;'
    f'height:2px;transform-origin:left center;transform:scaleX(0);'
    f'background:linear-gradient(to right,{NEG} 0 28%,{YELLOW} 28% 100%)"></div></div>'
)
j('tl.fromTo("#rail-fill", {scaleX:0}, {scaleX:1, duration:59, ease:"none"}, 0);')

# --- sous-titres mot à mot (bande y 1280→1400) -----------------------------
KEYWORDS = {"paies": "neg", "mêmes": "neg", "pubs": "neg", "seule": "acc",
            "milliers": "acc", "centaines": "acc", "mille": "acc", "offerts": "acc"}
UNDERLINE = {"chose", "vues", "trente", "mérites"}
no_cap = [(S[i][1], S[i][2]) for i in NO_CAPTION]

caps = []
for k, p in enumerate(ONS["phrases"]):
    if not p["text"]:
        continue
    a, b = p["start"], min(p["end"], 58.70)
    if any(x <= a < y for x, y in no_cap):
        continue
    n = max(1, len(p["text"]))
    fs = min(62, max(46, int(930 / (n * 0.53))))   # une seule ligne, jamais de wrap
    spans = []
    for wi, w in enumerate(p["words"]):
        key = re.sub(r"[^\wÀ-ÿ]", "", w["w"]).lower()
        cls = ""
        if key in KEYWORDS:
            cls = "kw-neg" if KEYWORDS[key] == "neg" else "kw-acc"
        if key in UNDERLINE:
            cls += " u"
        spans.append(f'<span id="w-{k}-{wi}" class="h {cls}" '
                     f'style="margin:0 6px;font-size:{fs}px">{w["w"]}</span>')
        t = min(max(w["s"], a), b - 0.01)
        j(f'tl.fromTo("#w-{k}-{wi}", {{opacity:1, y:7}}, '
          f'{{y:0, duration:0.12, ease:"power3.out"}}, {t:.3f});')
    caps.append(
        f'<div id="cap-{k}" class="h" style="position:absolute;left:60px;top:1280px;'
        f'width:960px;height:120px;display:flex;align-items:center;'
        f'justify-content:center;white-space:nowrap;overflow:hidden;'
        f'background:rgba(11,11,12,.88);border-top:1px solid rgba(244,241,234,.18);'
        f'border-radius:6px">' + "".join(spans) + "</div>")
    j(f'tl.set("#cap-{k}", {{opacity:1}}, {a:.3f});')
    j(f'tl.set("#cap-{k}", {{opacity:0}}, {b:.3f});')

caps_html = (f'<div class="clip" id="caps" data-start="0" data-duration="59" '
             f'data-track-index="60" style="position:absolute;inset:0;'
             f'pointer-events:none">' + "".join(caps) + "</div>")

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
.h{opacity:0}.mono{font-family:'Space Mono'}.sans{font-family:'Instrument Sans'}
.big{font-family:'Big Shoulders'}
#caps span{font-family:'Instrument Sans';font-weight:600;color:#F4F1EA;line-height:1.1}
#caps .kw-neg{background:#B5473A;color:#E9E4D6;padding:0 10px;border-radius:4px}
#caps .kw-acc{background:#F5BB00;color:#0B0B0C;padding:0 10px;border-radius:4px}
#caps .u{border-bottom:3px solid currentColor}
#grain{position:absolute;inset:0;pointer-events:none;opacity:.025;mix-blend-mode:screen;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='g'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23g)'/></svg>");
 background-size:200px 200px}
"""

html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<title>MISSA TV 360 — TON ÉCRAN MÉRITE MIEUX — WIP v2 (épuré) 59 s</title>
<style>{CSS}</style>
<script src="assets/js/gsap.min.js"></script>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="59"
     data-width="1080" data-height="1920" data-fps="30">
{"".join(HTML)}
<div class="clip" id="grain" data-start="0" data-duration="59" data-track-index="1"></div>
{caps_html}
{rail}
</div>
<script>
(function(){{
  var tl = gsap.timeline({{paused:true, defaults:{{immediateRender:false}}}});
{chr(10).join("  " + x for x in JS)}
  tl.set("#root", {{opacity:1}}, 58.99);
  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
}})();
</script></body></html>'''

(ROOT / "index.html").write_text(html)
print(f"✅ index.html : {len(HTML)} scènes, {len(JS)} tweens, "
      f"{len(caps)} bandeaux de sous-titre, {len(html) // 1024} Ko")
print("   éléments visibles :", sum(x.count('class="h') for x in HTML +
      [caps_html, rail]), "(objectif : ~70, contre ~250 en WIP v1)")
