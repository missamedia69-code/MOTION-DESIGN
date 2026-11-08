"""Compositeur publicitaire : un brief court → un montage pub complet.

L'agent (ou l'humain) décrit le *message*, pas l'animation :

    {"template": "promo", "brand": "missa", "canvas": "9x16",
     "hook": "La télé coûte trop cher ?",
     "product": {"image": "assets/images/box-mtn-cutout.png", "name": "Box MISSA"},
     "benefits": ["300 chaînes", "Installation offerte"],
     "proof": {"value": 10000, "suffix": "+", "label": "abonnés"},
     "offer": {"price": 1000, "old_price": 2000, "currency": "FCFA", "label": "par mois"},
     "cta": "Je m'abonne", "url": "missa.tv", "music": "assets/audio/…"}

Le compositeur choisit la mise en scène (rythme, hiérarchie, animations,
couleurs du kit de marque) et produit un `project.json` standard. Toutes les
positions sont relatives (%, vmin) : le même brief se rend en 9x16, 1x1, 4x5
ou 16x9 sans retouche.
"""
from __future__ import annotations

import copy
import re

from . import brand as brand_mod, presets

TEMPLATES = {
    "promo": {
        "label": "Promo produit complète",
        "scenes": ["hook", "product", "benefits", "proof", "offer", "cta"],
        "pace": 1.0,
        "usage": "présenter un produit/service : accroche → produit → bénéfices → preuve → offre → CTA",
    },
    "offre": {
        "label": "Offre flash / soldes",
        "scenes": ["hook", "offer", "benefits", "cta"],
        "pace": 0.85,
        "usage": "promotion limitée : prix barré qui chute, badge, urgence",
    },
    "annonce": {
        "label": "Annonce / lancement",
        "scenes": ["hook", "product", "benefits", "cta"],
        "pace": 1.0,
        "usage": "nouveauté, lancement, événement",
    },
    "preuve": {
        "label": "Preuve sociale / chiffres",
        "scenes": ["hook", "proof", "benefits", "cta"],
        "pace": 1.0,
        "usage": "mettre en avant un chiffre fort (abonnés, ventes, notes)",
    },
}

BASE_DURATIONS = {"hook": 2.4, "product": 2.8, "benefits": 1.4, "proof": 2.6,
                  "offer": 3.0, "cta": 3.0}
DEFAULT_COLORS = {"background": "#111318", "surface": "#1C1F27", "accent": "#4F8CFF",
                  "text": "#FFFFFF", "muted": "#A3A9B8", "on_accent": "#FFFFFF"}
DEFAULT_FONTS = {"title": "Montserrat-Black.ttf", "heading": "Montserrat-ExtraBold.ttf",
                 "body": "Montserrat-Bold.ttf"}
CHECK_FONT = "DejaVuSans-Bold.ttf"
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def templates() -> dict:
    return {k: {"label": v["label"], "scenes": v["scenes"], "usage": v["usage"]}
            for k, v in TEMPLATES.items()}


def example() -> dict:
    return {
        "template": "promo",
        "name": "pub-box-missa",
        "brand": "missa",
        "canvas": "9x16",
        "preset": "mp4-social",
        "duration": 15,
        "hook": "Votre télé vous coûte trop cher ?",
        "product": {"image": "assets/images/box-mtn-cutout.png", "name": "La Box MISSA TV",
                    "tagline": "Toute la télé africaine, partout"},
        "benefits": ["Plus de 300 chaînes", "Installation offerte", "Sans engagement"],
        "proof": {"value": 10000, "prefix": "+", "label": "familles abonnées"},
        "offer": {"price": 1000, "old_price": 2000, "currency": "FCFA", "label": "par mois",
                  "badge": "-50 %"},
        "cta": "Je m'abonne",
        "url": "missa.tv",
    }


