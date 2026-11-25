"""STUDIO — le moteur unifié : éléments fournis → pub motion design de qualité (HyperFrames).

Entrées minimales : l'AUDIO de la pub (voix + musique mixées, ou voix seule) et le LOGO.
Tout le reste est optionnel : texte dit (script.txt ou transcription locale), détails,
images produit, vidéos, éléments graphiques (bibliothèque libre de droits ou fournis).

Pipeline :
  1. écoute (listen.py)     : phrases et mots horodatés, respirations, rythme ;
  2. marque (intake.py)     : palette déduite du logo (ou kit brands/<nom>.json) ;
  3. storyboard (ici)       : une scène par phrase dite (ou brief explicite de l'agent),
                              type déduit du contenu (prix, chiffre, liste, CTA…) ;
  4. composition (ici)      : index.html HyperFrames, une timeline GSAP déterministe,
                              scènes signature, caméra, transitions, fond vivant ;
  5. rendu (hyperframes CLI) puis vérification (verify.py).

Grammaire appliquée (lois mesurées, skill motionmaxxing) : on coupe en plein mouvement ;
la scène démarre déjà en mouvement ; presque rien ne fond (masques, arrivées depuis le
surdimensionné, glissés) ; les mots arrivent au rythme de la voix ; une seule chose
lumineuse par plan ; aucune image morte ; fin courte.
"""
from __future__ import annotations

import html
import json
import math
import os
import re
import shutil

from . import brand as brand_mod, intake, presets, probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO_DIR = os.path.join(REPO, "projects")
GSAP = os.path.join(REPO, "node_modules", "gsap", "dist", "gsap.min.js")

SCENE_TYPES = ["hook", "phrase", "logo", "product", "media", "benefits", "stat", "price", "cta"]
STYLES = {
    "energique": {"punch": 1.0, "cam": 0.07, "wipes": True, "speed": 1.0},
    "premium": {"punch": 0.55, "cam": 0.035, "wipes": False, "speed": 1.25},
    "doux": {"punch": 0.35, "cam": 0.03, "wipes": False, "speed": 1.4},
}

_NUM_WORDS = {
    "zéro": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
    "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12, "treize": 13,
    "quatorze": 14, "quinze": 15, "seize": 16, "vingt": 20, "trente": 30, "quarante": 40,
    "cinquante": 50, "soixante": 60, "cent": 100, "cents": 100, "mille": 1000,
    "million": 1_000_000, "millions": 1_000_000,
}
_CURRENCIES = {"€": "€", "euro": "€", "euros": "€", "$": "$", "dollar": "$", "dollars": "$",
               "f": "F", "fcfa": "F CFA", "franc": "F", "francs": "F", "cfa": "F CFA", "£": "£"}
_CTA_RE = re.compile(r"\b(télécharge|telecharge|abonne|inscri|commande|achète|achete|essaie|essaye|"
                     r"découvre|decouvre|rejoins|rejoignez|appelle|appelez|visite|clique|cliquez|"
                     r"profite|profitez|réserve|reserve|contacte|rendez-vous|maintenant)\w*", re.I)


def _fail(msg: str):
    raise SystemExit(f"ERREUR : {msg}")


# ── Analyse du texte dit ─────────────────────────────────────────────────────

def _words_to_number(tokens: list[str]) -> float | None:
    """« trois mille », « vingt-neuf », « 5 000 », « 29,90 » → nombre."""
    txt = " ".join(tokens).lower().replace("-", " ")
    m = re.search(r"\d[\d\s  .]*(?:,\d+)?", txt)
    if m:
        raw = m.group(0).replace(" ", "").replace(" ", "").replace(" ", "").replace(".", "")
        try:
            return float(raw.replace(",", "."))
        except ValueError:
            pass
    total, cur, seen = 0, 0, False
    for t in txt.split():
        t = t.strip(".,;:!?")
        if t == "et":
            continue
        if t not in _NUM_WORDS:
            if seen:
                break
            continue
        seen = True
        v = _NUM_WORDS[t]
        if v == 100:
            cur = max(cur, 1) * 100
        elif v >= 1000:
            total += max(cur, 1) * v
            cur = 0
        else:
            cur += v
    return float(total + cur) if seen else None


def _find_numbers(text: str) -> list[dict]:
    """Repère montants et chiffres clés : [{value, currency, prefix, label, span}]."""
    out = []
    t = text.replace("’", "'")
    pat = re.compile(
        r"(?P<plus>\+|plus de |plus d'|jusqu'à |seulement |que )?"
        r"(?P<num>\d+(?:[  .]\d{3})*(?:,\d+)?|(?:(?:zéro|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|"
        r"treize|quatorze|quinze|seize|vingt|trente|quarante|cinquante|soixante|cent|cents|mille|millions?)"
        r"(?:[\s-]+(?:et[\s-]+)?(?:un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|"
        r"quatorze|quinze|seize|vingt|trente|quarante|cinquante|soixante|cent|cents|mille|millions?))*))"
        r"\s*(?P<cur>€|\$|£|euros?|dollars?|francs?|fcfa|f cfa|cfa|f\b)?"
        r"(?P<label>(?:\s*(?:de |d')?[a-zàâçéèêëîïôûùüÿœ&'-]+){0,3})", re.I)
    for m in pat.finditer(t):
        val = _words_to_number([m.group("num")])
        if val is None or val == 1 and not m.group("cur"):
            continue
        cur = m.group("cur")
        label = (m.group("label") or "").strip()
        label = re.sub(r"^(de|d')\s*", "", label, flags=re.I)
        label = re.split(r"\s(?:et|au|ou|par|pour|avec|seulement|même|à)\b", " " + label, flags=re.I)[0].strip() \
            if label else ""
        out.append({"value": val, "currency": _CURRENCIES.get((cur or "").lower().strip(), cur),
                    "plus": bool(m.group("plus") and m.group("plus").strip().lower() in ("+", "plus de", "plus d'")),
                    "label": label, "span": m.span()})
    return out


def _fmt_num(v: float) -> str:
    if abs(v - round(v)) < 1e-6:
        return f"{int(round(v)):,}".replace(",", " ")
    return f"{v:,.2f}".replace(",", " ").replace(".", ",")


def _key_word(words: list[str]) -> int:
    """Indice du mot fort d'une phrase (chiffre, nom propre, mot le plus long)."""
    best, score = 0, -1
    stop = {"pour", "avec", "dans", "plus", "même", "tout", "tous", "vous", "votre", "nous", "notre",
            "mais", "sans", "chaque", "quand", "comme", "alors", "aussi", "cette", "était"}
    for i, w in enumerate(words):
        c = re.sub(r"[^\wÀ-ÿ€$+%]", "", w)
        s = len(c)
        if c.lower() in stop:
            s -= 4
        if re.search(r"\d", c):
            s += 6
        if i > 0 and c[:1].isupper():
            s += 3
        if s > score:
            best, score = i, s
    return best


# ── Storyboard ───────────────────────────────────────────────────────────────

def storyboard_from_voice(phrases: list[dict], duration: float, has_product: bool = False,
                          brand_name: str | None = None) -> list[dict]:
    """Une scène par phrase dite ; le type vient du contenu (prix, chiffre, appel à l'action)."""
    scenes: list[dict] = []
    n = len(phrases)
    for i, p in enumerate(phrases):
        text = p["text"].strip()
        nums = _find_numbers(text)
        money = [x for x in nums if x["currency"]]
        sc = {"start": p["start"], "text": text, "words": p.get("words") or []}
        if i == n - 1 and (n > 1):
            sc["type"] = "cta"
            m = _CTA_RE.search(text)
            sc["button"] = (m.group(0).capitalize() if m else "Découvrir") + (" maintenant" if m and m.group(0).lower() != "maintenant" and "maintenant" in text.lower() else "")
            sc["button"] = sc["button"].strip()
        elif money:
            sc["type"] = "price"
            sc["price"] = money[-1]["value"] if len(money) == 1 else min(x["value"] for x in money)
            sc["old_price"] = max(x["value"] for x in money) if len(money) > 1 else None
            sc["currency"] = money[0]["currency"]
            per = re.search(r"\b(par|/)\s*(an|mois|semaine|jour)\b", text, re.I)
            sc["label"] = f"/ {per.group(2)}" if per else ""
        elif nums and max(x["value"] for x in nums) >= 10:
            sc["type"] = "stat"
            sc["stats"] = [{"value": x["value"], "prefix": "+" if x["plus"] else "",
                            "label": x["label"]} for x in nums[:3]]
        elif i == 0:
            sc["type"] = "hook"
        elif re.search(r"\s:\s|,.*,", text) and len(re.split(r",|:| et ", text)) >= 3:
            sc["type"] = "benefits"
            chunks = text.split(":")
            body = max(chunks, key=lambda c: c.count(",") + c.count(" et "))
            parts = [s.strip(" .!?") for s in re.split(r",| et ", body) if len(s.strip(" .!?")) > 2]
            sc["items"] = [x[:1].upper() + x[1:] for x in parts[:4]]
        else:
            sc["type"] = "phrase"
        scenes.append(sc)
    if brand_name:
        for sc in scenes:
            if sc["type"] == "phrase" and brand_name.lower() in sc["text"].lower():
                sc["type"] = "logo"   # la phrase qui nomme la marque révèle le logo
                break
    if has_product:
        idx = next((k for k, s in enumerate(scenes) if s["type"] in ("phrase", "logo") and k > 0), None)
        if idx is not None and scenes[idx]["type"] == "phrase":
            scenes[idx]["type"] = "product"
    _time(scenes, duration)
    return scenes


