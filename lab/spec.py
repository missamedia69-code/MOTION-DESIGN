"""Protocole d'entrée du Laboratoire : validation des échantillons de données.

Un « échantillon » est un JSON minimal (titre + lignes de données). Tout le
reste (style, durées, format, transitions) est optionnel et normalisé ici, pour
qu'une IA puisse soumettre le moins d'informations possible.
"""
from __future__ import annotations

import copy
import math
import os
import re

from engine import presets

MAX_ROWS = 12
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

DEFAULTS = {
    "canvas": "16x9",
    "preset": "mp4-web",
    "duration": 3.0,
    "style": {
        "background": "#0B1020",
        "text": "#FFFFFF",
        "accent": "#FFD400",
        "muted": "#9FB4D8",
        "font": "Montserrat-Bold.ttf",
        "transition": "fade",
    },
    "narrative": {
        "hook": "Données en mouvement",
        "insight": "Une lecture claire des chiffres",
        "cta": "Passez à l'action",
    },
}


def example() -> dict:
    """Échantillon complet, prêt à soumettre (sert aussi d'exemple pour l'IA)."""
    return {
        "name": "demo-ventes",
        "title": "Ventes T3 2026",
        "canvas": "720p",
        "preset": "mp4-web",
        "duration": 2.5,
        "style": {
            "background": "#0B1020",
            "text": "#FFFFFF",
            "accent": "#FFD400",
            "muted": "#9FB4D8",
            "font": "Montserrat-Bold.ttf",
            "transition": "fade",
        },
        "brand": {"logo": "assets/images/demo-logo.png"},
        "narrative": {
            "hook": "Vos chiffres prennent vie",
            "insight": "Une progression nette sur la période",
            "cta": "Passez à la vitesse supérieure",
        },
        "data": [
            {"label": "Jan", "value": 12},
            {"label": "Fév", "value": 19},
            {"label": "Mar", "value": 15},
            {"label": "Avr", "value": 28},
            {"label": "Mai", "value": 34},
        ],
    }


def schema() -> dict:
    """Description lisible par un agent (sans dépendance jsonschema)."""
    return {
        "required": ["data"],
        "fields": {
            "name": "identifiant slug (auto-dérivé de title si absent)",
            "title": "titre lisible",
            "data": f"liste de 1 à {MAX_ROWS} lignes {{label: string, value: number >= 0}}",
            "canvas": f"un de : {', '.join(presets.CANVAS_PRESETS)}",
            "preset": f"un de : {', '.join(presets.EXPORT_PRESETS)}",
            "duration": "durée d'une scène en secondes (1 à 10)",
            "style.background / text / accent / muted": "couleurs #RRGGBB",
            "style.font": "nom de fichier dans assets/fonts/",
            "style.transition": "une transition xfade (voir ./md presets)",
            "brand.logo": "chemin d'une image existante (optionnel)",
            "narrative.hook / insight / cta": "textes des scènes (optionnels)",
        },
        "output": "MP4 (ou GIF/WebM selon preset) + manifeste d'expérience JSON",
        "example": example(),
    }


def _fail(msg: str) -> None:
    raise SystemExit(f"ERREUR de protocole : {msg}")


def validate(raw: dict) -> dict:
    """Valide et normalise un échantillon. Retourne un spec autonome."""
    if not isinstance(raw, dict):
        _fail("un objet JSON est attendu")

    spec = copy.deepcopy(DEFAULTS)
    for key in ("style", "narrative"):
        spec[key].update(raw.get(key) or {})
    for key in ("name", "title", "canvas", "preset", "duration", "data", "brand"):
        if key in raw and raw[key] is not None:
            spec[key] = copy.deepcopy(raw[key])

    # ── Données (cœur de l'entrée) ──
    rows = spec.get("data")
    if not isinstance(rows, list) or not rows:
        _fail("'data' doit être une liste non vide de {label, value}")
    if len(rows) > MAX_ROWS:
        _fail(f"au plus {MAX_ROWS} lignes de données (reçu {len(rows)})")
    clean = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            _fail(f"ligne {i} : objet {{label, value}} attendu")
        label = str(row.get("label", "")).strip() or f"Ligne {i}"
        value = row.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _fail(f"ligne {i} : 'value' doit être un nombre")
        if not math.isfinite(float(value)) or float(value) < 0:
            _fail(f"ligne {i} : 'value' doit être un nombre fini >= 0")
        clean.append({"label": label[:24], "value": float(value)})
    spec["data"] = clean

    # ── Identité ──
    title = str(spec.get("title") or "Expérience motion").strip()
    spec["title"] = title
    name = str(spec.get("name") or "").strip().lower() or re.sub(
        r"[^a-z0-9]+", "-", title.lower()).strip("-") or "experience"
    if not SLUG_RE.match(name):
        _fail(f"name '{name}' invalide (minuscules, chiffres, tirets)")
    spec["name"] = name

    # ── Instruments disponibles ──
    if spec["canvas"] not in presets.CANVAS_PRESETS:
        _fail(f"canvas '{spec['canvas']}' inconnu ({', '.join(presets.CANVAS_PRESETS)})")
    if spec["preset"] not in presets.EXPORT_PRESETS:
        _fail(f"preset '{spec['preset']}' inconnu ({', '.join(presets.EXPORT_PRESETS)})")
    try:
        duration = float(spec["duration"])
    except (TypeError, ValueError):
        _fail("'duration' doit être un nombre")
    spec["duration"] = max(1.0, min(10.0, duration))

    style = spec["style"]
    for key in ("background", "text", "accent", "muted"):
        if not HEX_RE.match(str(style.get(key, ""))):
            _fail(f"style.{key} doit être au format #RRGGBB")
    if style.get("transition") not in presets.XFADE_TRANSITIONS:
        _fail(f"style.transition '{style.get('transition')}' inconnue")
    if style.get("font"):
        # On tolère une police absente : le moteur retombera sur son défaut.
        style["font"] = os.path.basename(str(style["font"]))

    logo = (spec.get("brand") or {}).get("logo")
    if logo:
        from engine import render as render_mod
        try:
            spec["brand"]["logo"] = render_mod.resolve_path(str(logo), os.getcwd())
        except SystemExit:
            _fail(f"brand.logo introuvable : {logo}")
    else:
        spec.pop("brand", None)

    for key in ("hook", "insight", "cta"):
        spec["narrative"][key] = str(spec["narrative"].get(key, ""))[:160]

    # ── Métriques dérivées (lues par le compositeur) ──
    values = [r["value"] for r in clean]
    spec["metrics"] = {
        "count": len(values),
        "total": round(sum(values), 2),
        "max": round(max(values), 2),
        "mean": round(sum(values) / len(values), 2),
        "best_label": clean[values.index(max(values))]["label"],
    }
    return spec
