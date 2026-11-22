# Version paysage 16:9 (1920×1080) dérivée de index.html (9:16) :
# fonds plein cadre, scène centrale (zoom 0,78), bandes et objets 3D sur les côtés, sous-titres recalés.
import os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(HERE), "missa-tv-360-40s-16x9")
s = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
Z = 0.78
left = (1920 / Z - 1080) / 2; top = -122 / Z
s = s.replace("html,body { width:1080px; height:1920px;", "html,body { width:1920px; height:1080px;")
s = s.replace("#root { position:relative; width:1080px; height:1920px;", "#root { position:relative; width:1920px; height:1080px;")
s = s.replace('data-width="1080" data-height="1920"', 'data-width="1920" data-height="1080"')
s = s.replace("<title>MISSA TV 360 — pub motion design 9:16</title>", "<title>MISSA TV 360 — pub motion design 16:9</title>")
css16 = f"""
/* ---- adaptation 16:9 ---- */
.cam {{ inset:auto; left:{left:.1f}px; top:{top:.1f}px; width:1080px; height:1920px; zoom:{Z}; }}
.cam .corner {{ display:none; }}
.scene > .corner {{ display:block; }}
.side {{ position:absolute; width:330px; filter: drop-shadow(0 30px 40px rgba(0,0,0,.35)); opacity:0; }}
.nightbg::before {{ content:""; position:absolute; inset:0; opacity:.35;
  background-image: radial-gradient(circle, #A6E31B 0 2px, transparent 3px), radial-gradient(circle, #A6E31B 0 1.5px, transparent 2.5px);
  background-size: 260px 230px, 170px 190px; background-position: 30px 40px, 120px 90px; }}
#stamp5 {{ white-space:nowrap; }}
.sub {{ left:200px; right:200px; top:966px; }}
.sub p {{ font-size:42px; padding:10px 26px; border-radius:22px; }}
"""
s = s.replace("</style>", css16 + "</style>", 1)
corners = '<div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>'
SIDES = {"sc3": ("television-3d", "film-projector-3d", 4.5), "sc4": ("popcorn-3d", "headphone-3d", 8.7),
         "sc5": ("film-frames-3d", "clapper-board-3d", 13.9), "sc6": ("antenna-bars-3d", "mobile-phone-with-arrow-3d", 16.5),
         "sc8": ("party-popper-3d", "wrapped-gift-3d", 23.0), "sc9": ("studio-microphone-3d", "party-popper-3d", 25.3),
         "sc10": ("mobile-phone-with-arrow-3d", "television-3d", 29.8)}
js16 = []
def add(m):
    tag, sid = m.group(0), m.group(1)
    extra = corners if "yellowbg" in tag else ""
    if sid in SIDES:
        a, b, t = SIDES[sid]
        extra += (f'<img class="side" id="{sid}L" src="assets/elements/{a}.png" style="left:110px;top:300px;transform:rotate(-10deg)"/>'
                  f'<img class="side" id="{sid}R" src="assets/elements/{b}.png" style="right:110px;top:380px;transform:rotate(10deg)"/>')
        for k, (side, dx) in enumerate([("L", -260), ("R", 260)]):
            js16.append(f'tl.fromTo("#{sid}{side}", {{ opacity: 0, x: {dx}, scale: 0.5 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.45, ease: "back.out(1.7)" }}, {t + k * 0.12:.2f});')
            js16.append(f'floaty("#{sid}{side}", {t + 0.6 + k * 0.2:.2f}, {t + 3.0:.2f}, 16, 1.4);')
    return tag + extra
s = re.sub(r'<div id="(sc\d+)" class="scene clip[^"]*"[^>]*>', add, s)
s = s.replace('window.__timelines["main"] = tl;', "/* objets latéraux 16:9 */\n" + "\n".join(js16) + '\nwindow.__timelines["main"] = tl;')
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
for f in ("hyperframes.json",):
    open(os.path.join(OUT, f), "w").write(open(os.path.join(HERE, f)).read())
open(os.path.join(OUT, "package.json"), "w").write('{\n  "name": "missa-tv-360-40s-16x9",\n  "private": true,\n  "type": "module"\n}\n')
for d in ("assets", "vendor"):
    p = os.path.join(OUT, d)
    if not os.path.exists(p): os.symlink(os.path.join("..", "missa-tv-360-40s", d), p)
print("16:9 ->", OUT, "| objets latéraux:", len(js16) // 2)