def _time(scenes: list[dict], duration: float, lead: float = 0.08) -> None:
    """Coupe ~2 images AVANT le premier mot de chaque phrase ; la 1re scène démarre à 0."""
    for k, sc in enumerate(scenes):
        sc["start"] = 0.0 if k == 0 else max(0.0, float(sc["start"]) - lead)
    for k, sc in enumerate(scenes):
        end = scenes[k + 1]["start"] if k + 1 < len(scenes) else duration
        sc["duration"] = round(max(0.6, end - sc["start"]), 3)
        sc["start"] = round(sc["start"], 3)


def storyboard_from_brief(brief: dict, duration: float) -> list[dict]:
    """Brief « classique » (hook, product, benefits, proof, offer, cta) → storyboard minuté.

    Réutilise le minutage du compositeur ads.py (respirations de l'audio, temps de la musique)."""
    from . import ads, render as render_mod

    spec = dict(brief)
    spec.setdefault("template", "promo")
    proj = ads.compose(spec)
    starts, total = render_mod.scene_starts(proj, proj["scenes"])
    plan = proj["_ad"]["plan"]
    out = []
    for k, kind in enumerate(plan):
        base = kind.split(":")[0]
        sc: dict = {"start": starts[k]}
        if base == "hook":
            sc.update(type="hook", text=brief["hook"])
        elif base == "product":
            p = brief.get("product") or {}
            sc.update(type="product", text=p.get("name", ""), tagline=p.get("tagline", ""), image=p.get("image"))
        elif base == "media":
            m = (brief.get("media") or [])[int(kind.split(":")[1])]
            m = m if isinstance(m, dict) else {"file": m}
            sc.update(type="media", file=m["file"], text=m.get("caption", ""), media_start=m.get("start", 0))
        elif base == "benefits":
            sc.update(type="benefits", items=brief.get("benefits") or [])
        elif base == "proof":
            pr = brief.get("proof") or {}
            sc.update(type="stat", stats=[{"value": pr.get("value", 0), "prefix": pr.get("prefix", ""),
                                           "suffix": pr.get("suffix", ""), "label": pr.get("label", "")}])
        elif base == "offer":
            o = brief.get("offer") or {}
            sc.update(type="price", price=o.get("price"), old_price=o.get("old_price"),
                      currency=o.get("currency", "€"), label=o.get("label", ""), badge=o.get("badge"))
        elif base == "cta":
            sc.update(type="cta", button=brief.get("cta", "En savoir plus"), url=brief.get("url", ""))
        out.append(sc)
    _time(out, duration or total, lead=0.0)
    return out


# ── Composition HyperFrames ──────────────────────────────────────────────────

class Film:
    """Accumule HTML, CSS et timeline GSAP d'une composition."""

    def __init__(self, W: int, H: int, colors: dict, fonts: dict, style: str = "energique"):
        self.W, self.H = W, H
        self.u = min(W, H) / 100.0
        self.vertical = H > W * 1.1
        self.landscape = W > H * 1.1
        self.C = colors
        self.F = fonts
        self.S = STYLES.get(style, STYLES["energique"])
        self.html: list[str] = []
        self.css: list[str] = []
        self.js: list[str] = []
        self.n = 0
        self._seen: set[str] = set()

    def px(self, v: float) -> str:
        return f"{v * self.u:.1f}px"

    def add(self, method: str, sel: str, a: dict, b=None, t: float = 0.0):
        if isinstance(b, (int, float)):          # add("to", sel, vars, instant)
            b, t = None, float(b)
        if method == "fromTo" and b is not None:
            # un seul fromTo « pose » l'état initial ; les suivants ne doivent pas l'écraser
            if sel in self._seen:
                b = {**b, "immediateRender": False}
            self._seen.add(sel)
        args = [json.dumps(sel), json.dumps(a)]
        if b is not None:
            args.append(json.dumps(b))
        args.append(f"{max(0.0, t):.3f}")
        self.js.append(f"tl.{method}({', '.join(args)});")

    def uid(self, p: str = "e") -> str:
        self.n += 1
        return f"{p}{self.n}"


def _hexa(h: str, a: float) -> str:
    h = h.lstrip("#")[:6]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a:.3f})"


def _lum(h: str) -> float:
    h = h.lstrip("#")[:6]
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _on(bg: str) -> str:
    return "#0B0F1A" if _lum(bg) > 0.35 else "#FFFFFF"


def _esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _kinetic(f: Film, words: list[str], size: float, t: float, timings: list[float] | None = None,
             accent: int | None = None, align: str = "center", color: str | None = None,
             max_w: float = 88) -> str:
    """Texte cinétique : chaque mot monte dans son masque, au rythme de la voix."""
    color = color or f.C["text"]
    spans = []
    for i, w in enumerate(words):
        wid = f.uid("w")
        cls = "wi acc" if i == accent else "wi"
        spans.append(f'<span class="w"><span id="{wid}" class="{cls}">{_esc(w)}</span></span>')
        at = t + (timings[i] if timings and i < len(timings) else i * 0.07 * f.S["speed"])
        f.add("fromTo", f"#{wid}", {"yPercent": 115, "rotation": 4},
              {"yPercent": 0, "rotation": 0, "duration": 0.5 * f.S["speed"], "ease": "power4.out"}, at)
        if i == accent:
            f.add("fromTo", f"#{wid}", {"backgroundSize": "0% 100%"},
                  {"backgroundSize": "100% 100%", "duration": 0.35, "ease": "expo.out"}, at + 0.18)
    return (f'<div class="kin" style="font-size:{size * f.u:.0f}px;text-align:{align};color:{color};'
            f'max-width:{max_w * f.W / 100:.0f}px">{" ".join(spans)}</div>')


def _norm_w(w: str) -> str:
    return re.sub(r"[^\wÀ-ÿ]", "", w.lower().split("\u00a0")[0])


def _word_times(sc: dict, t0: float, limit: int, shown: list[str] | None = None) -> list[float] | None:
    """Décalages (s, relatifs à t0) des mots affichés : chacun arrive quand il est dit."""
    ws = sc.get("words") or []
    if not ws:
        return None
    if shown is None:
        shown = [w["w"] for w in ws[:limit]]
    out, j = [], 0
    for w in shown[:limit]:
        k = j
        while k < len(ws) and _norm_w(ws[k]["w"]) != _norm_w(w):
            k += 1
        if k < len(ws):
            j = k + 1
            out.append(max(0.0, float(ws[k]["start"]) - t0 - 0.05))
        else:
            out.append(out[-1] + 0.12 if out else 0.0)
    # rythme lisible : 2 à 12 images entre deux mots
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + 0.06)
    return out


def _condense(text: str, max_words: int = 7) -> list[str]:
    """Garde l'essentiel d'une phrase longue (on lit plus lentement qu'on n'écoute)."""
    words = text.replace("’", "'").split()
    if len(words) <= max_words:
        return words
    stop = {"le", "la", "les", "un", "une", "des", "de", "du", "et", "à", "au", "aux", "en", "pour",
            "que", "qui", "ne", "pas", "tu", "vous", "on", "est", "il", "elle", "ce", "ça", "même",
            "avec", "dans", "sur", "ta", "ton", "tes", "votre", "vos", "mon", "ma", "mes", "a", "y"}
    keep = [w for w in words if w.lower().strip(",.!?:;") not in stop]
    if len(keep) > max_words:
        keep = keep[:max_words]
    return keep or words[:max_words]


