"""Inventaire des instruments du laboratoire (ce que l'IA peut utiliser)."""
from __future__ import annotations

import os

from engine import ffmpeg, presets, render, text

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inventory() -> dict:
    """État des instruments, sans effet de bord ni appel réseau."""
    assets = {"images": [], "fonts": [], "audio": [], "videos": []}
    for kind in assets:
        d = os.path.join(REPO, "assets", kind)
        if os.path.isdir(d):
            assets[kind] = sorted(
                f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))
            )
    return {
        "laboratoire": "MOTION-DESIGN Lab",
        "version": "1.0",
        "entree": "spec.json (données + style + narration)",
        "sortie": "MP4 / GIF / WebM + manifeste d'expérience",
        "scene_types": ["hook", "kpi", "bars", "cta"],
        "instruments": {
            "canvas": {k: v for k, v in presets.CANVAS_PRESETS.items()},
            "exports": {k: v["label"] for k, v in presets.EXPORT_PRESETS.items()},
            "transitions": list(presets.XFADE_TRANSITIONS),
            "animations": list(render.ANIMS),
            "fonts": [f["file"] for f in text.list_fonts()],
            "assets": assets,
        },
        "voix": {
            "commande": "./md vo <projet>",
            "backends": ["edge-tts", "voxcpm"],
            "note": "hors sandbox : service Microsoft / modèles HuggingFace",
        },
        "moteur": {
            "ffmpeg": ffmpeg.version(),
            "polices_disponibles": len(text.list_fonts()),
        },
        "limites": {"max_rows": 12, "duree_scene_s": [1, 10]},
    }
