"""Contrôle qualité d'un montage, AVANT de consommer du temps de rendu.

Trois niveaux :
  errors   → le rendu échouera ou sera faux (fichier absent, anim inconnue…)
  warnings → le rendu passera mais la pub sera moins efficace (texte trop
             petit, hors zone sûre TikTok/Reels, contraste faible, accroche
             tardive…)
  infos    → conseils (pas de musique, durée hors standards pub…)

Chaque remarque a un `where` précis (ex. `scenes[1].layers[3]`) pour qu'un
agent pilote puisse corriger directement le bon champ.
"""
from __future__ import annotations

import os
import re

from . import easing, layout, presets, render, text

HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    """Ratio de contraste WCAG entre deux couleurs #RRGGBB."""
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def _bg_color(bg) -> str | None:
    if isinstance(bg, str) and HEX_RE.match(bg):
        return bg if bg.startswith("#") else "#" + bg
    if isinstance(bg, dict) and bg.get("gradient"):
        stops = [s for s in bg["gradient"] if isinstance(s, str) and HEX_RE.match(s)]
        if stops:
            # couleur moyenne du dégradé
            rgb = [sum(int(s.lstrip("#")[i:i + 2], 16) for s in stops) // len(stops) for i in (0, 2, 4)]
            return "#%02x%02x%02x" % tuple(rgb)
    return None


def lint(proj: dict, project_dir: str, canvas_override=None) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    infos: list[dict] = []

    def err(where, msg):
        errors.append({"where": where, "message": msg})

    def warn(where, msg):
        warnings.append({"where": where, "message": msg})

    def info(where, msg):
        infos.append({"where": where, "message": msg})

    canvas_ref = canvas_override or proj.get("canvas", presets.DEFAULT_CANVAS)
    try:
        canvas = presets.canvas(canvas_ref)
    except KeyError as exc:
        err("canvas", str(exc).strip("'\""))
        return {"ok": False, "errors": errors, "warnings": warnings, "infos": infos}
    W, H = int(canvas["width"]), int(canvas["height"])
    if W % 2 or H % 2:
        err("canvas", "dimensions impaires (H.264 exige des dimensions paires)")
    try:
        norm = layout.normalize(proj, canvas)
    except SystemExit as exc:
        err("projet", str(exc))
        return {"ok": False, "errors": errors, "warnings": warnings, "infos": infos}

    preset = (norm.get("export") or {}).get("preset", presets.DEFAULT_EXPORT)
    if preset not in presets.EXPORT_PRESETS:
        err("export.preset", f"preset inconnu '{preset}' ({', '.join(presets.EXPORT_PRESETS)})")

    multi = bool(norm.get("scenes"))
    scenes = norm.get("scenes") or [norm]
    starts, total = render.scene_starts(norm, scenes) if multi else ([0.0], float(norm.get("duration", 5)))
    tr = norm.get("transitions") or {}
    if multi and tr.get("type", "fade") not in presets.XFADE_TRANSITIONS:
        err("transitions.type", f"transition inconnue '{tr.get('type')}'")
    safe = presets.SAFE_ZONES.get(canvas_ref if isinstance(canvas_ref, str) else "")
    first_text_at = None
    n_layers = 0
    ref = min(W, H)

    for si, sc in enumerate(scenes):
        sw = f"scenes[{si}]" if multi else "projet"
        try:
            D = float(sc.get("duration", 0))
        except (TypeError, ValueError):
            D = 0
        if D <= 0:
            err(sw, "'duration' manquante ou <= 0")
            continue
        bg = sc.get("background", "#000000")
        if isinstance(bg, str) and not HEX_RE.match(bg) and bg != "transparent":
            try:
                render.resolve_path(bg, project_dir)
            except SystemExit as exc:
                err(f"{sw}.background", str(exc))
        bg_hex = _bg_color(bg)
        plates: list[tuple[float, float, float, float, str]] = []  # formes pleines déjà posées
        if multi and si < len(scenes) - 1:
            t = sc.get("transition") or {}
            ty = t.get("type", tr.get("type", "fade"))
            du = float(t.get("duration", tr.get("duration", 0.5)))
            if ty not in presets.XFADE_TRANSITIONS:
                err(f"{sw}.transition.type", f"transition inconnue '{ty}'")
            nxt = float(scenes[si + 1].get("duration", 0) or 0)
            if du <= 0 or du >= min(D, nxt or D):
                err(f"{sw}.transition.duration", f"{du}s doit être > 0 et < durée des scènes voisines")

        for li, layer in enumerate(sc.get("layers", [])):
            if layer.get("enabled") is False:
                continue
            n_layers += 1
            lw = f"{sw}.layers[{li}]"
            lt = layer.get("type")
            pos = layer.get("pos")
            if lt not in render.LAYER_TYPES:
                err(lw, f"type '{lt}' inconnu ({'|'.join(render.LAYER_TYPES)})")
                continue
            for key, allowed in (("anim", render.ANIMS), ("exit", render.EXITS),
                                 ("idle", render.IDLES), ("anchor", render.ANCHORS)):
                if key in layer and layer[key] not in allowed:
                    err(f"{lw}.{key}", f"'{layer[key]}' inconnu ({', '.join(allowed)})")
            for key in ("ease", "exit_ease"):
                if key in layer and layer[key] not in easing.EASINGS:
                    err(f"{lw}.{key}", f"'{layer[key]}' inconnu ({', '.join(easing.EASINGS)})")
            try:
                t_in = float(layer.get("in", 0))
                t_out = float(layer.get("out", D))
            except (TypeError, ValueError):
                err(lw, "'in'/'out' doivent être des nombres")
                continue
            if t_in >= D:
                err(f"{lw}.in", f"in={t_in}s ≥ durée de la scène ({D}s) : calque invisible")
            if t_out > D + 1e-6:
                warn(f"{lw}.out", f"out={t_out}s dépasse la scène ({D}s) : coupé à {D}s")
            if t_out <= t_in:
                err(lw, "out <= in")
            if lt in ("image", "video", "audio"):
                try:
                    render.resolve_path(layer.get("file"), project_dir)
                except SystemExit as exc:
                    err(f"{lw}.file", str(exc))
            if lt in ("text", "counter"):
                if lt == "text" and not str(layer.get("text", "")).strip():
                    err(f"{lw}.text", "texte vide")
                if layer.get("font") and not text.font_exists(layer["font"], project_dir):
                    warn(f"{lw}.font", f"police '{layer['font']}' introuvable : repli sur la police par défaut")
                size = float(layer.get("size", 64))
                if size < ref * 0.028:
                    warn(f"{lw}.size", f"{size:.0f}px : illisible sur mobile (min. conseillé "
                                       f"{ref * 0.028:.0f}px, soit ~2.8vmin)")
                if lt == "text":
                    abs_t = starts[si] + t_in if si < len(starts) else t_in
                    first_text_at = abs_t if first_text_at is None else min(first_text_at, abs_t)
                    try:
                        lay = text._TextLayout(layer, project_dir)
                        if lay.block_w > W * 0.94:
                            warn(f"{lw}", f"texte de {lay.block_w}px plus large que l'écran ({W}px) : "
                                          "ajouter max_width ou réduire size")
                        if layer.get("split") and lay.token_count(layer["split"]) > text.MAX_TOKENS:
                            err(f"{lw}.split", f"trop de morceaux (> {text.MAX_TOKENS})")
                    except Exception as exc:  # noqa: BLE001
                        err(lw, f"texte non rendu : {exc}")
                color = layer.get("color", "#ffffff")
                under = bg_hex
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    try:
                        tx, ty = float(pos[0]), float(pos[1])
                        for px, py, pw, ph, pc in plates:
                            if abs(tx - px) <= pw / 2 and abs(ty - py) <= ph / 2:
                                under = pc if pc.startswith("#") else "#" + pc
                    except (TypeError, ValueError):
                        pass
                if under and isinstance(color, str) and HEX_RE.match(color) and not layer.get("box"):
                    c = contrast(color if color.startswith("#") else "#" + color, under)
                    if c < 3:
                        warn(f"{lw}.color", f"contraste {c}:1 avec le fond {under} (min. 3:1 ; "
                                            "4.5:1 pour les petits textes)")
            if lt == "counter":
                for k in ("to", "from"):
                    if k in layer and not isinstance(layer[k], (int, float)):
                        err(f"{lw}.{k}", "nombre attendu")
            if lt == "image" and (layer.get("full_bleed") or str(layer.get("anim", "")).startswith("kenburns")):
                bg_hex = None  # fond photo : contraste non mesurable
            if lt == "shape" and isinstance(pos, (list, tuple)) and isinstance(layer.get("color"), str) \
                    and HEX_RE.match(layer["color"]) and not layer.get("gradient") \
                    and float(layer.get("opacity", 1)) >= 0.6:
                try:
                    plates.append((float(pos[0]), float(pos[1]), float(layer.get("w", 400)),
                                   float(layer.get("h", 8)), layer["color"]))
                except (TypeError, ValueError):
                    pass
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                try:
                    x, y = float(pos[0]), float(pos[1])
                except (TypeError, ValueError):
                    err(f"{lw}.pos", "coordonnées invalides")
                    continue
                if not (0 <= x <= W and 0 <= y <= H) and layer.get("anim") not in ("kenburns_in",):
                    warn(f"{lw}.pos", f"centre ({x:.0f},{y:.0f}) hors du cadre {W}x{H}")
                elif safe and lt in ("text", "counter") and (
                        y < H * safe["top"] or y > H * (1 - safe["bottom"])):
                    warn(f"{lw}.pos", f"texte en zone masquée par l'interface ({safe['note']})")

    for key in ("audio", "voiceover", "sfx"):
        val = norm.get(key)
        items = val if isinstance(val, list) else [val] if val else []
        for k, item in enumerate(items):
            f = item if isinstance(item, str) else (item or {}).get("file")
            try:
                render.resolve_path(f, project_dir)
            except SystemExit as exc:
                err(f"{key}[{k}].file" if isinstance(val, list) else f"{key}.file", str(exc))

    # ── Conseils publicitaires ──
    if first_text_at is None:
        info("projet", "aucun texte : une pub sans message écrit performe mal en lecture muette")
    elif first_text_at > 1.5:
        warn("projet", f"accroche tardive : premier texte à {first_text_at:.1f}s (viser < 1,5s, "
                       "85 % des vidéos sociales sont vues sans le son)")
    has_audio = bool(norm.get("audio") or norm.get("voiceover") or norm.get("sfx")) or any(
        l.get("type") == "audio" for sc in scenes for l in sc.get("layers", []))
    if not has_audio:
        info("audio", "pas de son : ajouter une musique (audio) et/ou une voix off (voiceover)")
    std = presets.AD_DURATIONS.get(canvas_ref if isinstance(canvas_ref, str) else "")
    if std and not any(abs(total - d) <= 1.0 for d in std) and total < max(std) + 1:
        info("durée", f"{total:.1f}s ; formats pub courants pour ce canvas : "
                      f"{', '.join(f'{d}s' for d in std)}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "summary": {"canvas": f"{W}x{H}@{canvas['fps']}", "scenes": len(scenes),
                    "layers": n_layers, "duration_s": round(total, 2),
                    "preset": preset},
    }


def format_report(rep: dict) -> str:
    lines = []
    s = rep.get("summary") or {}
    if s:
        lines.append(f"── Contrôle qualité · {s['canvas']} · {s['scenes']} scène(s) · "
                     f"{s['layers']} calque(s) · {s['duration_s']}s ──")
    for k, icon in (("errors", "✖"), ("warnings", "⚠"), ("infos", "ℹ")):
        for item in rep.get(k, []):
            lines.append(f"{icon} {item['where']} : {item['message']}")
    lines.append("✅ Prêt à rendre." if rep["ok"] else "❌ Corriger les erreurs avant le rendu.")
    return "\n".join(lines)


def lint_file(path: str) -> dict:
    import json
    with open(path, encoding="utf-8") as f:
        proj = json.load(f)
    return lint(proj, os.path.dirname(os.path.abspath(path)))
