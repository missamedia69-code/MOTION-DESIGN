"""Normalisation d'un projet avant rendu : jetons de marque + unités relatives.

Unités acceptées partout où une dimension est attendue :

    120        → pixels
    "120px"    → pixels
    "50%"      → pourcentage de l'axe du champ (x/largeur → W, y/hauteur → H)
    "8vw" / "8vh"     → % de la largeur / hauteur du canvas
    "6vmin" / "6vmax" → % du plus petit / plus grand côté

Grâce à ces unités, un même projet se décline en 9x16, 1x1 et 16x9 sans
réécrire les positions (`./md render <nom> --formats 9x16,1x1,16x9`).
"""
from __future__ import annotations

import copy
import re

from . import brand

_UNIT_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(px|%|vw|vh|vmin|vmax)?\s*$")

# Champ → axe de référence pour '%'
_FIELDS_W = ("w", "size", "max_width", "amplitude", "radius", "stroke_width",
             "letter_spacing", "stroke")
_FIELDS_H = ("h",)


def to_px(value, axis: str, W: int, H: int, where: str = ""):
    """Convertit une valeur (nombre ou chaîne avec unité) en pixels."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return value
    m = _UNIT_RE.match(value)
    if not m:
        raise SystemExit(f"ERREUR : unité invalide '{value}' ({where}). "
                         "Formats : 120, '120px', '50%', '8vw', '8vh', '6vmin', '6vmax'")
    num, unit = float(m.group(1)), m.group(2) or "px"
    ref = {"px": None, "%": W if axis == "x" else H, "vw": W, "vh": H,
           "vmin": min(W, H), "vmax": max(W, H)}[unit]
    return num if ref is None else num * ref / 100.0


def _layer_units(layer: dict, W: int, H: int, where: str) -> dict:
    out = dict(layer)
    pos = out.get("pos")
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        out["pos"] = [to_px(pos[0], "x", W, H, f"{where}.pos[0]"),
                      to_px(pos[1], "y", W, H, f"{where}.pos[1]")]
    for k in _FIELDS_W:
        if k in out:
            out[k] = to_px(out[k], "x", W, H, f"{where}.{k}")
    for k in _FIELDS_H:
        if k in out:
            out[k] = to_px(out[k], "y", W, H, f"{where}.{k}")
    if isinstance(out.get("scale"), dict):
        sc = dict(out["scale"])
        if "w" in sc:
            sc["w"] = to_px(sc["w"], "x", W, H, f"{where}.scale.w")
        if "h" in sc:
            sc["h"] = to_px(sc["h"], "y", W, H, f"{where}.scale.h")
        out["scale"] = sc
    if isinstance(out.get("box"), dict):
        box = dict(out["box"])
        pad = box.get("padding")
        if isinstance(pad, (list, tuple)):
            box["padding"] = [to_px(pad[0], "x", W, H), to_px(pad[1], "y", W, H)]
        elif pad is not None:
            box["padding"] = to_px(pad, "x", W, H)
        if "radius" in box:
            box["radius"] = to_px(box["radius"], "x", W, H)
        out["box"] = box
    return out


def normalize(proj: dict, canvas: dict) -> dict:
    """Retourne une copie prête à rendre (jetons résolus, unités en px)."""
    W, H = int(canvas["width"]), int(canvas["height"])
    out = brand.resolve_project(copy.deepcopy(proj))
    if out.get("scenes"):
        for si, sc in enumerate(out["scenes"]):
            sc["layers"] = [_layer_units(l, W, H, f"scenes[{si}].layers[{li}]")
                            for li, l in enumerate(sc.get("layers", []))]
    else:
        out["layers"] = [_layer_units(l, W, H, f"layers[{li}]")
                         for li, l in enumerate(out.get("layers", []))]
    return out