def schema() -> dict:
    return {
        "required": ["hook"],
        "fields": {
            "template": f"un de : {', '.join(TEMPLATES)} (défaut promo)",
            "name": "slug du projet (auto si absent)",
            "brand": "kit de marque (brands/<nom>.json) ou objet {colors, fonts, logo}",
            "canvas": f"un de : {', '.join(presets.CANVAS_PRESETS)} (défaut 9x16)",
            "preset": "export (défaut mp4-social : H.264 + -14 LUFS)",
            "duration": "durée cible en secondes (6, 15, 30…) — le rythme s'adapte",
            "hook": "accroche (≤ 60 caractères conseillé), animée mot par mot",
            "product": "{image, name, tagline}",
            "benefits": "liste de 1 à 5 bénéfices courts",
            "proof": "{value, prefix, suffix, label, decimals} → compteur animé",
            "offer": "{price, old_price, currency, label, badge} → prix barré qui chute",
            "cta": "appel à l'action (bouton)",
            "url": "site / handle affiché sous le bouton",
            "music": "fichier musique (bouclé, mixé sous la voix)",
            "voiceover": "fichier voix off (la musique baisse automatiquement dessous)",
            "style": "surcharges : background, surface, accent, text, muted, on_accent, "
                     "font_title, font_body, transition, background_style (gradient|solid)",
        },
        "templates": templates(),
        "example": example(),
    }


def _fail(msg: str):
    raise SystemExit(f"ERREUR de brief pub : {msg}")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "pub"


def _palette(spec: dict) -> tuple[dict, dict, str | None]:
    colors, fonts, logo = dict(DEFAULT_COLORS), dict(DEFAULT_FONTS), None
    if spec.get("brand"):
        kit = brand_mod.load(spec["brand"])
        colors.update(kit.get("colors") or {})
        fonts.update(kit.get("fonts") or {})
        logo = kit.get("logo")
    style = spec.get("style") or {}
    for k in DEFAULT_COLORS:
        if style.get(k):
            colors[k] = style[k]
    if style.get("font_title"):
        fonts["title"] = style["font_title"]
    if style.get("font_body"):
        fonts["body"] = fonts["heading"] = style["font_body"]
    for k, v in colors.items():
        if not HEX_RE.match(str(v)):
            _fail(f"couleur {k} invalide '{v}' (#RRGGBB attendu)")
    if spec.get("logo") is not None:
        logo = spec["logo"] or None
    return colors, fonts, logo


def _fmt_price(v) -> str:
    if isinstance(v, (int, float)) and float(v).is_integer():
        return f"{int(v):,}".replace(",", " ")
    return str(v)


