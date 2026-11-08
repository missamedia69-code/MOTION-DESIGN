"""Moteur de rendu : compile project.json en commandes ffmpeg et produit le livrable.

Modèle :
  projet = 1..n scènes ; scène = fond + calques (image, texte, forme, vidéo,
  compteur, audio) ; chaque calque a une fenêtre [in, out], une animation
  d'entrée (`anim`), une sortie (`exit`), une animation continue (`idle`) et
  une courbe (`ease`) ;
  les scènes sont rendues en parallèle (avec cache), puis chaînées en xfade ;
  l'audio (musique, voix, effets) est mixé sur la timeline globale, avec
  ducking automatique de la musique sous la voix et normalisation optionnelle.
"""
from __future__ import annotations

import concurrent.futures
import copy
import hashlib
import json
import os
import re
import time

from . import easing, ffmpeg, layout, presets, probe, text

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_VERSION = "2.0"

# ── Catalogue de mouvements ──────────────────────────────────────────────────

ANIMS = ["none", "fade", "fade_up", "fade_down", "fade_left", "fade_right",
         "slide_up", "slide_down", "slide_left", "slide_right",
         "pop", "scale_in", "zoom_in", "punch", "rotate_in",
         "grow_x", "grow_y", "kenburns_in", "kenburns_out",
         "kenburns_pan_left", "kenburns_pan_right"]
EXITS = ["none", "fade", "fade_up", "fade_down", "slide_up", "slide_down",
         "slide_left", "slide_right", "scale_out"]
IDLES = ["none", "float", "drift", "pulse", "sway", "breathe"]
ANCHORS = ["center", "top_left", "top", "top_right", "left", "right",
           "bottom_left", "bottom", "bottom_right"]
LAYER_TYPES = ["image", "text", "video", "shape", "counter", "audio"]

ANIM_HELP = {
    "fade": "fondu", "fade_up": "fondu + montée", "fade_down": "fondu + descente",
    "fade_left": "fondu + glissé vers la gauche", "fade_right": "fondu + glissé vers la droite",
    "slide_up": "entre par le bas de l'écran", "slide_down": "entre par le haut",
    "slide_left": "entre par la droite", "slide_right": "entre par la gauche",
    "pop": "rebond 60→100 % (back_out)", "scale_in": "naît de 0 → 100 % (back_out)",
    "zoom_in": "s'agrandit 70→100 % en fondu", "punch": "arrive de 140 % → 100 % (impact)",
    "rotate_in": "pivote en arrivant", "grow_x": "révélation gauche→droite",
    "grow_y": "révélation bas→haut", "kenburns_in": "zoom lent (plein cadre)",
    "kenburns_out": "dézoom lent", "kenburns_pan_left": "travelling gauche",
    "kenburns_pan_right": "travelling droite",
}

_FADE_IN = {"fade", "fade_up", "fade_down", "fade_left", "fade_right", "pop",
            "zoom_in", "punch", "rotate_in"}
_SCALE_IN = {"pop": (0.6, "back_out"), "scale_in": (0.0, "back_out"),
             "zoom_in": (0.7, "ease_out"), "punch": (1.4, "expo_out"),
             "rotate_in": (0.7, "back_out")}
_DEFAULT_EASE = {"grow_x": "ease_in_out", "grow_y": "ease_in_out",
                 "slide_up": "expo_out", "slide_down": "expo_out",
                 "slide_left": "expo_out", "slide_right": "expo_out"}


# ── Utilitaires ──────────────────────────────────────────────────────────────

def resolve_path(p: str, project_dir: str) -> str:
    """Résout un chemin média : absolu, relatif au projet, à la racine, ou par nom dans assets/."""
    if not isinstance(p, str) or not p:
        _fail(f"Chemin de fichier invalide : {p!r}")
    if os.path.isabs(p):
        return p if os.path.exists(p) else _fail(f"Fichier introuvable : {p}")
    for base in (project_dir, REPO, os.path.join(REPO, "assets")):
        cand = os.path.join(base, p)
        if os.path.exists(cand):
            return os.path.abspath(cand)
    hits = []
    assets_root = os.path.join(REPO, "assets")
    for root, _, files in os.walk(assets_root):
        if os.path.basename(p) in files:
            hits.append(os.path.join(root, os.path.basename(p)))
    if hits:
        return sorted(hits)[0]
    _fail(f"Fichier introuvable : {p} (cherché dans le projet, la racine et assets/)")


def _fail(msg: str):
    raise SystemExit(f"ERREUR : {msg}")


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _num(v) -> str:
    """Nombre compact pour les expressions ffmpeg."""
    return f"{float(v):.4f}".rstrip("0").rstrip(".") or "0"