def _chunks(words: list[str], max_words: int = 4) -> list[list[str]]:
    """Découpe en groupes lisibles (≤ max_words), en coupant de préférence après la ponctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or (re.search(r"[,.;:!?…]$", w) and len(cur) >= 2):
            out.append(cur)
            cur = []
    if cur:
        if out and len(cur) == 1 and len(out[-1]) < max_words + 1:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def _spoken(f: Film, sc: dict, t0: float, D: float, size_max: float = 15.0, size_min: float = 8.0,
            color: str | None = None, max_words: int = 4) -> str:
    """Phrase entière, par groupes de mots qui se remplacent au rythme de la voix."""
    words = []
    for w in sc.get("text", "").replace("’", "'").split():
        if words and re.fullmatch(r"[?!:;.,…»]+", w):
            words[-1] += "\u00a0" + w          # « regarder ? » reste sur une ligne
        else:
            words.append(w)
    if not words:
        return ""
    groups = _chunks(words, max_words)
    times = _word_times(sc, sc["start"], len(words), words) or \
        [i * min(0.32, (D - 0.4) / max(1, len(words))) for i in range(len(words))]
    longest = max(sum(len(w) for w in g) + len(g) for g in groups)
    widest = max(len(w) for w in words)
    # viser ~2 lignes par groupe, sans qu'un mot seul dépasse la largeur utile
    size = min(205.0 / max(6, longest), 140.0 / max(4, widest)) * (1.0 if f.vertical else 0.75)
    size = max(size_min, min(size_max, size))
    if f.landscape:
        size = min(size, 10.5)
    blocks, idx = [], 0
    for gi, g in enumerate(groups):
        gt = times[idx: idx + len(g)]
        g_at = t0 + (gt[0] if gt else 0)
        rel = [x - gt[0] for x in gt]
        cid = f.uid("grp")
        body = _kinetic(f, g, size, g_at, rel, accent=_key_word(g) if len(g) > 1 else None, color=color)
        blocks.append(f'<div id="{cid}" class="grp">{body}</div>')
        if gi < len(groups) - 1:
            nxt = t0 + times[idx + len(g)] if idx + len(g) < len(times) else t0 + D
            last = t0 + (gt[-1] if gt else 0)
            f.add("to", f"#{cid} .wi", {"yPercent": -115, "duration": 0.2, "ease": "power3.in",
                                        "stagger": 0.015}, None, max(last + 0.28, nxt - 0.12))
        idx += len(g)
    return f'<div class="grps" style="min-height:{size * f.u * 2.6:.0f}px">{"".join(blocks)}</div>'


def _scene_hook(f: Film, sc: dict, t0: float, D: float, sid: str) -> str:
    body = _spoken(f, sc, t0 + 0.02, D, size_max=17.0, size_min=10.0, max_words=3)
    bar = f.uid("bar")
    f.add("fromTo", f"#{bar}", {"scaleX": 0}, {"scaleX": 1, "duration": 0.6, "ease": "expo.out"}, t0 + 0.1)
    return f'<div class="stack"><div id="{bar}" class="bar"></div>{body}</div>'


def _scene_phrase(f: Film, sc: dict, t0: float, D: float, sid: str, variant: int) -> str:
    words = _condense(sc.get("text", ""), 7)
    n = sum(len(w) for w in words) + len(words)
    times = _word_times(sc, sc["start"], len(words), words)
    k = _key_word(words)
    if variant % 3 == 1 and len(words) >= 3:
        # le mot fort en géant, le reste en petit au-dessus
        big = f.uid("big")
        small = _kinetic(f, words[:k] + ["…"] + words[k + 1:] if len(words) > 1 else words,
                         5.2, t0 + 0.02, times, align="center", color=f.C["muted"])
        size = min(26.0, 190.0 / max(4, len(words[k])))
        at = t0 + ((times[k] if times and k < len(times) else 0.15))
        f.add("fromTo", f"#{big}", {"scale": 2.6, "opacity": 0, "filter": "blur(18px)"},
              {"scale": 1, "opacity": 1, "filter": "blur(0px)", "duration": 0.55, "ease": "expo.out"}, at)
        return (f'<div class="stack">{small}<div id="{big}" class="giant" '
                f'style="font-size:{size * f.u:.0f}px">{_esc(words[k])}</div></div>')
    if variant % 3 == 2:
        # bandeau couleur d'accent qui balaie, texte posé dessus
        band = f.uid("band")
        size = min(12.0, max(6.5, 120.0 / max(10, n)))
        body = _kinetic(f, words, size, t0 + 0.12, times, accent=None, color=f.C["on_accent"])
        f.add("fromTo", f"#{band}", {"scaleX": 0, "transformOrigin": "0% 50%"},
              {"scaleX": 1, "duration": 0.45, "ease": "expo.out"}, t0)
        return f'<div class="stack"><div id="{band}" class="band">{body}</div></div>'
    return f'<div class="stack">{_spoken(f, sc, t0 + 0.02, D, size_max=15.0, size_min=9.0, max_words=3)}</div>'


def _logo_html(f: Film, logo: str | None, w: float, t: float, cls: str = "logo") -> str:
    if not logo:
        return ""
    lid = f.uid("logo")
    f.add("fromTo", f"#{lid}", {"scale": 3.2, "opacity": 0, "filter": "blur(24px)"},
          {"scale": 1, "opacity": 1, "filter": "blur(0px)", "duration": 0.62 * f.S["speed"],
           "ease": "expo.out"}, t)
    return (f'<img id="{lid}" class="{cls}" src="{_esc(logo)}" '
            f'style="max-width:{w * f.u:.0f}px;max-height:{w * 0.62 * f.u:.0f}px" alt="">')


def _burst(f: Film, t: float, n: int = 14, r: float = 34, color: str | None = None) -> str:
    """Éclats + anneaux qui jaillissent derrière un élément (positions déterministes)."""
    color = color or f.C["accent"]
    parts = []
    for i in range(2):
        rid = f.uid("ring")
        parts.append(f'<div id="{rid}" class="ring" style="border-color:{color}"></div>')
        f.add("fromTo", f"#{rid}", {"scale": 0.2, "opacity": 0.9},
              {"scale": 3.2 + i * 1.2, "opacity": 0, "duration": 0.9 + i * 0.25, "ease": "expo.out"},
              t + i * 0.08)
    for i in range(n):
        a = 2 * math.pi * i / n + (0.3 if i % 2 else 0)
        sid = f.uid("spark")
        dist = r * (1.0 if i % 2 else 1.35) * f.u
        parts.append(f'<div id="{sid}" class="spark" style="background:{color};'
                     f'transform:rotate({math.degrees(a) + 90:.1f}deg)"></div>')
        f.add("fromTo", f"#{sid}", {"x": 0, "y": 0, "scaleY": 0.2, "opacity": 1},
              {"x": round(math.cos(a) * dist), "y": round(math.sin(a) * dist), "scaleY": 1, "opacity": 0,
               "duration": 0.7, "ease": "power3.out"}, t + 0.05)
    return f'<div class="burst">{"".join(parts)}</div>'


def _scene_logo(f: Film, sc: dict, t0: float, D: float, sid: str, logo: str | None) -> str:
    words = _condense(sc.get("text", ""), 6)
    times = _word_times(sc, sc["start"], len(words), words)
    tl = t0 + 0.12
    return (f'<div class="stack"><div class="hero">{_burst(f, tl + 0.18)}'
            f'{_logo_html(f, logo, 72 if f.vertical else 44, tl)}</div>'
            f'{_spoken(f, sc, t0 + 0.3, D, size_max=10.0, size_min=7.0, max_words=4)}</div>')


def _scene_product(f: Film, sc: dict, t0: float, D: float, sid: str, image: str | None,
                   logo: str | None) -> str:
    img = image or logo
    pid, shine, shadow = f.uid("prod"), f.uid("shine"), f.uid("shadow")
    f.add("fromTo", f"#{pid}", {"rotationY": -32, "rotationX": 8, "x": f.u * 18, "scale": 1.25,
                                 "transformPerspective": 1400, "opacity": 0},
          {"rotationY": 0, "rotationX": 0, "x": 0, "scale": 1, "opacity": 1, "duration": 0.9,
           "ease": "expo.out"}, t0)
    f.add("to", f"#{pid}", {"y": -f.u * 2.2, "rotationY": 6, "duration": max(0.5, D - 0.9),
                            "ease": "sine.inOut"}, t0 + 0.9)
    f.add("fromTo", f"#{shine}", {"xPercent": -160}, {"xPercent": 160, "duration": 0.9,
                                                       "ease": "power2.inOut"}, t0 + 0.45)
    f.add("fromTo", f"#{shadow}", {"scaleX": 0.3, "opacity": 0}, {"scaleX": 1, "opacity": 0.55,
                                                                  "duration": 0.8, "ease": "expo.out"}, t0)
    words = _condense(sc.get("text", ""), 6)
    times = _word_times(sc, sc["start"], len(words), words)
    side = "row" if f.landscape else "stack"
    size = 68 if f.vertical else 44
    tag = ""
    if sc.get("tagline"):
        tag = _kinetic(f, sc["tagline"].split(), 4.2, t0 + 0.6, None, color=f.C["muted"])
    return (f'<div class="{side}"><div class="prodwrap" style="width:{size * f.u:.0f}px">'
            f'<div id="{pid}" class="prod"><img src="{_esc(img)}" alt="">'
            f'<div class="shinebox"><div id="{shine}" class="shine"></div></div></div>'
            f'<div id="{shadow}" class="shadow"></div></div>'
            f'<div class="stack tight">{_kinetic(f, words, 7.0, t0 + 0.3, times, accent=_key_word(words))}'
            f'{tag}</div></div>')


def _scene_benefits(f: Film, sc: dict, t0: float, D: float, sid: str, icons: list[str | None]) -> str:
    items = [str(x.get("text") if isinstance(x, dict) else x) for x in (sc.get("items") or [])][:4]
    rows = []
    step = min(0.55, max(0.25, (D - 0.8) / max(1, len(items))))
    for i, it in enumerate(items):
        rid, cid = f.uid("row"), f.uid("chk")
        at = t0 + 0.08 + i * step
        f.add("fromTo", f"#{rid}", {"x": f.W * 0.6, "skewX": -12},
              {"x": 0, "skewX": 0, "duration": 0.55, "ease": "expo.out"}, at)
        ic = icons[i] if i < len(icons) else None
        if ic:
            mark = f'<img id="{cid}" class="ic3d" src="{_esc(ic)}" alt="">'
            f.add("fromTo", f"#{cid}", {"scale": 2.4, "rotation": -25},
                  {"scale": 1, "rotation": 0, "duration": 0.5, "ease": "expo.out"}, at + 0.1)
        else:
            mark = (f'<svg class="chk" viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="{f.C["accent"]}"/>'
                    f'<path id="{cid}" d="M13 25 L21 33 L36 16" fill="none" stroke="{f.C["on_accent"]}" '
                    f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round" '
                    f'stroke-dasharray="40" stroke-dashoffset="40"/></svg>')
            f.add("to", f"#{cid}", {"strokeDashoffset": 0, "duration": 0.35, "ease": "power2.out"}, at + 0.22)
        rows.append(f'<div id="{rid}" class="item">{mark}<span>{_esc(it)}</span></div>')
    return f'<div class="list">{"".join(rows)}</div>'


def _scene_stat(f: Film, sc: dict, t0: float, D: float, sid: str) -> str:
    stats = (sc.get("stats") or [])[:2]
    blocks = []
    for i, s in enumerate(stats):
        nid, lid, ring = f.uid("num"), f.uid("lab"), f.uid("ringp")
        val = float(s.get("value", 0))
        at = t0 + 0.05 + i * 0.5
        dec = 0 if abs(val - round(val)) < 1e-6 else 1
        pre, suf = _esc(s.get("prefix", "")), _esc(s.get("suffix", ""))
        f.js.append(f"(function(){{var o={{v:0}};var el=document.getElementById('{nid}');"
                    f"tl.to(o,{{v:{val},duration:{1.1 * f.S['speed']:.2f},ease:'expo.out',onUpdate:function(){{"
                    f"el.textContent='{pre}'+fmt(o.v,{dec})+'{suf}';}}}},{at:.3f});}})();")
        f.add("fromTo", f"#{nid}", {"scale": 1.9}, {"scale": 1, "duration": 0.7, "ease": "expo.out"}, at)
        f.add("to", f"#{ring}", {"strokeDashoffset": 0, "duration": 1.1, "ease": "expo.out"}, at)
        size = 19 if len(stats) == 1 else 13
        lab = _kinetic(f, str(s.get("label", "")).split(), 5.0, at + 0.35, None, color=f.C["muted"])
        r = 46
        blocks.append(
            f'<div class="statb"><svg class="ringsvg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="{r}" '
            f'fill="none" stroke="{_hexa(f.C["text"], 0.12)}" stroke-width="2.4"/><circle id="{ring}" cx="50" '
            f'cy="50" r="{r}" fill="none" stroke="{f.C["accent"]}" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-dasharray="{2 * math.pi * r:.1f}" stroke-dashoffset="{2 * math.pi * r:.1f}" '
            f'transform="rotate(-90 50 50)"/></svg>'
            f'<div id="{nid}" class="num" style="font-size:{size * f.u:.0f}px">{pre}0{suf}</div>'
            f'<div id="{lid}">{lab}</div></div>')
    cls = "row" if f.landscape and len(blocks) > 1 else "stack"
    return f'<div class="{cls}">{"".join(blocks)}</div>'


def _scene_price(f: Film, sc: dict, t0: float, D: float, sid: str) -> str:
    cur = sc.get("currency") or "€"

    def money(v):
        s = _fmt_num(float(v))
        return f"{cur}{s}" if cur in ("$", "£") else f"{s} {cur}"
    parts = []
    old = sc.get("old_price")
    if old:
        oid, strike = f.uid("old"), f.uid("strike")
        f.add("fromTo", f"#{oid}", {"yPercent": 120}, {"yPercent": 0, "duration": 0.45, "ease": "expo.out"}, t0 + 0.02)
        f.add("fromTo", f"#{strike}", {"scaleX": 0}, {"scaleX": 1, "duration": 0.3, "ease": "power3.inOut"}, t0 + 0.45)
        f.add("to", f"#{oid}", {"y": f.u * 3, "opacity": 0.45, "scale": 0.8, "duration": 0.5, "ease": "power3.in"}, t0 + 0.8)
        parts.append(f'<div class="w"><div id="{oid}" class="old">{_esc(money(old))}'
                     f'<div id="{strike}" class="strike"></div></div></div>')
    pid = f.uid("price")
    at = t0 + (0.95 if old else 0.1)
    f.add("fromTo", f"#{pid}", {"scale": 3.4, "opacity": 0, "filter": "blur(20px)"},
          {"scale": 1, "opacity": 1, "filter": "blur(0px)", "duration": 0.5, "ease": "expo.out"}, at)
    # impact : la scène tremble 0,25 s (déterministe)
    for k, (dx, dy) in enumerate([(14, -8), (-11, 6), (7, -4), (-3, 2), (0, 0)]):
        f.add("to", f"#{sid} .cam", {"x": dx * f.S["punch"], "y": dy * f.S["punch"], "duration": 0.05,
                                      "ease": "none"}, at + 0.38 + k * 0.05)
    size = 24 if f.vertical else 19
    parts.append(f'<div id="{pid}" class="price" style="font-size:{size * f.u:.0f}px">{_esc(money(sc.get("price", 0)))}</div>')
    if sc.get("label"):
        parts.append(_kinetic(f, str(sc["label"]).split(), 5.4, at + 0.4, None, color=f.C["on_accent"]))
    if sc.get("badge"):
        bid = f.uid("badge")
        f.add("fromTo", f"#{bid}", {"scale": 3, "rotation": -40, "opacity": 0},
              {"scale": 1, "rotation": -10, "opacity": 1, "duration": 0.45, "ease": "expo.out"}, at + 0.5)
        parts.append(f'<div id="{bid}" class="badge">{_esc(sc["badge"])}</div>')
    return f'<div class="stack onacc">{"".join(parts)}</div>'


def _scene_cta(f: Film, sc: dict, t0: float, D: float, sid: str, logo: str | None) -> str:
    bid, shine, arrow = f.uid("btn"), f.uid("bshine"), f.uid("arrow")
    lg = _logo_html(f, logo, 70 if f.vertical else 42, t0 + 0.02)
    at = t0 + 0.35
    f.add("fromTo", f"#{bid}", {"scale": 0.4, "opacity": 0},
          {"scale": 1, "opacity": 1, "duration": 0.6, "ease": "back.out(2.2)"}, at)
    for k in range(3):
        f.add("fromTo", f"#{shine}", {"xPercent": -180}, {"xPercent": 260, "duration": 0.7,
                                                          "ease": "power2.inOut"}, at + 0.6 + k * 1.3)
        f.add("fromTo", f"#{arrow}", {"x": 0}, {"x": f.u * 1.6, "duration": 0.25, "yoyo": True, "repeat": 1,
                                               "ease": "power2.inOut"}, at + 0.9 + k * 1.3)
    url = ""
    if sc.get("url"):
        url = _kinetic(f, [sc["url"]], 4.2, at + 0.35, None, color=f.C["muted"])
    raw = sc.get("button") or "En savoir plus"
    label = _esc(raw)
    fs = min(7.0 if f.vertical else 5.2, 118.0 / max(8, len(raw)))
    return (f'<div class="stack">{lg}<div id="{bid}" class="btn" style="font-size:{fs * f.u:.0f}px"><span>{label}</span>'
            f'<span id="{arrow}" class="arr">→</span><div class="bshinebox"><div id="{shine}" class="bshine">'
            f'</div></div></div>{url}</div>')


def _media_root(f: Film, sc: dict, t0: float, D: float, path: str, idx: int) -> str:
    """Média plein cadre posé à la racine (règle HyperFrames : pas de data-start imbriqué)."""
    mid = f.uid("media")
    ext = os.path.splitext(path)[1].lower()
    f.add("fromTo", f"#{mid}", {"scale": 1.18, "xPercent": -3 if idx % 2 else 3},
          {"scale": 1.02, "xPercent": 0, "duration": D, "ease": "none"}, t0)
    if ext in (".mp4", ".mov", ".webm", ".m4v"):
        ms = float(sc.get("media_start", 0) or 0)
        extra = f' data-media-start="{ms:.2f}"' if ms else ""
        return (f'<video id="{mid}" class="clip bgmedia" src="{_esc(path)}" muted playsinline '
                f'data-start="{t0:.3f}" data-duration="{D:.3f}" data-track-index="0"{extra}></video>')
    return (f'<img id="{mid}" class="clip bgmedia" src="{_esc(path)}" alt="" '
            f'data-start="{t0:.3f}" data-duration="{D:.3f}" data-track-index="0">')


def _scene_media(f: Film, sc: dict, t0: float, D: float, sid: str) -> str:
    words = _condense(sc.get("text", ""), 7)
    if not words:
        return '<div class="stack"></div>'
    times = _word_times(sc, sc["start"], len(words), words) if sc.get("words") else None
    return (f'<div class="stack bottom"><div class="shade"></div>'
            f'{_kinetic(f, words, 7.2, t0 + 0.15, times, accent=_key_word(words))}</div>')


def _decor(f: Film, items: list[str], t0: float, D: float) -> str:
    """Éléments 3D (emojis Fluent, objets) qui flottent aux bords, en parallaxe."""
    spots = [(12, 16, -14), (86, 22, 12), (14, 84, 10), (84, 80, -10)]
    out = []
    for i, src in enumerate(items[:4]):
        x, y, rot = spots[i]
        did = f.uid("deco")
        size = (16 if f.vertical else 12)
        out.append(f'<img id="{did}" class="deco" src="{_esc(src)}" alt="" style="left:{x}%;top:{y}%;'
                   f'width:{size * f.u:.0f}px">')
        f.add("fromTo", f"#{did}", {"scale": 2.6, "opacity": 0, "rotation": rot * 3},
              {"scale": 1, "opacity": 1, "rotation": rot, "duration": 0.6, "ease": "expo.out"}, t0 + 0.15 + i * 0.09)
        f.add("to", f"#{did}", {"y": -f.u * (3 + i), "rotation": rot + (6 if i % 2 else -6),
                                "duration": max(0.4, D - 0.8), "ease": "sine.inOut"}, t0 + 0.75)
    return "".join(out)


# ── Assemblage ───────────────────────────────────────────────────────────────

def _font_face(name: str, file: str) -> str:
    return f'@font-face {{ font-family: "{name}"; src: url("assets/fonts/{file}"); font-display: block; }}'


def compose(storyboard: list[dict], *, canvas: str, colors: dict, fonts: dict, duration: float,
            audio: list[dict] | None = None, logo: str | None = None, product: str | None = None,
            icons: dict | None = None, decor: list[str] | None = None, style: str = "energique",
            subtitles: bool = False, title: str = "Pub") -> str:
    cv = presets.canvas(canvas)
    W, H = int(cv["width"]), int(cv["height"])
    f = Film(W, H, colors, fonts, style)
    C, u = colors, f.u
    scenes_html, root_media = [], []
    cut_times = []
    phrase_variant = 0
    for k, sc in enumerate(storyboard):
        t0, D = float(sc["start"]), float(sc["duration"])
        sid = f"sc{k}"
        typ = sc.get("type", "phrase")
        ground = ""
        if typ == "hook":
            inner = _scene_hook(f, sc, t0, D, sid)
        elif typ == "logo":
            inner = _scene_logo(f, sc, t0, D, sid, logo)
        elif typ == "product":
            inner = _scene_product(f, sc, t0, D, sid, sc.get("image") or product, logo)
        elif typ == "benefits":
            inner = _scene_benefits(f, sc, t0, D, sid, (icons or {}).get(k, []))
        elif typ == "stat":
            inner = _scene_stat(f, sc, t0, D, sid)
            ground = "surface"
        elif typ == "price":
            inner = _scene_price(f, sc, t0, D, sid)
            ground = "accent"
        elif typ == "cta":
            inner = _scene_cta(f, sc, t0, D, sid, logo)
        elif typ == "media" and sc.get("file"):
            root_media.append(_media_root(f, sc, t0, D, sc["file"], k))
            inner = _scene_media(f, sc, t0, D, sid)
            ground = "none"
        else:
            inner = _scene_phrase(f, sc, t0, D, sid, phrase_variant)
            phrase_variant += 1
        deco = _decor(f, decor or [], t0, D) if decor and typ in ("hook", "cta") else ""
        # caméra : la scène démarre déjà en mouvement (punch-in) puis dérive
        cam = f.S["cam"]
        moves = [{"scale": 1 + cam}, {"x": -u * 3, "scale": 1 + cam * 0.6}, {"y": -u * 2.5, "scale": 1 + cam * 0.7},
                 {"x": u * 3, "scale": 1 + cam * 0.6}, {"rotation": 0.8, "scale": 1 + cam}]
        f.add("fromTo", f"#{sid} .cam", {"scale": 1 + 0.12 * f.S["punch"], "x": 0, "y": 0, "rotation": 0},
              {"scale": 1, "duration": 0.55, "ease": "expo.out"}, t0)
        f.add("to", f"#{sid} .cam", {**moves[k % len(moves)], "duration": max(0.3, D - 0.55), "ease": "none"},
              t0 + 0.55)
        if k:
            cut_times.append(t0)
        gstyle = {"accent": f"background:{C['accent']}", "surface": f"background:{C['surface']}",
                  "none": "background:transparent"}.get(ground, "")
        pattern = ""
        if ground in ("accent", "surface"):
            # fond plein : un motif qui défile pour qu'aucune image ne soit morte
            pid = f.uid("pat")
            pattern = f'<div id="{pid}" class="pattern"></div>'
            f.add("fromTo", f"#{pid}", {"backgroundPosition": "0px 0px"},
                  {"backgroundPosition": f"{18 * u * D:.0f}px {6 * u * D:.0f}px", "duration": D, "ease": "none"}, t0)
        scenes_html.append(
            f'<div id="{sid}" class="scene clip t-{typ}" data-start="{t0:.3f}" data-duration="{D:.3f}" '
            f'data-track-index="1" style="{gstyle}">{pattern}<div class="cam">{inner}</div>{deco}</div>')

    # transitions : volets de couleur sur les coupes fortes (offre, CTA, logo), punch ailleurs
    wipes = []
    if f.S["wipes"]:
        for k, sc in enumerate(storyboard[1:], start=1):
            if sc.get("type") in ("price", "cta", "logo", "stat"):
                wid = f.uid("wipe")
                t = float(sc["start"])
                col = C["accent"] if sc.get("type") != "price" else C["text"]
                wipes.append(f'<div id="{wid}" class="wipe" style="background:{col}"></div>')
                d = 1 if k % 2 else -1
                f.add("fromTo", f"#{wid}", {"xPercent": -105 * d, "skewX": -14 * d},
                      {"xPercent": 0, "skewX": 0, "duration": 0.2, "ease": "power3.in"}, t - 0.2)
                f.add("to", f"#{wid}", {"xPercent": 105 * d, "skewX": 14 * d, "duration": 0.26,
                                        "ease": "power3.out"}, t)

    # fond vivant : halos de couleur qui dérivent sur tout le film
    blobs = []
    for i, (col, x0, y0) in enumerate([(C["accent"], 20, 18), (C.get("secondary", C["accent"]), 80, 70),
                                       (C["accent"], 60, 95)]):
        bid = f"blob{i}"
        blobs.append(f'<div id="{bid}" class="blob" style="left:{x0}%;top:{y0}%;'
                     f'background:radial-gradient(circle, {_hexa(col, 0.55)} 0%, {_hexa(col, 0.18)} 38%, '
                     f'{_hexa(col, 0)} 70%)"></div>')
        legs = max(1, int(duration // 3.2))
        seg = duration / legs
        for L in range(legs):
            ang = (i * 2.1 + L * 1.7)
            f.add("to", f"#{bid}", {"x": round(math.cos(ang) * u * 26), "y": round(math.sin(ang) * u * 22),
                                    "scale": 1 + 0.25 * math.sin(ang * 1.3), "duration": seg, "ease": "sine.inOut"},
                  L * seg)

    # sous-titres synchronisés (option)
    subs = []
    if subtitles:
        for k, sc in enumerate(storyboard):
            # le texte déjà animé à l'écran n'est pas doublé
            if sc.get("type") in ("price", "stat", "hook", "phrase", "media") or not sc.get("text"):
                continue
            s_id = f.uid("sub")
            st = float(sc["start"])
            subs.append(f'<div id="{s_id}" class="sub clip" data-start="{st:.3f}" '
                        f'data-duration="{float(sc["duration"]):.3f}" data-track-index="3">'
                        f'<span>{_esc(sc["text"])}</span></div>')

    audio_html = []
    for i, a in enumerate(audio or []):
        audio_html.append(f'<audio id="snd{i}" src="{_esc(a["src"])}" data-start="{a.get("at", 0):.3f}" '
                          f'data-duration="{duration:.3f}" data-track-index="{6 + i}" '
                          f'data-volume="{a.get("volume", 1.0)}"></audio>')

    tfont, bfont = fonts.get("title"), fonts.get("body") or fonts.get("title")
    css = f"""
{_font_face("MDTitle", tfont)}
{_font_face("MDBody", bfont)}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:{C['background']}; }}
#root {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; font-family:"MDBody", sans-serif;
  background: radial-gradient(120% 90% at 50% 0%, {C['surface']} 0%, {C['background']} 70%); }}
