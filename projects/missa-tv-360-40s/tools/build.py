# words.json + composition.tpl -> index.html (9:16) + sous-titres .srt
import json, os, html
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(HERE, "words.json"), encoding="utf-8"))
DUR = round(d["duration"], 3)
words = d["words"]
# morceaux de sous-titres : ≤ 30 caractères, coupés aux fins de phrase
chunks, cur = [], []
for i, w in enumerate(words):
    txt = " ".join(x["w"] for x in cur + [w])
    if cur and (len(txt) > 30 or cur[-1]["line"] != w["line"] or cur[-1]["w"][-1] in "?!:" or (cur[-1]["w"].endswith(".") and not cur[-1]["w"].endswith("..."))):
        chunks.append(cur); cur = []
    cur.append(w)
chunks.append(cur)
subs, js, srt = [], [], []
def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")
for ci, ch in enumerate(chunks):
    s = max(0.0, ch[0]["s"] - 0.05)
    e = chunks[ci + 1][0]["s"] - 0.05 if ci + 1 < len(chunks) else DUR
    e = min(e, ch[-1]["e"] + 0.8) if ci + 1 < len(chunks) else e
    spans = "".join(f'<span id="w{ci}_{k}">{html.escape(w["w"])}</span>' for k, w in enumerate(ch))
    subs.append(f'<div class="sub clip" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="{20 + ci % 2}"><p>{spans}</p></div>')
    for k, w in enumerate(ch):
        js.append(f'tl.set("#w{ci}_{k}", {{ color: "#FDE503", scale: 1.08 }}, {w["s"]:.3f});')
        nxt = ch[k + 1]["s"] if k + 1 < len(ch) else e
        js.append(f'tl.set("#w{ci}_{k}", {{ color: "#ffffff", scale: 1 }}, {nxt:.3f});')
    srt.append(f"{ci + 1}\n{ts(s)} --> {ts(e)}\n{' '.join(w['w'] for w in ch)}\n")
keys = "".join(f"<i>{c}</i>" for c in "AZERTYUIOPQSDFGHJKLMWXCVBN1234")
out = open(os.path.join(HERE, "composition.tpl"), encoding="utf-8").read()
out = (out.replace("__DUR__", str(DUR)).replace("__D10__", f"{DUR - 29.5:.3f}")
          .replace("__SUBS__", "\n".join(subs)).replace("__SUBJS__", "\n".join(js)).replace("__KEYS__", keys))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
open(os.path.join(HERE, "missa-tv-360-pub.srt"), "w", encoding="utf-8").write("\n".join(srt))
print("index.html :", DUR, "s,", len(chunks), "sous-titres")
for c in chunks: print("  ", " ".join(w["w"] for w in c))
