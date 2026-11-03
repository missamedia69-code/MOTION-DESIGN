"""Compositeur : transforme un échantillon de données en `project.json`.

C'est la traduction « protocole → montage déclaratif ». Aucun rendu ici :
le résultat est exactement le format consommé par `engine/render.py`, ce qui
garantit que le laboratoire réutilise le moteur existant (pas un moteur bis).
"""
from __future__ import annotations

from engine import presets


def _window(spec: dict, t_in: float, t_out: float | None = None) -> tuple[float, float]:
    """Fenêtre [in,out] toujours valide, même avec une scène très courte."""
    D = float(spec["duration"])
    start = max(0.0, min(float(t_in), D * 0.5))
    end = max(start + 0.3, float(t_out) if t_out is not None else D - 0.1)
    return round(start, 3), round(end, 3)


def _text(content: str, pos, size: int, color: str, spec: dict,
          anim: str = "fade_up", t_in: float = 0.2, t_out: float | None = None,
          max_width: int | None = None, align: str = "center") -> dict:
    start, end = _window(spec, t_in, t_out)
    layer = {
        "type": "text",
        "text": content,
        "font": spec["style"]["font"],
        "size": size,
        "color": color,
        "align": align,
        "pos": pos,
        "in": start,
        "out": end,
        "anim": anim,
        "anim_duration": 0.6,
    }
    if max_width:
        layer["max_width"] = max_width
    return layer


def _shape(kind: str, w: int, h: int, color: str, pos, anim: str,
           spec: dict, t_in: float = 0.3, radius: int = 0) -> dict:
    start, end = _window(spec, t_in)
    return {
        "type": "shape",
        "kind": kind,
        "w": max(2, int(w)),
        "h": max(2, int(h)),
        "radius": radius,
        "color": color,
        "pos": pos,
        "in": start,
        "out": end,
        "anim": anim,
        "anim_duration": 0.8,
    }


def _scene(layers: list[dict], spec: dict, transition: bool = True) -> dict:
    sc = {
        "duration": spec["duration"],
        "background": spec["style"]["background"],
        "layers": layers,
    }
    if transition:
        sc["transition"] = {"type": spec["style"]["transition"], "duration": 0.5}
    return sc


def _logo_layer(spec: dict, W: int, H: int, pos, size: int) -> dict | None:
    logo = (spec.get("brand") or {}).get("logo")
    if not logo:
        return None
    return {
        "type": "image",
        "file": logo,
        "fit": "contain",
        "scale": {"w": size},
        "pos": pos,
        "in": 0.2,
        "out": spec["duration"] - 0.1,
        "anim": "fade",
        "fade_in": 0.5,
    }


def compose(spec: dict) -> dict:
    """Retourne un project.json complet prêt pour `render_project_data`."""
    canvas = presets.canvas(spec["canvas"])
    W, H = int(canvas["width"]), int(canvas["height"])
    style, nar, metrics = spec["style"], spec["narrative"], spec["metrics"]
    big = max(36, int(W * 0.062))
    mid = max(24, int(W * 0.036))
    small = max(16, int(W * 0.022))
    scenes: list[dict] = []

    # ── Scène 1 · Hook ────────────────────────────────────────────────────
    hook = [
        _shape("rect", W * 0.46, 8, style["accent"], [W / 2, H * 0.30],
               "grow_x", spec, t_in=0.2, radius=4),
        _text(nar["hook"], [W / 2, H * 0.44], big, style["text"], spec,
              anim="fade_up", max_width=int(W * 0.84)),
        _text(spec["title"], [W / 2, H * 0.56], mid, style["muted"], spec,
              anim="fade", t_in=0.6, max_width=int(W * 0.84)),
    ]
    logo = _logo_layer(spec, W, H, [W / 2, H * 0.78], int(W * 0.16))
    if logo:
        hook.append(logo)
    scenes.append(_scene(hook, spec))

    # ── Scène 2 · KPI ─────────────────────────────────────────────────────
    kpi = [
        _text("TOTAL", [W / 2, H * 0.22], small, style["muted"], spec,
              anim="fade", t_in=0.2),
        _text(f"{metrics['total']:g}", [W / 2, H * 0.44], int(big * 1.7),
              style["accent"], spec, anim="pop", t_in=0.3),
        _text(nar["insight"], [W / 2, H * 0.64], mid, style["text"], spec,
              anim="fade_up", t_in=0.7, max_width=int(W * 0.84)),
        _text(f"{metrics['count']} points · pic : {metrics['best_label']}",
              [W / 2, H * 0.78], small, style["muted"], spec, anim="fade", t_in=1.0),
    ]
    scenes.append(_scene(kpi, spec))

    # ── Scène 3 · Barres (les données brutes deviennent du motion) ─────────
    rows = spec["data"]
    n = len(rows)
    left, right = W * 0.12, W * 0.88
    slot = (right - left) / n
    baseline = H * 0.72
    max_h = H * 0.40
    peak = metrics["max"] or 1
    bars: list[dict] = [
        _text("LES DONNÉES", [W / 2, H * 0.14], mid, style["text"], spec,
              anim="fade", t_in=0.1),
    ]
    for i, row in enumerate(rows):
        cx = left + slot * (i + 0.5)
        bh = max(6, int(row["value"] / peak * max_h))
        bw = max(6, int(slot * 0.52))
        bars.append(_shape("rect", bw, bh, style["accent"],
                           [cx, baseline - bh / 2], "grow_y", spec,
                           t_in=0.2 + i * 0.08, radius=6))
        bars.append(_text(row["label"], [cx, baseline + H * 0.055], small,
                          style["muted"], spec, anim="fade", t_in=0.5 + i * 0.06))
        bars.append(_text(f"{row['value']:g}", [cx, baseline - bh - H * 0.035],
                          small, style["text"], spec, anim="fade",
                          t_in=0.6 + i * 0.06))
    scenes.append(_scene(bars, spec))

    # ── Scène 4 · CTA ─────────────────────────────────────────────────────
    cta = [
        _shape("rect", W * 0.62, H * 0.13, style["accent"],
               [W / 2, H * 0.62], "pop", spec, t_in=0.5, radius=int(H * 0.06)),
        _text(nar["cta"], [W / 2, H * 0.43], big, style["text"], spec,
              anim="fade_up", max_width=int(W * 0.84)),
        _text(spec["title"], [W / 2, H * 0.62], mid, style["background"], spec,
              anim="fade", t_in=0.8),
    ]
    logo = _logo_layer(spec, W, H, [W / 2, H * 0.82], int(W * 0.14))
    if logo:
        cta.append(logo)
    scenes.append(_scene(cta, spec, transition=False))

    return {
        "name": spec["name"],
        "title": spec["title"],
        "version": 2,
        "canvas": spec["canvas"],
        "export": {"preset": spec["preset"]},
        "transitions": {"type": style["transition"], "duration": 0.5},
        "_lab": {
            "source": "lab/spec.py",
            "rows": metrics["count"],
            "scene_types": ["hook", "kpi", "bars", "cta"],
            "metrics": metrics,
        },
        "scenes": scenes,
    }