.blob {{ position:absolute; width:{110 * u:.0f}px; height:{110 * u:.0f}px; margin:-{55 * u:.0f}px 0 0 -{55 * u:.0f}px;
  border-radius:50%; pointer-events:none; }}
.grain {{ position:absolute; inset:-50%; opacity:.07; pointer-events:none; z-index:40;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>"); }}
.bgmedia {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:1; }}
.scene {{ position:absolute; inset:0; z-index:5; overflow:hidden; }}
.cam {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  padding:{(14 if f.vertical else 7) * H / 100:.0f}px {8 * W / 100:.0f}px {(20 if f.vertical else 8) * H / 100:.0f}px; }}
.stack {{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:{3 * u:.0f}px; width:100%; }}
.stack.tight {{ gap:{1.4 * u:.0f}px; }}
.stack.bottom {{ justify-content:flex-end; height:100%; }}
.row {{ display:flex; flex-direction:row; align-items:center; justify-content:center; gap:{6 * u:.0f}px; width:100%; }}
.row .stack {{ align-items:flex-start; width:auto; flex:1; }}
.row .stack .kin {{ text-align:left !important; }}
.kin {{ font-family:"MDTitle", sans-serif; line-height:1.02; letter-spacing:-0.02em; }}
.grps {{ position:relative; width:100%; display:grid; place-items:center; }}
.grp {{ grid-area:1 / 1; width:100%; display:flex; justify-content:center; }}
.w {{ display:inline-block; overflow:hidden; vertical-align:top; padding:0.04em 0.06em 0.1em; margin:0 -0.02em; }}
.wi {{ display:inline-block; will-change:transform; }}
.wi.acc {{ color:{C['on_accent']}; padding:0 0.12em; border-radius:0.12em;
  background-image:linear-gradient({C['accent']},{C['accent']}); background-repeat:no-repeat; background-size:0% 100%; }}
