# Déclinaisons de la pub à partir d'index.html (9:16) : python3 tools/build_format.py 4x5|1x1
# La scène 1080×1920 est zoomée et centrée ; fonds et bandes en plein cadre ; sous-titres recalés.
import os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = {  # W, H, zoom, y écran du haut du contenu, y sous-titres, taille sous-titres
    "4x5": (1080, 1350, 0.92, 24, 1150, 46),
    "1x1": (1080, 1080, 0.72, 18, 880, 36),
}
key = sys.argv[1]; W, H, Z, Y0, SUBY, SUBF = F[key]
OUT = os.path.join(os.path.dirname(HERE), f"missa-tv-360-40s-{key}")
s = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
left = (W / Z - 1080) / 2; top = Y0 / Z - 190
s = s.replace("html,body { width:1080px; height:1920px;", f"html,body {{ width:{W}px; height:{H}px;")
s = s.replace("#root { position:relative; width:1080px; height:1920px;", f"#root {{ position:relative; width:{W}px; height:{H}px;")
s = s.replace('data-width="1080" data-height="1920"', f'data-width="{W}" data-height="{H}"')
s = s.replace("pub motion design 9:16", f"pub motion design {key.replace('x', ':')}")
css = f"""
/* ---- déclinaison {key} ---- */
.cam {{ inset:auto; left:{left:.1f}px; top:{top:.1f}px; width:1080px; height:1920px; zoom:{Z}; }}
.cam .corner {{ display:none; }}
.scene > .corner {{ display:block; transform-origin:0 0; }}
.scene > .corner.tl {{ transform:scale(.75); }} .scene > .corner.br {{ transform:rotate(180deg) scale(.75); transform-origin:100% 100%; }}
.nightbg::before {{ content:""; position:absolute; inset:0; opacity:.35;
  background-image: radial-gradient(circle, #A6E31B 0 2px, transparent 3px), radial-gradient(circle, #A6E31B 0 1.5px, transparent 2.5px);
  background-size: 260px 230px, 170px 190px; background-position: 30px 40px, 120px 90px; }}
#stamp5 {{ white-space:nowrap; left:500px !important; }}
.sub {{ left:40px; right:40px; top:{SUBY}px; }}
.sub p {{ font-size:{SUBF}px; padding:10px 24px; border-radius:22px; }}
"""
s = s.replace("</style>", css + "</style>", 1)
corners = '<div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>'
s = re.sub(r'<div id="sc\d+" class="scene clip yellowbg"[^>]*>', lambda m: m.group(0) + corners, s)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
open(os.path.join(OUT, "hyperframes.json"), "w").write(open(os.path.join(HERE, "hyperframes.json")).read())
open(os.path.join(OUT, "package.json"), "w").write(f'{{\n  "name": "missa-tv-360-40s-{key}",\n  "private": true,\n  "type": "module"\n}}\n')
for d in ("assets", "vendor"):
    p = os.path.join(OUT, d)
    if not os.path.exists(p): os.symlink(os.path.join("..", "missa-tv-360-40s", d), p)
print(key, "->", OUT)