def _fitted_size(info: dict, fit: str, W: int, H: int, explicit_scale) -> tuple[int, int]:
    iw, ih = info.get("width") or W, info.get("height") or H
    if explicit_scale:
        w = explicit_scale.get("w")
        h = explicit_scale.get("h")
        if w and h:
            return max(2, int(w) // 2 * 2), max(2, int(h) // 2 * 2)
        if w:
            return max(2, int(w) // 2 * 2), max(2, int(ih * (float(w) / iw)) // 2 * 2)
        if h:
            return max(2, int(iw * (float(h) / ih)) // 2 * 2), max(2, int(h) // 2 * 2)
    if fit == "cover" or fit == "stretch":
        return W, H
    if fit == "original":
        return max(2, iw // 2 * 2), max(2, ih // 2 * 2)
    # contain (défaut)
    r = min(W / iw, H / ih, 1.0) if (iw > W or ih > H) else min(W / iw, H / ih)
    return max(2, int(iw * r) // 2 * 2), max(2, int(ih * r) // 2 * 2)


def _scale_filter(fit: str, fw: int, fh: int) -> str:
    if fit == "cover":
        return f"scale={fw}:{fh}:force_original_aspect_ratio=increase,crop={fw}:{fh},setsar=1"
    return f"scale={fw}:{fh},setsar=1"


def _pos_expr(pos, anchor: str = "center"):
    """Retourne (x_base, y_base) en expressions overlay (coin haut-gauche du calque)."""
    if anchor not in ANCHORS:
        _fail(f"anchor inconnu '{anchor}' ({', '.join(ANCHORS)})")
    named = {"center": ("W/2", "H/2"), "top": ("W/2", "H*0.14"), "bottom": ("W/2", "H*0.86"),
             "top_third": ("W/2", "H*0.33"), "bottom_third": ("W/2", "H*0.72")}
    if pos is None:
        pos = "center"
    if isinstance(pos, str):
        if pos not in named:
            _fail(f"Position inconnue : {pos!r} ({'|'.join(named)}|[x,y])")
        px, py = named[pos]
    elif isinstance(pos, (list, tuple)) and len(pos) >= 2:
        px, py = _num(pos[0]), _num(pos[1])
    else:
        _fail(f"Position inconnue : {pos!r} (center|top|bottom|top_third|bottom_third|[x,y])")
    ax = "left" if "left" in anchor else "right" if "right" in anchor else "center"
    ay = "top" if anchor.startswith("top") else "bottom" if anchor.startswith("bottom") else "center"
    x = {"left": f"{px}", "center": f"{px}-w/2", "right": f"{px}-w"}[ax]
    y = {"top": f"{py}", "center": f"{py}-h/2", "bottom": f"{py}-h"}[ay]
    return x, y


# ── Construction du graphe d'une scène ───────────────────────────────────────

class SceneGraph:
    def __init__(self):
        self.inputs: list[list[str]] = []
        self.filters: list[str] = []
        self.n_video_inputs = 0

    def add_input(self, args: list[str]) -> int:
        self.inputs.append(args)
        idx = len(self.inputs) - 1
        self.n_video_inputs += 1
        return idx


def _background_input(g: SceneGraph, bg, W: int, H: int, FPS: float, D: float,
                      project_dir: str, cache_dir: str, scene_idx: int,
                      transparent_bg: bool) -> None:
    if (bg in ("transparent", None)) and transparent_bg:
        i = g.add_input(["-f", "lavfi", "-t", f"{D}", "-i", f"color=c=black@0:s={W}x{H}:r={FPS}"])
        g.filters.append(f"[{i}:v]format=rgba,setsar=1[bg]")
        return
    if bg in ("transparent", None):
        bg = "#000000"
    if isinstance(bg, dict):
        if bg.get("gradient"):
            path = text.render_gradient_png(bg, W, H, os.path.join(cache_dir, f"s{scene_idx}_bg.png"))
        elif bg.get("image"):
            path = resolve_path(bg["image"], project_dir)
        else:
            _fail(f"scène {scene_idx} : fond objet attendu {{gradient:[…]}} ou {{image:…}}")
        i = g.add_input(["-loop", "1", "-framerate", f"{FPS}", "-t", f"{D}", "-i", path])
        g.filters.append(f"[{i}:v]{_scale_filter('cover', W, H)},format=rgba[bg]")
        return
    if isinstance(bg, str) and re.match(r"^(#|0x)?[0-9a-fA-F]{6}$", bg):
        i = g.add_input(["-f", "lavfi", "-t", f"{D}", "-i", f"color=c={bg}:s={W}x{H}:r={FPS}"])
        g.filters.append(f"[{i}:v]format=rgba,setsar=1[bg]")
        return
    p = resolve_path(bg, project_dir)
    i = g.add_input(["-loop", "1", "-framerate", f"{FPS}", "-t", f"{D}", "-i", p])
    g.filters.append(f"[{i}:v]{_scale_filter('cover', W, H)},format=rgba[bg]")


def build_scene_graph(scene: dict, canvas: dict, project_dir: str, cache_dir: str,
                      scene_idx: int, transparent_bg: bool = False) -> tuple[SceneGraph, str, float]:
    """Construit inputs+filtres d'une scène. Retourne (graphe, label vidéo, durée)."""
    W, H, FPS = int(canvas["width"]), int(canvas["height"]), float(canvas["fps"])
    D = float(scene.get("duration", canvas.get("duration", 5)))
    if D <= 0:
        _fail(f"scène {scene_idx} : durée invalide ({D})")
    g = SceneGraph()
    bg = scene.get("background", "#000000" if not transparent_bg else "transparent")
    _background_input(g, bg, W, H, FPS, D, project_dir, cache_dir, scene_idx, transparent_bg)

    prev = "bg"
    for li, layer in enumerate(scene.get("layers", [])):
        if layer.get("type") == "audio":
            continue  # mixé par collect_audio
        if layer.get("enabled") is False:
            continue
        tag = f"s{scene_idx}l{li}"
        for sub_i, sub in enumerate(_expand_layer(layer, li, tag, canvas, D, project_dir, cache_dir)):
            prev = _add_layer(g, sub, li, f"{tag}k{sub_i}", canvas, D, project_dir, cache_dir, prev)

    g.filters.append(f"[{prev}]format=yuv420p" if not transparent_bg else f"[{prev}]format=rgba")
    g.filters[-1] += "[vout]"
    return g, "vout", D


def _expand_layer(layer: dict, li: int, tag: str, canvas: dict, D: float,
                  project_dir: str, cache_dir: str) -> list[dict]:
    """Texte cinétique (`split`) → N calques image superposés en cascade."""
    if layer.get("type") != "text" or not layer.get("split"):
        return [layer]
    paths = text.render_text_tokens(layer, os.path.join(cache_dir, "tokens"), tag, project_dir)
    stagger = float(layer.get("stagger", 0.08))
    t_in = float(layer.get("in", 0))
    out = []
    has_box = bool(layer.get("box"))
    for k, p in enumerate(paths):
        sub = {key: v for key, v in layer.items()
               if key not in ("type", "text", "split", "stagger", "box", "max_width")}
        sub.update({"type": "image", "file": p, "fit": "original"})
        sub.pop("scale", None)
        if has_box and k == 0:
            sub["in"] = t_in
            sub["anim"] = layer.get("box_anim", "grow_x")
            sub.setdefault("anim_duration", 0.45)
        else:
            idx = k - 1 if has_box else k
            sub["in"] = round(t_in + (0.15 if has_box else 0) + idx * stagger, 3)
            sub["anim"] = layer.get("anim", "fade_up") if layer.get("anim", "none") != "none" else "fade_up"
            sub.setdefault("amplitude", max(12, float(layer.get("size", 64)) * 0.5))
        if float(sub.get("out", D)) <= float(sub["in"]):
            sub["in"] = max(0.0, float(sub.get("out", D)) - 0.05)
        out.append(sub)
    return out


def _source(g: SceneGraph, layer: dict, li: int, tag: str, canvas: dict, L: float,
            project_dir: str, cache_dir: str):
    """Prépare l'entrée ffmpeg d'un calque. Retourne (idx, chain, fw, fh, kind)."""
    W, H, FPS = int(canvas["width"]), int(canvas["height"]), float(canvas["fps"])
    ltype = layer.get("type", "image")
    fit = layer.get("fit")
    chain: list[str] = []
    anim = layer.get("anim", "none")

    if ltype == "counter":
        pattern, n = text.render_counter_frames(layer, os.path.join(cache_dir, "counters"),
                                                tag, FPS, project_dir)
        info = probe.probe(pattern % 0)
        fw, fh = _fitted_size(info, "original", W, H, None)
        i = g.add_input(["-framerate", f"{FPS}", "-start_number", "0", "-i", pattern])
        hold = max(0.0, L - (n - 1) / FPS) + 1.0
        chain.append(f"tpad=stop_mode=clone:stop_duration={_num(hold)}")
        chain.append(f"trim=duration={_num(L)},setpts=PTS-STARTPTS")
        chain.append(f"scale={fw}:{fh},setsar=1")
        return i, chain, fw, fh, "image"

    if ltype == "text":
        src = text.render_text_png(layer, os.path.join(cache_dir, f"{tag}_text.png"),
                                   W, H, project_dir)
        kind, fit = "image", fit or "original"
    elif ltype == "shape":
        src = text.render_shape_png(layer, os.path.join(cache_dir, f"{tag}_shape.png"))
        kind, fit = "image", fit or "original"
    elif ltype == "image":
        src = resolve_path(layer.get("file"), project_dir)
        kind = "image"
        fit = fit or ("cover" if layer.get("full_bleed") else "original")
    else:
        src = resolve_path(layer.get("file"), project_dir)
        kind, fit = "video", fit or "cover"

    info = probe.probe(src)
    if "error" in info:
        _fail(f"Calque {li} : média illisible {src} ({info['error']})")
    fw, fh = _fitted_size(info, fit, W, H, layer.get("scale"))

    if kind == "image" and anim.startswith("kenburns"):
        n = max(2, round(L * FPS))
        i = g.add_input(["-framerate", f"{FPS}", "-i", src])
        up_w, up_h = W * 2, H * 2
        chain.append(f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,"
                     f"crop={up_w}:{up_h},setsar=1")
        e = easing.ease(layer.get("ease", "ease_in_out"), f"on/{n - 1}")
        strength = float(layer.get("zoom", 0.22))
        zc = (f"z='1+{_num(strength)}*{e}'" if anim == "kenburns_in" else
              f"z='{_num(1 + strength)}-{_num(strength)}*{e}'" if anim == "kenburns_out" else
              f"z='{_num(1 + strength * 0.8)}'")
        if anim == "kenburns_pan_left":
            xy = f"x='(iw-iw/zoom)*(1-{e})':y='(ih-ih/zoom)/2'"
        elif anim == "kenburns_pan_right":
            xy = f"x='(iw-iw/zoom)*{e}':y='(ih-ih/zoom)/2'"
        else:
            xy = "x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        chain.append(f"zoompan={zc}:{xy}:d={n}:s={W}x{H}:fps={FPS}")
        chain.append(f"setpts=N/{FPS}/TB")
        return i, chain, W, H, "kenburns"
    if kind == "video":
        src_in = float(layer.get("src_in", 0))
        speed = float(layer.get("speed", 1.0))
        args = ["-stream_loop", "-1"] if layer.get("loop") else []
        i = g.add_input(args + ["-i", src])
        chain.append(f"trim=start={_num(src_in)}:duration={_num(L * speed)},setpts=PTS-STARTPTS")
        if speed != 1.0:
            chain.append(f"setpts=PTS/{_num(speed)}")
        chain.append(f"fps={FPS}")
        chain.append(_scale_filter(fit, fw, fh))
        return i, chain, fw, fh, "video"
    i = g.add_input(["-loop", "1", "-framerate", f"{FPS}", "-t", f"{_num(L)}", "-i", src])
    chain.append(_scale_filter(fit, fw, fh))
    return i, chain, fw, fh, "image"


def _add_layer(g: SceneGraph, layer: dict, li: int, tag: str, canvas: dict, D: float,
               project_dir: str, cache_dir: str, prev: str) -> str:
    W, H = int(canvas["width"]), int(canvas["height"])
    ltype = layer.get("type", "image")
    if ltype not in LAYER_TYPES or ltype == "audio":
        _fail(f"Calque {li} : type inconnu '{ltype}' ({'|'.join(LAYER_TYPES)})")
    anim = layer.get("anim", "none")
    if anim not in ANIMS:
        _fail(f"Calque {li} : animation inconnue '{anim}'. Dispo : {', '.join(ANIMS)}")
    exit_ = layer.get("exit", "none")
    if exit_ not in EXITS:
        _fail(f"Calque {li} : sortie inconnue '{exit_}'. Dispo : {', '.join(EXITS)}")
    idle = layer.get("idle", "none")
    if idle not in IDLES:
        _fail(f"Calque {li} : idle inconnu '{idle}'. Dispo : {', '.join(IDLES)}")

    t_in = _clamp(float(layer.get("in", 0)), 0.0, max(0.0, D - 0.04))
    t_out = _clamp(float(layer.get("out", D)), t_in + 0.04, D)
    L = t_out - t_in

    i, chain, fw, fh, kind = _source(g, layer, li, tag, canvas, L, project_dir, cache_dir)
    chain.append("format=rgba")

    ad = max(0.05, float(layer.get("anim_duration", 0.6)))
    ed = _clamp(float(layer.get("exit_duration", 0.45)), 0.05, max(0.05, L / 2))
    curve = layer.get("ease") or _DEFAULT_EASE.get(anim) or (
        _SCALE_IN[anim][1] if anim in _SCALE_IN else easing.DEFAULT)
    exit_curve = layer.get("exit_ease", "ease_in")
    e_in = easing.ease(curve, easing.progress("t", 0, ad))           # timeline locale
    e_out = easing.ease(exit_curve, easing.progress("t", L - ed, ed))
    animated = False

    # ── Rotation (statique, rotate_in, sway) ──
    rot = float(layer.get("rotate", 0))
    period = max(0.2, float(layer.get("idle_period", 2.4)))
    angle_terms = []
    if rot:
        angle_terms.append(f"{_num(rot)}*PI/180")
    if anim == "rotate_in":
        angle_terms.append(f"-0.6*(1-{e_in})")
    if idle == "sway":
        angle_terms.append(f"{_num(float(layer.get('idle_amplitude', 3)))}*PI/180*sin(2*PI*t/{_num(period)})")
    if angle_terms and kind != "kenburns":
        a = "+".join(angle_terms)
        diag = int((fw ** 2 + fh ** 2) ** 0.5) // 2 * 2 + 2
        chain.append(f"rotate=a='{a}':c=none:ow={diag}:oh={diag}")
        fw = fh = diag
        animated = animated or anim == "rotate_in" or idle == "sway"

    # ── Opacité globale ──
    opacity = float(layer.get("opacity", 1.0))
    if opacity < 1.0:
        chain.append(f"colorchannelmixer=aa={_num(max(0.0, opacity))}")

    # ── Fondus alpha ──
    legacy_fade_out = exit_ == "none" and "exit" not in layer and anim.startswith("fade")
    if anim in _FADE_IN:
        default_fi = 0.5 if anim.startswith("fade") else ad * 0.6
        fi = _clamp(float(layer.get("fade_in", default_fi)), 0.01, L / 2)
        chain.append(f"fade=t=in:st=0:d={_num(fi)}:alpha=1")
    if legacy_fade_out or exit_ in ("fade", "fade_up", "fade_down", "scale_out"):
        fo = _clamp(float(layer.get("fade_out", 0.5 if legacy_fade_out else ed)), 0.01, L / 2)
        chain.append(f"fade=t=out:st={_num(L - fo)}:d={_num(fo)}:alpha=1")

    # ── Révélations (masque) ──
    # (masque alpha animé : `crop` n'évalue sa taille qu'une fois, d'où geq)
    if anim in ("grow_x", "grow_y"):
        e_mask = easing.ease(curve, easing.progress("T", 0, ad))
        cond = f"lte(X,W*{e_mask})" if anim == "grow_x" else f"gte(Y,H*(1-{e_mask}))"
        chain.append(f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if({cond},alpha(X,Y),0)'")

    # ── Échelle animée (entrée × sortie × idle) ──
    factors = []
    if anim in _SCALE_IN:
        s0 = _SCALE_IN[anim][0]
        factors.append(f"({_num(s0)}+{_num(1 - s0)}*{e_in})")
    if exit_ == "scale_out":
        factors.append(f"(1-{e_out})")
    if idle == "pulse":
        amp = float(layer.get("idle_amplitude", 0.04))
        factors.append(f"(1+{_num(amp)}*sin(2*PI*t/{_num(period)}))")
    elif idle == "breathe":
        amp = float(layer.get("idle_amplitude", 0.03))
        factors.append(f"(1+{_num(amp)}*(1-cos(2*PI*t/{_num(period * 2)}))/2)")
    if factors and kind != "kenburns":
        s = "*".join(factors)
        chain.append(f"scale=w='max(1,{fw}*{s})':h='max(1,{fh}*{s})':eval=frame")
        animated = True

    chain.append(f"setpts=PTS+{_num(t_in)}/TB")
    g.filters.append(f"[{i}:v]{','.join(chain)}[{tag}]")

    # ── Placement + mouvements (timeline de la scène) ──
    xb, yb = _pos_expr(layer.get("pos"), layer.get("anchor", "center"))
    if kind == "kenburns":
        xb, yb = "0", "0"
    x, y = xb, yb
    E_in = easing.ease(curve, easing.progress("t", t_in, ad))
    E_out = easing.ease(exit_curve, easing.progress("t", t_out - ed, ed))
    amp = float(layer.get("amplitude", max(24, H * 0.04)))
    explicit_amp = "amplitude" in layer
    dx, dy = [], []
    if anim in ("fade_up",):
        dy.append(f"{_num(amp)}*(1-{E_in})")
    elif anim == "fade_down":
        dy.append(f"-{_num(amp)}*(1-{E_in})")
    elif anim == "fade_left":
        dx.append(f"{_num(amp)}*(1-{E_in})")
    elif anim == "fade_right":
        dx.append(f"-{_num(amp)}*(1-{E_in})")
    elif anim == "slide_up":
        dy.append(f"{_num(amp)}*(1-{E_in})" if explicit_amp else f"(H-({yb}))*(1-{E_in})")
    elif anim == "slide_down":
        dy.append(f"-{_num(amp)}*(1-{E_in})" if explicit_amp else f"-(({yb})+h)*(1-{E_in})")
    elif anim == "slide_left":
        dx.append(f"{_num(amp)}*(1-{E_in})" if explicit_amp else f"(W-({xb}))*(1-{E_in})")
    elif anim == "slide_right":
        dx.append(f"-{_num(amp)}*(1-{E_in})" if explicit_amp else f"-(({xb})+w)*(1-{E_in})")

    if exit_ == "fade_up":
        dy.append(f"-{_num(amp)}*{E_out}")
    elif exit_ == "fade_down":
        dy.append(f"{_num(amp)}*{E_out}")
    elif exit_ == "slide_up":
        dy.append(f"-(({yb})+h)*{E_out}")
    elif exit_ == "slide_down":
        dy.append(f"(H-({yb}))*{E_out}")
    elif exit_ == "slide_left":
        dx.append(f"-(({xb})+w)*{E_out}")
    elif exit_ == "slide_right":
        dx.append(f"(W-({xb}))*{E_out}")

    if idle in ("float", "drift"):
        ia = float(layer.get("idle_amplitude", max(6, H * 0.008)))
        wave = f"{_num(ia)}*sin(2*PI*(t-{_num(t_in)})/{_num(period)})"
        (dy if idle == "float" else dx).append(wave)
    if dx:
        x = f"({xb})+" + "+".join(f"({d})" for d in dx)
    if dy:
        y = f"({yb})+" + "+".join(f"({d})" for d in dy)
    time_dependent = bool(dx or dy) or animated
    ev = ":eval=frame" if time_dependent else ""
    g.filters.append(
        f"[{prev}][{tag}]overlay=x='{x}':y='{y}':repeatlast=0:eof_action=pass{ev}[{tag}o]")
    return f"{tag}o"


# ── Timeline globale ─────────────────────────────────────────────────────────

def scene_starts(proj: dict, scenes: list[dict]) -> tuple[list[float], float]:
    """Instants de début de chaque scène sur la timeline finale + durée totale."""
    tr = proj.get("transitions", {}) or {}
    tr_dur = float(tr.get("duration", 0.5))
    starts, t = [], 0.0
    for k, sc in enumerate(scenes):
        starts.append(round(t, 4))
        if k < len(scenes) - 1:
            d_tr = float((sc.get("transition") or {}).get("duration", tr_dur))
            t += float(sc.get("duration", 5)) - d_tr
        else:
            t += float(sc.get("duration", 5))
    return starts, round(t, 4)


# ── Audio ────────────────────────────────────────────────────────────────────

AUDIO_ROLES = ("music", "voice", "sfx")


def _track(item, project_dir: str, at_offset: float = 0.0, role: str = "music") -> dict:
    if isinstance(item, str):
        item = {"file": item}
    path = resolve_path(item.get("file"), project_dir)
    r = item.get("role", role)
    if r not in AUDIO_ROLES:
        _fail(f"audio : rôle '{r}' inconnu ({'|'.join(AUDIO_ROLES)})")
    info = probe.probe(path)
    return {
        "path": path,
        "at": at_offset + float(item.get("at", item.get("in", 0))),
        "src_in": float(item.get("src_in", 0)),
        "volume": float(item.get("volume", 1.0)),
        "fade_in": float(item.get("fade_in", 0.5 if r == "music" else 0)),
        "fade_out": float(item.get("fade_out", 1.0 if r == "music" else 0)),
        "loop": bool(item.get("loop", False)),
        "role": r,
        "file_duration": info.get("duration") or 0,
    }


def collect_audio(proj: dict, D: float, project_dir: str, scenes: list[dict] | None = None,
                  starts: list[float] | None = None) -> list[dict]:
    """Toutes les pistes audio du projet, positionnées sur la timeline globale."""
    tracks: list[dict] = []
    a = proj.get("audio")
    for item in (a if isinstance(a, list) else [a] if a else []):
        tracks.append(_track(item, project_dir, role="music"))
    vo = proj.get("voiceover")
    for item in (vo if isinstance(vo, list) else [vo] if vo else []):
        tracks.append(_track(item, project_dir, role="voice"))
    for item in proj.get("sfx", []) or []:
        tracks.append(_track(item, project_dir, role="sfx"))
    scenes = scenes if scenes is not None else (proj.get("scenes") or [proj])
    starts = starts if starts is not None else scene_starts(proj, scenes)[0]
    for sc, s0 in zip(scenes, starts):
        for layer in sc.get("layers", []):
            if layer.get("enabled") is False:
                continue
            if layer.get("type") == "audio":
                tracks.append(_track(layer, project_dir, at_offset=s0, role="sfx"))
            elif layer.get("type") == "video" and layer.get("keep_audio"):
                info = probe.probe(resolve_path(layer["file"], project_dir))
                if info.get("audio"):
                    tracks.append(_track({"file": layer["file"], "at": layer.get("in", 0),
                                          "src_in": layer.get("src_in", 0),
                                          "volume": layer.get("audio_volume", 1.0),
                                          "role": layer.get("audio_role", "voice"),
                                          "fade_in": 0.05, "fade_out": 0.1},
                                         project_dir, at_offset=s0))
    return [t for t in tracks if t["at"] < D]


def audio_input_args(tracks: list[dict]) -> list[str]:
    args: list[str] = []
    for t in tracks:
        if t["loop"]:
            args += ["-stream_loop", "-1"]
        args += ["-i", t["path"]]
    return args


def audio_filters(tracks: list[dict], first_input: int, D: float, mix: dict | None = None) -> list[str]:
    """Graphe audio : pistes → (ducking musique sous la voix) → mix → normalisation."""
    mix = mix or {}
    filters, groups = [], {"music": [], "voice": [], "sfx": []}
    for j, t in enumerate(tracks):
        idx = first_input + j
        avail = (t["file_duration"] - t["src_in"]) if t["file_duration"] and not t["loop"] else D
        length = max(0.05, min(avail, D - t["at"]))
        parts = [f"atrim=start={_num(t['src_in'])}:duration={_num(length)}",
                 "asetpts=PTS-STARTPTS", "aresample=48000",
                 "aformat=sample_fmts=fltp:channel_layouts=stereo",
                 f"volume={_num(t['volume'])}"]
        if t["fade_in"]:
            parts.append(f"afade=t=in:st=0:d={_num(min(t['fade_in'], length / 2))}")
        if t["fade_out"]:
            fo = min(t["fade_out"], length / 2)
            parts.append(f"afade=t=out:st={_num(length - fo)}:d={_num(fo)}")
        ms = int(round(t["at"] * 1000))
        if ms > 0:
            parts.append(f"adelay={ms}:all=1")
        lbl = f"a{j}"
        filters.append(f"[{idx}:a]{','.join(parts)}[{lbl}]")
        groups[t["role"]].append(lbl)

    def mixdown(labels: list[str], out: str) -> str:
        if len(labels) == 1:
            filters.append(f"[{labels[0]}]anull[{out}]")
        else:
            filters.append("".join(f"[{l}]" for l in labels) +
                           f"amix=inputs={len(labels)}:duration=longest:normalize=0[{out}]")
        return out

    finals = []
    duck = mix.get("duck", True)
    if groups["voice"]:
        vox = mixdown(groups["voice"], "vox")
        if groups["music"] and duck:
            filters.append(f"[{vox}]asplit=2[voxm][voxk]")
            mus = mixdown(groups["music"], "mus")
            strength = float(mix.get("duck_ratio", 8))
            filters.append(f"[{mus}][voxk]sidechaincompress=threshold={_num(mix.get('duck_threshold', 0.03))}"
                           f":ratio={_num(strength)}:attack=20:release={int(mix.get('duck_release', 400))}[musd]")
            finals += ["musd", "voxm"]
        else:
            finals.append(vox)
            if groups["music"]:
                finals.append(mixdown(groups["music"], "mus"))
    elif groups["music"]:
        finals.append(mixdown(groups["music"], "mus"))
    if groups["sfx"]:
        finals.append(mixdown(groups["sfx"], "fx"))
    master = mixdown(finals, "amaster") if len(finals) > 1 else finals[0]
    post = ["apad", f"atrim=0:{_num(D)}", "asetpts=N/SR/TB"]
    lufs = mix.get("loudnorm")
    if lufs not in (None, False):
        target = -14.0 if lufs is True else float(lufs)
        post.insert(0, f"loudnorm=I={_num(target)}:TP=-1.5:LRA=11")
        post.insert(1, "aresample=48000")
    else:
        post.insert(0, "alimiter=limit=0.97:level=false")
    filters.append(f"[{master}]{','.join(post)}[aout]")
    return filters


# ── Rendu projet ─────────────────────────────────────────────────────────────

def render_project(name: str, export_name: str | None = None, out_path: str | None = None,
                   dry_run: bool = False, fps_override: float | None = None,
                   formats: list[str] | None = None, draft: bool = False) -> str | list[str]:
    """Charge `projects/<name>/project.json` puis délègue à `render_project_data`."""
    from . import project as project_mod

    proj, project_dir = project_mod.load(name)
    if formats:
        outs = []
        for fmt in formats:
            outs.append(render_project_data(proj, project_dir, name, export_name=export_name,
                                            dry_run=dry_run, fps_override=fps_override,
                                            canvas_override=fmt, draft=draft))
        return outs
    return render_project_data(proj, project_dir, name, export_name=export_name,
                               out_path=out_path, dry_run=dry_run,
                               fps_override=fps_override, draft=draft)


def _jobs() -> int:
    env = os.environ.get("MD_JOBS")
    if env and env.isdigit():
        return max(1, int(env))
    return max(1, min(4, (os.cpu_count() or 2)))


_FINGERPRINT: str | None = None


def engine_fingerprint() -> str:
    """Empreinte du code de rendu : toute modification du moteur invalide le cache."""
    global _FINGERPRINT
    if _FINGERPRINT is None:
        h = hashlib.sha1(ENGINE_VERSION.encode())
        here = os.path.dirname(os.path.abspath(__file__))
        for mod in ("render.py", "text.py", "easing.py", "layout.py", "brand.py", "presets.py"):
            try:
                with open(os.path.join(here, mod), "rb") as f:
                    h.update(f.read())
            except OSError:
                pass
        _FINGERPRINT = h.hexdigest()[:12]
    return _FINGERPRINT


def _scene_key(scene: dict, canvas: dict, project_dir: str, quality: str) -> str:
    """Empreinte d'une scène : contenu + canvas + fichiers référencés + version moteur."""
    stamps = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("file", "background", "image", "font") and isinstance(v, str):
                    try:
                        p = resolve_path(v, project_dir) if k != "font" else text.find_font(v, project_dir)
                        st = os.stat(p)
                        stamps.append((v, st.st_mtime_ns, st.st_size))
                    except (SystemExit, OSError, FileNotFoundError):
                        pass
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(scene)
    blob = json.dumps({"scene": scene, "canvas": canvas, "q": quality, "v": engine_fingerprint(),
                       "files": stamps}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def _validate_timeline(scenes: list[dict], proj: dict) -> None:
    tr = proj.get("transitions", {}) or {}
    tr_type = tr.get("type", "fade")
    tr_dur = float(tr.get("duration", 0.5))
    if tr_type not in presets.XFADE_TRANSITIONS:
        _fail(f"Transition inconnue : {tr_type}. Dispo : {', '.join(presets.XFADE_TRANSITIONS)}")
    for k in range(len(scenes) - 1):
        t_k = scenes[k].get("transition") or {}
        ty = t_k.get("type", tr_type)
        du = float(t_k.get("duration", tr_dur))
        if ty not in presets.XFADE_TRANSITIONS:
            _fail(f"scène {k} : transition inconnue '{ty}'. Dispo : {', '.join(presets.XFADE_TRANSITIONS)}")
        shortest = min(float(scenes[k].get("duration", 5)), float(scenes[k + 1].get("duration", 5)))
        if du <= 0 or du >= shortest:
            _fail(f"scène {k} : transition de {du}s impossible (doit être > 0 et < {shortest}s, "
                  "la durée de la plus courte des deux scènes)")


def render_project_data(proj: dict, project_dir: str, name: str,
                        export_name: str | None = None, out_path: str | None = None,
                        dry_run: bool = False, fps_override: float | None = None,
                        canvas_override: str | dict | None = None,
                        draft: bool = False) -> str:
    """Compile un project.json **déjà chargé** en vidéo.

    Point d'entrée commun (CLI, Laboratoire, cockpit MCP) : un agent peut
    fabriquer un montage en mémoire, sans créer de dossier dans `projects/`.
    """
    canvas_ref = canvas_override or proj.get("canvas", presets.DEFAULT_CANVAS)
    try:
        canvas = presets.canvas(canvas_ref)
    except KeyError as exc:
        _fail(str(exc).strip("'\""))
    if draft:
        canvas["fps"] = min(float(canvas["fps"]), 15)
    if fps_override:
        canvas["fps"] = fps_override
    if int(canvas["width"]) % 2 or int(canvas["height"]) % 2:
        _fail("Le canvas doit avoir des dimensions paires (requis par H.264).")
    proj = layout.normalize(proj, canvas)

    export_name = "mp4-draft" if draft else (
        export_name or (proj.get("export") or {}).get("preset", presets.DEFAULT_EXPORT))
    try:
        exp = presets.export(export_name)
    except KeyError as exc:
        _fail(str(exc).strip("'\""))
    alpha_export = export_name in ("mov-alpha",) or (export_name == "webm-vp9" and proj.get("transparent"))

    scenes = proj.get("scenes") or [proj]
    if len(scenes) > 1 and alpha_export:
        _fail("L'export avec canal alpha ne supporte qu'une seule scène.")
    if len(scenes) > 1:
        _validate_timeline(scenes, proj)

    out_dir = os.path.join(REPO, ".cache", "rendus")
    os.makedirs(out_dir, exist_ok=True)
    canvas_tag = f"-{canvas_override}" if isinstance(canvas_override, str) else ""
    default_file = f"{name}{canvas_tag}-{export_name}{exp['ext']}"
    out_path = out_path or ((proj.get("export") or {}).get("filename") if not canvas_override else None)
    if out_path and not os.path.isabs(out_path):
        out_path = os.path.join(out_dir, out_path)
    out_path = out_path or os.path.join(out_dir, default_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base, ext = os.path.splitext(out_path)
    tmp_path = os.path.join(os.path.dirname(out_path), f".{os.path.basename(base)}.part{ext}")

    cache_dir = os.path.join(REPO, ".cache", name)
    os.makedirs(cache_dir, exist_ok=True)
    mix = dict(proj.get("mix") or {})
    if "loudnorm" in (proj.get("export") or {}):
        mix["loudnorm"] = proj["export"]["loudnorm"]
    elif exp.get("loudnorm") is not None and "loudnorm" not in mix:
        mix["loudnorm"] = exp["loudnorm"]

    t0 = time.time()
    if len(scenes) == 1:
        sc = scenes[0]
        D = float(sc.get("duration", canvas.get("duration", 5)))
        g, _, _ = build_scene_graph(sc, canvas, project_dir, cache_dir, 0,
                                    transparent_bg=alpha_export)
        tracks = collect_audio(proj, D, project_dir, [sc], [0.0]) if not alpha_export else []
        args: list[str] = []
        for inp in g.inputs:
            args += inp
        args += audio_input_args(tracks)
        filters = list(g.filters)
        if tracks:
            filters += audio_filters(tracks, g.n_video_inputs, D, mix)
        if export_name == "gif":
            filters += _gif_chain(canvas, exp)
            vmap = "[vgif]"
        else:
            vmap = "[vout]"
        args += ["-filter_complex", ";".join(filters), "-map", vmap]
        if tracks and export_name != "gif":
            args += ["-map", "[aout]"]
        args += ["-t", f"{D}", "-r", f"{canvas['fps']}"]
        args += exp["args"] if export_name != "gif" else []
        args += [tmp_path]
        _execute(args, dry_run)
    else:
        clips = _render_scenes(scenes, canvas, project_dir, cache_dir, dry_run, draft)
        starts, total = scene_starts(proj, scenes)
        tr = proj.get("transitions", {}) or {}
        tr_type = tr.get("type", "fade")
        tr_dur = float(tr.get("duration", 0.5))
        bounds = []
        for k in range(1, len(clips)):
            t_k = scenes[k - 1].get("transition") or {}
            bounds.append((t_k.get("type", tr_type), float(t_k.get("duration", tr_dur))))
        args = []
        for c, _ in clips:
            args += ["-i", c]
        tracks = collect_audio(proj, total, project_dir, scenes, starts)
        args += audio_input_args(tracks)

        filters = []
        prev_lbl = "0:v"
        for k in range(1, len(clips)):
            tk_type, tk_dur = bounds[k - 1]
            off = starts[k]
            lbl = f"x{k}" if k < len(clips) - 1 else "vchain"
            filters.append(f"[{prev_lbl}][{k}:v]xfade=transition={tk_type}:"
                           f"duration={_num(tk_dur)}:offset={_num(off)}[{lbl}]")
            prev_lbl = lbl
        if tracks:
            filters += audio_filters(tracks, len(clips), total, mix)
        filters.append("[vchain]format=yuv420p[vout]")
        if export_name == "gif":
            filters += _gif_chain(canvas, exp)
            vmap = "[vgif]"
        else:
            vmap = "[vout]"
        args += ["-filter_complex", ";".join(filters), "-map", vmap]
        if tracks and export_name != "gif":
            args += ["-map", "[aout]"]
        args += ["-t", f"{total}"]
        args += exp["args"] if export_name != "gif" else []
        args += [tmp_path]
        _execute(args, dry_run)

    if not dry_run:
        if not os.path.isfile(tmp_path) or os.path.getsize(tmp_path) == 0:
            _fail("ffmpeg n'a produit aucun fichier.")
        os.replace(tmp_path, out_path)
        info = probe.probe(out_path)
        manifest = {
            "projet": name,
            "sortie": os.path.relpath(out_path, REPO),
            "export": export_name,
            "canvas": canvas,
            "duree_s": info.get("duration"),
            "poids": probe.fmt_size(info.get("size", 0)),
            "rendu_le": time.strftime("%Y-%m-%d %H:%M:%S"),
            "temps_rendu_s": round(time.time() - t0, 1),
            "moteur": ENGINE_VERSION,
        }
        # Manifeste à côté du project.json (jamais à la racine du dépôt pour un
        # montage en mémoire) ; sinon à côté du livrable.
        man_dir = project_dir if os.path.abspath(project_dir) != REPO else os.path.dirname(out_path)
        try:
            with open(os.path.join(man_dir, "manifest.json" if man_dir == project_dir
                                   else os.path.basename(base) + ".manifest.json"), "w") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
        except OSError:
            pass
        print(f"\n✅ Sortie : {os.path.relpath(out_path, REPO)}  "
              f"({manifest['duree_s']}s · {manifest['poids']} · rendu en {manifest['temps_rendu_s']}s)")
    return out_path


def _render_scenes(scenes, canvas, project_dir, cache_dir, dry_run, draft):
    """Rend chaque scène en clip intermédiaire (parallèle + cache par empreinte)."""
    quality = "draft" if draft else "final"
    enc = (["-c:v", "libx264", "-crf", "28", "-preset", "ultrafast"] if draft else
           ["-c:v", "libx264", "-crf", "14", "-preset", "veryfast"])
    jobs = []
    for si, sc in enumerate(scenes):
        D_i = float(sc.get("duration", canvas.get("duration", 5)))
        key = _scene_key(sc, canvas, project_dir, quality)
        clip = os.path.join(cache_dir, f"scene{si}-{key}.mp4")
        jobs.append((si, sc, D_i, clip))

    def work(job):
        si, sc, D_i, clip = job
        if not dry_run and os.path.isfile(clip) and os.path.getsize(clip) > 0:
            print(f"── Scène {si + 1}/{len(scenes)} ({D_i}s) · cache ──")
            return clip, D_i
        g, _, _ = build_scene_graph(sc, canvas, project_dir, cache_dir, si)
        args = []
        for inp in g.inputs:
            args += inp
        part = clip + ".part.mp4"
        args += ["-filter_complex", ";".join(g.filters), "-map", "[vout]",
                 "-t", f"{D_i}", "-r", f"{canvas['fps']}", *enc,
                 "-pix_fmt", "yuv420p", "-an", part]
        print(f"── Scène {si + 1}/{len(scenes)} ({D_i}s) ──")
        _execute(args, dry_run)
        if not dry_run:
            os.replace(part, clip)
        return clip, D_i

    if dry_run or _jobs() == 1 or len(jobs) == 1:
        return [work(j) for j in jobs]
    with concurrent.futures.ThreadPoolExecutor(max_workers=_jobs()) as pool:
        return list(pool.map(work, jobs))


def _gif_chain(canvas: dict, exp: dict) -> list[str]:
    fps = exp.get("gif_fps", 15)
    w = min(exp.get("gif_width", 640), int(canvas["width"]))
    return [
        f"[vout]fps={fps},scale={w}:-1:flags=lanczos,split[g0][g1]",
        "[g0]palettegen=stats_mode=diff[pal]",
        "[g1][pal]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle[vgif]",
    ]


def _execute(args: list, dry_run: bool):
    if dry_run:
        ffmpeg.dry_run(args)
    else:
        ffmpeg.run(args)


def clone(proj: dict) -> dict:
    return copy.deepcopy(proj)