.bar {{ width:{14 * u:.0f}px; height:{1.1 * u:.0f}px; background:{C['accent']}; border-radius:{u:.0f}px; transform-origin:0 50%; }}
.giant {{ font-family:"MDTitle", sans-serif; color:{C['accent']}; line-height:.95; letter-spacing:-0.04em; }}
.band {{ background:{C['accent']}; padding:{3 * u:.0f}px {4 * u:.0f}px; border-radius:{1.2 * u:.0f}px; }}
.hero {{ position:relative; display:flex; align-items:center; justify-content:center; }}
.logo {{ position:relative; z-index:2; object-fit:contain; }}
.burst {{ position:absolute; left:50%; top:50%; width:0; height:0; z-index:1; }}
.ring {{ position:absolute; width:{30 * u:.0f}px; height:{30 * u:.0f}px; margin:-{15 * u:.0f}px 0 0 -{15 * u:.0f}px;
  border:{0.8 * u:.1f}px solid; border-radius:50%; }}
.spark {{ position:absolute; width:{0.9 * u:.1f}px; height:{5 * u:.0f}px; margin:-{2.5 * u:.1f}px 0 0 -{0.45 * u:.1f}px; border-radius:{u:.0f}px; }}
.prodwrap {{ position:relative; display:flex; flex-direction:column; align-items:center; }}
.prod {{ position:relative; overflow:hidden; border-radius:{2 * u:.0f}px; }}
.prod img {{ display:block; width:100%; height:auto; max-height:{(46 if f.vertical else 62) * H / 100:.0f}px; object-fit:contain; }}
.shinebox {{ position:absolute; inset:0; overflow:hidden; mix-blend-mode:screen; pointer-events:none; }}
.shine {{ position:absolute; top:-20%; left:30%; width:35%; height:140%; transform:skewX(-18deg);
  background:linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.55), rgba(255,255,255,0)); }}