def compose(raw: dict, canvas: str | None = None) -> dict:
    """Retourne un project.json complet à partir d'un brief publicitaire.

    `canvas` force le format (déclinaisons) : la mise en page s'adapte à
    l'orientation (verticale/carrée vs paysage).
    """
    if not isinstance(raw, dict):
        _fail("objet JSON attendu")
    spec = copy.deepcopy(raw)
    if canvas:
        spec["canvas"] = canvas
    tpl_name = spec.get("template", "promo")
    if tpl_name not in TEMPLATES:
        _fail(f"template '{tpl_name}' inconnu ({', '.join(TEMPLATES)})")
    tpl = TEMPLATES[tpl_name]
    hook = str(spec.get("hook") or "").strip()
    if not hook:
        _fail("'hook' (accroche) obligatoire")
    canvas = spec.get("canvas", "9x16")
    if isinstance(canvas, str) and canvas not in presets.CANVAS_PRESETS:
        _fail(f"canvas '{canvas}' inconnu ({', '.join(presets.CANVAS_PRESETS)})")
    preset = spec.get("preset", "mp4-social")
    if preset not in presets.EXPORT_PRESETS:
        _fail(f"preset '{preset}' inconnu ({', '.join(presets.EXPORT_PRESETS)})")
    benefits = [str(b).strip() for b in (spec.get("benefits") or []) if str(b).strip()]
    if len(benefits) > 5:
        _fail("au plus 5 bénéfices (la lisibilité chute au-delà)")
    style = spec.get("style") or {}
    transition = style.get("transition", "smoothleft")
    if transition not in presets.XFADE_TRANSITIONS:
        _fail(f"transition '{transition}' inconnue")
    C, F, logo = _palette(spec)
    vertical = True
    if isinstance(canvas, str):
        cv = presets.CANVAS_PRESETS[canvas]
        vertical = cv["height"] >= cv["width"] * 0.95

    # ── Scènes disponibles selon le contenu ──
    plan = []
    for kind in tpl["scenes"]:
        if kind == "product" and not (spec.get("product") or {}).get("image") \
                and not (spec.get("product") or {}).get("name"):
            continue
        if kind == "benefits" and not benefits:
            continue
        if kind == "proof" and not isinstance((spec.get("proof") or {}).get("value"), (int, float)):
            continue
        if kind == "offer" and (spec.get("offer") or {}).get("price") is None:
            continue
        if kind == "cta" and not spec.get("cta"):
            spec["cta"] = "En savoir plus"
        plan.append(kind)

    durs = {k: BASE_DURATIONS[k] * tpl["pace"] for k in plan}
    if "benefits" in durs:
        durs["benefits"] = (1.2 + 0.75 * len(benefits)) * tpl["pace"]
    tr_dur = 0.4
    target = spec.get("duration")
    if target:
        natural = sum(durs.values()) - tr_dur * (len(plan) - 1)
        k = (float(target) + tr_dur * (len(plan) - 1)) / (natural + tr_dur * (len(plan) - 1))
        durs = {key: max(1.6, round(v * k, 2)) for key, v in durs.items()}

    big = "9vmin" if vertical else "8vmin"
    title_font, body_font = F["title"], F.get("body", F["title"])
    head_font = F.get("heading", body_font)
    bg_style = style.get("background_style", "gradient")

    def background(kind: str):
        if bg_style == "solid":
            return C["background"]
        if kind in ("product", "proof"):
            return {"gradient": [C["surface"], C["background"]], "type": "radial"}
        return {"gradient": [C["background"], C["surface"]], "angle": 160}

    def logo_layer(y: str, w: str, t_in: float, D: float):
        if not logo:
            return []
        return [{"type": "image", "file": logo, "scale": {"w": w}, "pos": ["50%", y],
                 "in": t_in, "out": D, "anim": "fade", "fade_out": 0.01}]

    scenes = []
    for idx, kind in enumerate(plan):
        D = durs[kind]
        L: list[dict] = []
        if kind == "hook":
            L += [
                {"type": "shape", "kind": "rect", "w": "22vmin", "h": "1.2vmin", "radius": 8,
                 "color": C["accent"], "pos": ["50%", "33%"], "in": 0.05, "anim": "grow_x",
                 "anim_duration": 0.5},
                {"type": "text", "text": hook, "split": "word", "stagger": 0.09,
                 "font": title_font, "size": big, "color": C["text"], "max_width": "84vw",
                 "line_height": 1.1, "pos": ["50%", "46%"], "in": 0.1, "anim": "fade_up",
                 "ease": "back_out", "exit": "fade_up", "exit_duration": 0.3},
            ]
            if spec.get("subhook"):
                L.append({"type": "text", "text": str(spec["subhook"]), "font": body_font,
                          "size": "4vmin", "color": C["muted"], "max_width": "80vw",
                          "pos": ["50%", "62%"], "in": 0.8, "anim": "fade"})
        elif kind == "product":
            prod = spec.get("product") or {}
            if prod.get("image"):
                L.append({"type": "shape", "kind": "circle", "w": "62vmin", "h": "62vmin",
                          "color": C["accent"], "opacity": 0.14, "pos": ["50%", "42%"],
                          "in": 0.0, "anim": "scale_in", "anim_duration": 0.8, "idle": "breathe"})
                L.append({"type": "image", "file": prod["image"], "scale": {"w": "56vmin"},
                          "pos": ["50%", "42%"], "in": 0.15, "anim": "scale_in",
                          "anim_duration": 0.7, "idle": "float"})
            if prod.get("name"):
                L.append({"type": "text", "text": str(prod["name"]), "font": head_font,
                          "size": "6.5vmin", "color": C["text"], "max_width": "86vw",
                          "pos": ["50%", "71%" if prod.get("image") else "45%"], "in": 0.55,
                          "anim": "fade_up"})
            if prod.get("tagline"):
                L.append({"type": "text", "text": str(prod["tagline"]), "font": body_font,
                          "size": "3.8vmin", "color": C["muted"], "max_width": "84vw",
                          "pos": ["50%", "78%" if prod.get("image") else "55%"], "in": 0.85,
                          "anim": "fade"})
        elif kind == "benefits":
            n = len(benefits)
            if spec.get("benefits_title"):
                L.append({"type": "text", "text": str(spec["benefits_title"]), "font": head_font,
                          "size": "5vmin", "color": C["accent"], "pos": ["50%", "24%"],
                          "in": 0.1, "anim": "fade"})
            step = 11 if vertical else 14
            y0 = 50 - step * (n - 1) / 2
            for i, b in enumerate(benefits):
                y = f"{y0 + i * step:.1f}%"
                t = round(0.25 + i * 0.55, 2)
                x_icon, x_text = ("16%", "24%") if vertical else ("27%", "32%")
                L += [
                    {"type": "shape", "kind": "circle", "w": "7vmin", "h": "7vmin",
                     "color": C["accent"], "pos": [x_icon, y], "in": t, "anim": "pop"},
                    {"type": "text", "text": "✓", "font": CHECK_FONT, "size": "4.4vmin",
                     "color": C["on_accent"], "pos": [x_icon, y], "in": t + 0.1, "anim": "pop"},
                    {"type": "text", "text": b, "font": head_font, "size": "5vmin",
                     "color": C["text"], "align": "left", "anchor": "left",
                     "max_width": "68vw" if vertical else "55vw", "pos": [x_text, y],
                     "in": t + 0.12, "anim": "fade_left"},
                ]
        elif kind == "proof":
            pr = spec["proof"]
            L += [
                {"type": "counter", "from": float(pr.get("from", 0)), "to": float(pr["value"]),
                 "prefix": str(pr.get("prefix", "")), "suffix": str(pr.get("suffix", "")),
                 "decimals": int(pr.get("decimals", 0)), "count_duration": min(1.6, D * 0.6),
                 "font": title_font, "size": "15vmin", "color": C["accent"],
                 "pos": ["50%", "44%"], "in": 0.1, "anim": "punch"},
                {"type": "text", "text": str(pr.get("label", "")) or " ", "font": head_font,
                 "size": "5vmin", "color": C["text"], "max_width": "84vw",
                 "pos": ["50%", "58%"], "in": 0.6, "anim": "fade_up"},
            ]
            if pr.get("stars"):
                L.append({"type": "text", "text": "★" * int(pr["stars"]), "font": CHECK_FONT,
                          "size": "6vmin", "color": C["accent"], "pos": ["50%", "30%"],
                          "split": "char", "stagger": 0.08, "in": 0.2, "anim": "pop"})
        elif kind == "offer":
            of = spec["offer"]
            cur = f" {of['currency']}" if of.get("currency") else ""
            price = of["price"]
            if isinstance(price, (int, float)) and isinstance(of.get("old_price"), (int, float)):
                L.append({"type": "counter", "from": float(of["old_price"]), "to": float(price),
                          "suffix": cur, "count_duration": 1.2, "ease": "ease_in_out",
                          "font": title_font, "size": "13vmin", "color": C["accent"],
                          "pos": ["50%", "47%"], "in": 0.6, "anim": "punch"})
            else:
                L.append({"type": "text", "text": f"{_fmt_price(price)}{cur}", "font": title_font,
                          "size": "13vmin", "color": C["accent"], "pos": ["50%", "47%"],
                          "in": 0.6, "anim": "punch"})
            if of.get("old_price") is not None:
                L += [
                    {"type": "text", "text": f"{_fmt_price(of['old_price'])}{cur}", "font": head_font,
                     "size": "6vmin", "color": C["muted"], "pos": ["50%", "33%"], "in": 0.1,
                     "anim": "fade_down"},
                    {"type": "shape", "kind": "rect", "w": "34vmin", "h": "0.9vmin", "radius": 4,
                     "color": "#FF4D4D", "pos": ["50%", "33%"], "rotate": -8, "in": 0.45,
                     "anim": "grow_x", "anim_duration": 0.3},
                ]
            if of.get("label"):
                L.append({"type": "text", "text": str(of["label"]), "font": body_font,
                          "size": "4.5vmin", "color": C["text"], "pos": ["50%", "58%"],
                          "in": 1.0, "anim": "fade_up"})
            if of.get("badge"):
                L += [
                    {"type": "shape", "kind": "circle", "w": "22vmin", "h": "22vmin",
                     "color": C["accent"], "pos": ["76%", "22%"], "in": 1.3, "anim": "scale_in",
                     "rotate": 0, "idle": "pulse"},
                    {"type": "text", "text": str(of["badge"]), "font": title_font, "size": "6vmin",
                     "color": C["on_accent"], "pos": ["76%", "22%"], "in": 1.4,
                     "anim": "rotate_in", "rotate": -10, "idle": "pulse"},
                ]
            if of.get("deadline"):
                L.append({"type": "text", "text": str(of["deadline"]), "font": body_font,
                          "size": "3.6vmin", "color": C["muted"], "max_width": "84vw", "pos": ["50%", "66%"],
                          "in": 1.5, "anim": "fade", "uppercase": True, "letter_spacing": 3})
        elif kind == "cta":
            L += logo_layer("28%", "30vmin", 0.1, D)
            if spec.get("cta_title") or spec.get("signature"):
                L.append({"type": "text", "text": str(spec.get("cta_title") or spec["signature"]),
                          "font": head_font, "size": "5.5vmin", "color": C["text"],
                          "max_width": "84vw", "pos": ["50%", "45%"], "in": 0.25,
                          "anim": "fade_up"})
            L += [
                {"type": "shape", "kind": "rect", "w": "66vmin", "h": "14vmin", "radius": "7vmin",
                 "color": C["accent"], "pos": ["50%", "58%"], "in": 0.45, "anim": "pop",
                 "idle": "pulse", "idle_amplitude": 0.03, "idle_period": 1.2},
                {"type": "text", "text": str(spec["cta"]), "font": title_font, "size": "5.6vmin",
                 "color": C["on_accent"], "max_width": "60vmin", "pos": ["50%", "58%"],
                 "in": 0.6, "anim": "pop", "idle": "pulse", "idle_amplitude": 0.03,
                 "idle_period": 1.2},
            ]
            if spec.get("url"):
                L.append({"type": "text", "text": str(spec["url"]), "font": body_font,
                          "size": "4vmin", "color": C["muted"], "pos": ["50%", "69%"],
                          "in": 0.9, "anim": "fade"})
        for layer in L:
            layer.setdefault("out", D)
        sc = {"duration": D, "background": background(kind), "layers": L, "_scene": kind}
        if idx < len(plan) - 1:
            sc["transition"] = {"type": transition, "duration": tr_dur}
        scenes.append(sc)

    project = {
        "name": spec.get("name") or _slug(hook)[:40],
        "title": spec.get("title") or hook,
        "version": 2,
        "canvas": canvas,
        "export": {"preset": preset},
        "transitions": {"type": transition, "duration": tr_dur},
        "scenes": scenes,
        "_ad": {"template": tpl_name, "plan": plan},
    }
    if spec.get("music"):
        m = spec["music"]
        project["audio"] = {"file": m, "volume": 0.8, "loop": True, "fade_out": 1.2} \
            if isinstance(m, str) else m
    if spec.get("voiceover"):
        v = spec["voiceover"]
        project["voiceover"] = {"file": v, "at": 0.3} if isinstance(v, str) else v
    if spec.get("sfx"):
        project["sfx"] = spec["sfx"]
    return project