.shadow {{ width:70%; height:{3 * u:.0f}px; margin-top:{2 * u:.0f}px; border-radius:50%;
  background:radial-gradient(closest-side, rgba(0,0,0,.65), rgba(0,0,0,0)); }}
.list {{ display:flex; flex-direction:column; gap:{2.6 * u:.0f}px; width:100%; max-width:{(86 if f.vertical else 60) * W / 100:.0f}px; }}
.item {{ display:flex; align-items:center; gap:{3 * u:.0f}px; padding:{2.6 * u:.0f}px {3.4 * u:.0f}px;
  border-radius:{2.4 * u:.0f}px; background:{_hexa(C['text'], 0.07)}; border:1px solid {_hexa(C['text'], 0.14)};
  font-family:"MDTitle", sans-serif; font-size:{5.4 * u:.0f}px; color:{C['text']}; }}
.chk, .ic3d {{ width:{8 * u:.0f}px; height:{8 * u:.0f}px; flex:none; object-fit:contain; }}
.statb {{ position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center;
  width:{(70 if f.vertical else 46) * u:.0f}px; height:{(70 if f.vertical else 46) * u:.0f}px; }}
.ringsvg {{ position:absolute; inset:0; width:100%; height:100%; }}
.num {{ font-family:"MDTitle", sans-serif; color:{C['text']}; letter-spacing:-0.03em; line-height:1; }}
.onacc .kin {{ color:{C['on_accent']}; }}
.old {{ position:relative; font-family:"MDTitle", sans-serif; font-size:{9 * u:.0f}px; color:{_on(C['accent'])}; opacity:.85; }}
.strike {{ position:absolute; left:-6%; right:-6%; top:52%; height:{1.2 * u:.1f}px; background:{_on(C['accent'])};
  transform:rotate(-8deg); transform-origin:0 50%; }}
.price {{ font-family:"MDTitle", sans-serif; color:{_on(C['accent'])}; line-height:1; letter-spacing:-0.04em; }}
.badge {{ font-family:"MDTitle", sans-serif; font-size:{6 * u:.0f}px; color:{C['accent']}; background:{_on(C['accent'])};
  padding:{1.4 * u:.0f}px {3 * u:.0f}px; border-radius:{6 * u:.0f}px; }}
.btn {{ position:relative; overflow:hidden; display:flex; align-items:center; gap:{2.4 * u:.0f}px;
  font-family:"MDTitle", sans-serif; font-size:{(6.4 if f.vertical else 5) * u:.0f}px; color:{C['on_accent']}; white-space:nowrap;
  background:{C['accent']}; padding:{2.8 * u:.0f}px {6.5 * u:.0f}px; border-radius:{10 * u:.0f}px;
  box-shadow:0 {2 * u:.0f}px {6 * u:.0f}px {_hexa(C['accent'], 0.45)}; }}
.arr {{ display:inline-block; }}
.bshinebox {{ position:absolute; inset:0; overflow:hidden; pointer-events:none; }}
.bshine {{ position:absolute; top:-30%; left:0; width:30%; height:160%; transform:skewX(-20deg);
  background:linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.6), rgba(255,255,255,0)); }}
.deco {{ position:absolute; margin:-{8 * u:.0f}px 0 0 -{8 * u:.0f}px; z-index:6;
  filter:drop-shadow(0 {1.5 * u:.0f}px {3 * u:.0f}px rgba(0,0,0,.45)); }}
.shade {{ position:absolute; left:0; right:0; bottom:0; height:55%;
  background:linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.78)); z-index:0; }}
.stack.bottom .kin {{ position:relative; z-index:1; }}
.wipe {{ position:absolute; inset:-5% -15%; z-index:30; }}
.pattern {{ position:absolute; inset:0; opacity:.16;
  background-image:repeating-linear-gradient(135deg, {_hexa(_on(C['accent']), 0.55)} 0 {1.2 * u:.0f}px, transparent {1.2 * u:.0f}px {7 * u:.0f}px); }}
.sub {{ position:absolute; left:6%; right:6%; bottom:{(17 if f.vertical else 7) * H / 100:.0f}px; z-index:35; text-align:center; }}
.sub span {{ display:inline; font-family:"MDBody", sans-serif; font-size:{(3.6 if f.vertical else 2.8) * u:.0f}px;
  color:#fff; background:rgba(0,0,0,.62); padding:.15em .45em; line-height:1.5;
  -webkit-box-decoration-break:clone; box-decoration-break:clone; border-radius:.25em; }}
"""
    js = "\n".join(f.js)
    doc = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width={W}, height={H}">
<title>{_esc(title)}</title>
<script src="vendor/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{duration:.3f}" data-width="{W}" data-height="{H}">
{''.join(blobs)}
{''.join(root_media)}
{''.join(scenes_html)}
{''.join(subs)}
{''.join(wipes)}
<div class="grain"></div>
{''.join(audio_html)}
</div>
<script>
function fmt(v, d) {{
  var s = (d ? v.toFixed(d) : Math.round(v).toString());
  var p = s.split('.'); p[0] = p[0].replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, '\\u202f');
  return p.join(',');
}}
const tl = gsap.timeline({{ paused: true }});
{js}
tl.set({{}}, {{}}, {duration:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    return doc


# ── Projet complet ───────────────────────────────────────────────────────────

def _copy(src: str, dest_dir: str, name: str | None = None) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    name = name or re.sub(r"[^\w.-]+", "-", os.path.basename(src)).strip("-")
    dst = os.path.join(dest_dir, name)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copyfile(src, dst)
    return name


def _resolve(p: str | None) -> str | None:
    if not p:
        return None
    from . import render as render_mod
    return render_mod.resolve_path(p, os.getcwd())


def _font_file(name: str) -> str:
    from . import text
    return text.find_font(name, REPO)


def _auto_icons(items: list, limit: int = 4) -> list[str | None]:
    """Cherche une icône 3D libre de droits pour chaque bénéfice (bibliothèque Fluent)."""
    from . import elements
    out = []
    for it in items[:limit]:
        if isinstance(it, dict) and it.get("icon"):
            out.append(it["icon"])
            continue
        txt = it.get("text") if isinstance(it, dict) else str(it)
        try:
            res = elements.search(txt, style="3d", limit=1)
            hits = res.get("results") or res.get("resultats") or []
            out.append(hits[0]["id"] if hits else None)
        except Exception:  # noqa: BLE001 (réseau absent : coche dessinée)
            out.append(None)
    return out


def _fetch_elements(ids: list[str], dest: str) -> dict[str, str]:
    """ids « source:nom » (bibliothèque) ou chemins de fichiers → fichiers copiés dans le projet."""
    from . import elements
    got: dict[str, str] = {}
    for ident in ids:
        if not ident:
            continue
        if os.path.isfile(ident) or (not ":" in ident and _resolve_quiet(ident)):
            p = ident if os.path.isfile(ident) else _resolve_quiet(ident)
            got[ident] = "assets/elements/" + _copy(p, dest)
            continue
        try:
            res = elements.get([ident], dest=dest, png=True, size=512)
            files = [os.path.basename(x) for x in res.get("recuperes", [])]
            pick = next((n for n in files if n.endswith(".png")), files[0] if files else None)
            if pick:
                got[ident] = "assets/elements/" + pick
        except Exception:  # noqa: BLE001
            pass
    return got


def _resolve_quiet(p: str) -> str | None:
    try:
        return _resolve(p)
    except SystemExit:
        return None


def build(brief: dict, canvas: str | None = None, name: str | None = None) -> dict:
    """Brief (ou simples éléments fournis) → projet HyperFrames prêt à rendre.

    Champs : audio (obligatoire sauf duration), logo, script, brand, style, subtitles,
    scenes (storyboard explicite de l'agent), hook/product/benefits/proof/offer/cta/url/media
    (brief classique), music, voiceover, decor (éléments), auto_elements (défaut true).
    """
    canvas = canvas or brief.get("canvas", "9x16")
    if canvas not in presets.CANVAS_PRESETS:
        _fail(f"canvas '{canvas}' inconnu ({', '.join(presets.CANVAS_PRESETS)})")
    style = brief.get("style", "energique") if isinstance(brief.get("style"), str) else "energique"
    if style not in STYLES:
        _fail(f"style '{style}' inconnu ({', '.join(STYLES)})")
    name = name or brief.get("name") or "pub"
    name = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-") or "pub"
    pdir = os.path.join(STUDIO_DIR, f"{name}-{canvas}")
    adir = os.path.join(pdir, "assets")
    os.makedirs(os.path.join(adir, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(pdir, "vendor"), exist_ok=True)
    if not os.path.isfile(GSAP):
        _fail("GSAP absent : lancer `npm ci` (ou make bootstrap) à la racine du dépôt")
    shutil.copyfile(GSAP, os.path.join(pdir, "vendor", "gsap.min.js"))

    # ── Audio ──
    master = _resolve(brief.get("audio") or brief.get("audio_master"))
    voice = _resolve(brief.get("voiceover"))
    music = _resolve(brief.get("music"))
    speech = master or voice
    duration = float(brief.get("duration") or 0)
    if speech:
        duration = duration or float(probe.probe(speech).get("duration") or 0)
    elif music and not duration:
        duration = float(probe.probe(music).get("duration") or 15)
    duration = duration or 15.0
    sounds = []
    if master:
        sounds.append({"src": "assets/" + _copy(master, adir, "audio" + os.path.splitext(master)[1]), "volume": 1.0})
    else:
        if voice:
            sounds.append({"src": "assets/" + _copy(voice, adir, "voix" + os.path.splitext(voice)[1]), "volume": 1.0})
        if music:
            sounds.append({"src": "assets/" + _copy(music, adir, "musique" + os.path.splitext(music)[1]),
                           "volume": 0.32 if voice else 0.9})

    # ── Marque ──
    logo_src = _resolve(brief.get("logo"))
    kit = None
    if brief.get("brand"):
        kit = brand_mod.load(brief["brand"]) if isinstance(brief["brand"], (str, dict)) else None
        logo_src = logo_src or _resolve((kit or {}).get("logo"))
    if not kit and logo_src:
        kit = intake.brand_from_logo(name, logo_src)
    kit = kit or brand_mod.load("neutre")
    colors = dict(kit["colors"])
    colors.setdefault("secondary", colors["accent"])
    colors.setdefault("on_accent", _on(colors["accent"]))
    colors.update({k: v for k, v in (brief.get("colors") or {}).items() if v})
    fonts = {}
    for role in ("title", "body"):
        fname = (brief.get("fonts") or {}).get(role) or kit.get("fonts", {}).get(role) \
            or kit.get("fonts", {}).get("heading") or "Montserrat-Black.ttf"
        fonts[role] = _copy(_font_file(fname), os.path.join(adir, "fonts"))
    logo = "assets/" + _copy(logo_src, adir, "logo" + os.path.splitext(logo_src)[1]) if logo_src else None
    prod_src = _resolve((brief.get("product") or {}).get("image") if isinstance(brief.get("product"), dict) else brief.get("product"))
    product = "assets/" + _copy(prod_src, adir, "produit" + os.path.splitext(prod_src)[1]) if prod_src else None

    # ── Storyboard ──
    transcript = None
    if brief.get("scenes"):
        sb = [dict(s) for s in brief["scenes"]]
        if any("start" not in s for s in sb):
            n = len(sb)
            for i, s in enumerate(sb):
                s.setdefault("start", round(duration * i / n, 3))
        _time(sb, duration, lead=0.0)
    elif brief.get("hook"):
        sb = storyboard_from_brief({**brief, "audio_master": brief.get("audio") or brief.get("audio_master"),
                                    "canvas": canvas}, duration)
    elif speech:
        from . import listen
        script = brief.get("script")
        if script and os.path.isfile(str(script)):
            with open(script, encoding="utf-8") as fh:
                script = fh.read()
        transcript = listen.transcribe(speech, script=script if isinstance(script, str) else None)
        if not transcript["phrases"]:
            _fail("impossible de savoir ce que dit l'audio : fournir script.txt (le texte dit), "
                  "installer faster-whisper, ou donner un storyboard \"scenes\"")
        sb = storyboard_from_voice(transcript["phrases"], duration, has_product=bool(product),
                                   brand_name=brief.get("brand_name") or kit.get("title"))
        # médias fournis : ils illustrent les phrases « simples », dans l'ordre
        pool = list(brief.get("media_pool") or [])
        for s in sb:
            if pool and s["type"] == "phrase":
                s.update(type="media", file=pool.pop(0))
        for s in sb:
            if s["type"] == "cta":
                if brief.get("cta"):
                    s["button"] = brief["cta"]
                if brief.get("url"):
                    s["url"] = brief["url"]
    else:
        _fail("rien à monter : fournir l'audio de la pub (audio), un brief (hook…) ou un storyboard (scenes)")
    for s in sb:
        if s.get("type") not in SCENE_TYPES:
            _fail(f"type de scène inconnu '{s.get('type')}' ({', '.join(SCENE_TYPES)})")
        if s.get("type") == "media" and s.get("file"):
            p = _resolve(s["file"])
            s["file"] = "assets/" + _copy(p, adir)
        if s.get("type") == "product" and s.get("image"):
            s["image"] = "assets/" + _copy(_resolve(s["image"]), adir)

    # ── Éléments (bibliothèque libre de droits ou fournis) ──
    edir = os.path.join(adir, "elements")
    icons: dict[int, list] = {}
    auto = brief.get("auto_elements", True)
    for k, s in enumerate(sb):
        if s.get("type") == "benefits":
            ids = [it.get("icon") if isinstance(it, dict) else None for it in s.get("items", [])]
            if auto and not any(ids):
                ids = _auto_icons(s.get("items", []))
            got = _fetch_elements([i for i in ids if i], edir)
            icons[k] = [got.get(i) if i else None for i in ids]
    decor = list(brief.get("decor") or [])
    deco_files = list(_fetch_elements(decor, edir).values()) if decor else []

    doc = compose(sb, canvas=canvas, colors=colors, fonts=fonts, duration=duration, audio=sounds,
                  logo=logo, product=product, icons=icons, decor=deco_files, style=style,
                  subtitles=bool(brief.get("subtitles")), title=brief.get("title") or name)
    with open(os.path.join(pdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    meta = {"id": f"{name}-{canvas}", "name": f"{name}-{canvas}"}
    with open(os.path.join(pdir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    with open(os.path.join(pdir, "hyperframes.json"), "w", encoding="utf-8") as fh:
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"assets": "assets"}, "media": {"autoProxy": True}}, fh, indent=2)
    plan = {"canvas": canvas, "duration": round(duration, 3), "style": style, "colors": colors,
            "fonts": fonts, "logo": logo, "product": product,
            "transcription": (transcript or {}).get("source"),
            "storyboard": [{k: v for k, v in s.items() if k != "words"} for s in sb]}
    with open(os.path.join(pdir, "storyboard.json"), "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=2)
    return {"project": os.path.relpath(pdir, REPO), "dir": pdir, **plan}


# ── Rendu, aperçu, vérification ──────────────────────────────────────────────

def _hf_env() -> dict:
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", HYPERFRAMES_SKIP_SKILLS="1",
               HYPERFRAMES_NO_UPDATE_CHECK="1")
    if not env.get("HYPERFRAMES_BROWSER_PATH"):
        for cand in ("/opt/pw-browsers/chromium", "/tmp/chromium"):
            if os.path.exists(cand):
                env["HYPERFRAMES_BROWSER_PATH"] = cand
                break
    env.setdefault("CHROMIUM_FLAGS", "--no-sandbox")
    return env


def _hf(args: list[str], timeout: int = 1800) -> str:
    import subprocess
    exe = os.path.join(REPO, "node_modules", ".bin", "hyperframes")
    cmd = [exe] if os.path.isfile(exe) else ["npx", "--yes", "hyperframes@0.8.142"]
    proc = subprocess.run(cmd + args, cwd=REPO, env=_hf_env(), capture_output=True, text=True, timeout=timeout)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        tail = "\n".join(l for l in out.splitlines() if "Render:trace" not in l)[-2500:]
        _fail(f"hyperframes {args[0]} a échoué :\n{tail}")
    return out


def check(pdir: str) -> dict:
    """Contrôle HyperFrames (erreurs bloquantes / avertissements)."""
    out = _hf(["lint", pdir], timeout=300)
    m = re.search(r"(\d+) error\(s\), (\d+) warning\(s\)", out)
    return {"errors": int(m.group(1)) if m else 0, "warnings": int(m.group(2)) if m else 0}


def preview(pdir: str, at: list[float] | None = None, count: int = 8, width: int = 270) -> dict:
    """Images clés rendues par le vrai moteur HyperFrames + planche contact."""
    import subprocess
    from . import ffmpeg as ff
    out_dir = os.path.join(REPO, ".cache", "apercus", os.path.basename(pdir))
    shutil.rmtree(out_dir, ignore_errors=True)
    if not at:
        with open(os.path.join(pdir, "storyboard.json"), encoding="utf-8") as fh:
            sb = json.load(fh)
        at = []
        for s in sb["storyboard"]:
            at.append(round(s["start"] + max(0.3, min(s["duration"] - 0.25, s["duration"] * 0.72)), 2))
        at = at[:max(count, len(at))]
    _hf(["snapshot", pdir, "-o", out_dir, "--at", ",".join(f"{t:.2f}" for t in at), "--no-end"], timeout=600)
    frames = sorted(os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.startswith("frame") and f.endswith(".png"))
    sheet = os.path.join(out_dir, "planche.jpg")
    cols = min(len(frames), 8)
    subprocess.run([ff.ffmpeg_exe(), "-v", "error", "-y", "-pattern_type", "glob", "-i",
                    os.path.join(out_dir, "frame*.png"), "-vf",
                    f"scale={width}:-1,tile={cols}x{math.ceil(len(frames) / cols)}:padding=6:color=0x111111",
                    "-frames:v", "1", sheet], check=True)
    return {"frames": [os.path.relpath(f, REPO) for f in frames], "sheet": os.path.relpath(sheet, REPO),
            "at": at}


def render(pdir: str, out: str | None = None, quality: str = "standard", loudness: float = -14.0) -> str:
    """Rendu HyperFrames → MP4, puis son normalisé (réseaux sociaux : -14 LUFS)."""
    import subprocess
    from . import ffmpeg as ff
    name = os.path.basename(os.path.normpath(pdir))
    out = out or os.path.join(REPO, ".cache", "rendus", f"{name}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    raw = out + ".brut.mp4"
    _hf(["render", pdir, "--quality", quality, "-o", raw])
    info = probe.probe(raw)
    if info.get("audio"):
        tmp = out + ".part.mp4"
        r = subprocess.run([ff.ffmpeg_exe(), "-v", "error", "-y", "-i", raw, "-c:v", "copy",
                            "-af", f"loudnorm=I={loudness}:TP=-1.5:LRA=11", "-ar", "48000",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp],
                           capture_output=True, text=True)
        if r.returncode == 0:
            os.replace(tmp, out)
            os.remove(raw)
        else:
            os.replace(raw, out)
    else:
        os.replace(raw, out)
    # coupes exactes pour la vérification
    try:
        with open(os.path.join(pdir, "storyboard.json"), encoding="utf-8") as fh:
            sb = json.load(fh)["storyboard"]
        with open(out + ".events.json", "w", encoding="utf-8") as fh:
            json.dump([{"type": "cut", "t": s["start"]} for s in sb[1:]], fh)
    except (OSError, KeyError, ValueError):
        pass
    return out


def produce(brief: dict, formats: list[str] | None = None, quality: str = "standard",
            name: str | None = None, do_render: bool = True, do_preview: bool = True) -> dict:
    """Le geste complet : construire, contrôler, prévisualiser, rendre, vérifier (par format)."""
    from . import verify
    formats = formats or [brief.get("canvas", "9x16")]
    results = []
    for fmt in formats:
        plan = build(brief, canvas=fmt, name=name)
        item = {"format": fmt, "project": plan["project"], "storyboard": plan["storyboard"],
                "duration": plan["duration"], "check": check(plan["dir"])}
        if do_preview:
            item["preview"] = preview(plan["dir"])
        if do_render:
            path = render(plan["dir"], quality=quality)
            rep = verify.verify(path, expect=plan["duration"], expect_audio=bool(brief.get("audio") or brief.get("audio_master") or brief.get("voiceover") or brief.get("music")))
            rep.pop("rapport_brut", None)
            item.update(video=os.path.relpath(path, REPO), verification=rep)
        results.append(item)
    return {"results": results}


# ── Depuis un dossier d'entrées ──────────────────────────────────────────────

_DETAIL_KEYS = {
    "marque": "brand_name", "nom": "brand_name", "brand": "brand_name",
    "site": "url", "url": "url", "lien": "url", "web": "url",
    "bouton": "cta", "cta": "cta", "appel": "cta",
    "style": "style", "ton": "style", "couleur": "accent", "accent": "accent",
    "format": "canvas", "formats": "formats", "sous-titres": "subtitles", "soustitres": "subtitles",
}


def parse_details(text: str) -> dict:
    """Lignes « clé : valeur » d'un details.txt (marque, site, bouton, style, couleur…)."""
    out: dict = {}
    for line in text.splitlines():
        m = re.match(r"\s*[-•*]?\s*([\wÀ-ÿ -]{2,20})\s*[:=]\s*(.+)$", line)
        if not m:
            continue
        key = _DETAIL_KEYS.get(m.group(1).strip().lower())
        if key:
            out[key] = m.group(2).strip()
    if "subtitles" in out:
        out["subtitles"] = out["subtitles"].lower() in ("oui", "yes", "true", "1")
    if "style" in out:
        st = out["style"].lower()
        out["style"] = next((k for k in STYLES if k in st), "energique")
    return out


def brief_from_folder(folder: str | None = None) -> dict:
    """entrees/ → brief : audio, logo, texte dit, détails, produit, médias."""
    folder = folder or os.path.join(REPO, "entrees")
    rep = intake.scan(folder)
    files = rep.get("fichiers", {})
    absf = lambda p: os.path.abspath(os.path.join(REPO, p)) if not os.path.isabs(p) else p  # noqa: E731
    brief: dict = {"name": os.path.basename(os.path.abspath(folder)) if folder else "pub"}
    if files.get("audio"):
        brief["audio"] = absf(files["audio"][0])
    if files.get("logo"):
        brief["logo"] = absf(files["logo"][0])
    if files.get("script"):
        brief["script"] = absf(files["script"][0])
    for d in (files.get("text") or []) + (files.get("details") or []):
        with open(absf(d), encoding="utf-8") as fh:
            brief.update(parse_details(fh.read()))
    images = [absf(m["file"]) for m in rep.get("medias", []) if m.get("kind") == "image"]
    videos = [absf(m["file"]) for m in rep.get("medias", []) if m.get("kind") == "video"]
    prod = next((i for i in images if re.search(r"produit|product|packshot|box|app", os.path.basename(i), re.I)), None)
    if prod:
        brief["product"] = {"image": prod}
        images.remove(prod)
    if images or videos:
        brief["media_pool"] = videos + images
    if brief.get("accent"):
        brief["colors"] = {"accent": brief.pop("accent")}
    brief["_manquants"] = rep.get("manquants", [])
    return brief
