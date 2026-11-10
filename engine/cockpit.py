"""Cockpit : tableau de bord unique des capacités du moteur pour un agent pilote.

Toutes les portes d'entrée (CLI `./md cockpit`, serveur MCP `md_cockpit`,
API HTTP) lisent CE module : un agent voit exactement les mêmes instruments
quel que soit le moyen de connexion.
"""
from __future__ import annotations

import json
import os

from . import ads, brand, easing, ffmpeg, presets, render, text

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LAYER_FIELDS = {
    "communs": {
        "in / out": "fenêtre d'apparition (s, timeline de la scène)",
        "pos": "[x, y] centre du calque (px, '50%', '10vw'…) ou center|top|bottom|top_third|bottom_third",
        "anchor": "point du calque placé sur pos : " + ", ".join(render.ANCHORS),
        "anim": "entrée : " + ", ".join(render.ANIMS),
        "ease": "courbe d'entrée : " + ", ".join(easing.EASINGS),
        "anim_duration": "durée de l'entrée (défaut 0.6 s)",
        "exit": "sortie : " + ", ".join(render.EXITS),
        "exit_duration / exit_ease": "durée (0.45 s) / courbe (ease_in) de la sortie",
        "idle": "mouvement continu : " + ", ".join(render.IDLES),
        "idle_amplitude / idle_period": "amplitude (px, degrés ou facteur) / période (s)",
        "amplitude": "distance des glissés (px ; absent = hors-champ pour slide_*)",
        "opacity": "0 → 1", "rotate": "rotation fixe en degrés",
        "fade_in / fade_out": "durées de fondu (s)", "enabled": "false = calque ignoré",
    },
    "text": {"text": "contenu (\\n = saut de ligne)", "font": "fichier police (./md fonts)",
             "size": "corps (px ou '6vmin')", "color": "#RRGGBB", "align": "center|left|right",
             "max_width": "retour à la ligne auto", "line_height": "×, défaut 1.15",
             "letter_spacing": "px", "uppercase": "bool", "stroke_width / stroke_color": "contour",
             "shadow": "true ou {color, blur, offset:[x,y], opacity}",
             "box": "pastille derrière le texte {color, opacity, padding, radius}",
             "split": "texte cinétique : word|line|char", "stagger": "décalage entre morceaux (0.08 s)"},
    "counter": {"from / to": "valeurs", "count_duration": "durée du comptage",
                "prefix / suffix": "ex. '+' / ' €'", "decimals": "chiffres après la virgule",
                "ease": "courbe du comptage (expo_out)", "+ champs texte": "font, size, color…"},
    "shape": {"kind": ", ".join(text.SHAPE_KINDS), "w / h": "dimensions", "color": "#RRGGBB",
              "gradient": "[couleurs…] + angle", "radius": "coins (rect)",
              "stroke / stroke_color": "contour (rect, circle)", "ring_width": "épaisseur (ring)"},
    "image": {"file": "chemin ou jeton $logo", "fit": "contain|cover|stretch|original",
              "full_bleed": "plein cadre", "scale": "{w} et/ou {h}",
              "zoom": "intensité kenburns (0.22)"},
    "video": {"file": "rush", "src_in": "point d'entrée (s)", "speed": "vitesse (1.0)",
              "loop": "bouclage", "keep_audio": "garder le son du rush",
              "audio_role": "voice|music|sfx (si keep_audio)"},
    "audio": {"file": "son", "in / at": "départ dans la scène", "volume": "gain",
              "role": "sfx|voice|music", "src_in": "point d'entrée"},
}

PROJECT_FIELDS = {
    "canvas": "preset (" + ", ".join(presets.CANVAS_PRESETS) + ") ou {width, height, fps}",
    "brand": "kit de marque (brands/<nom>.json) → jetons $accent, $font.title, $logo…",
    "export": "{preset, filename, loudnorm (-14 ou true)}",
    "transitions": "{type, duration} par défaut entre scènes",
    "scenes": "[{duration, background, layers, transition}]",
    "background": "#hex, chemin d'image, {gradient:[…], angle, type:linear|radial} ou {image}",
    "audio": "musique : fichier, {file, volume, loop, fade_in, fade_out, at} ou liste",
    "voiceover": "voix off (même format) — la musique est baissée automatiquement dessous",
    "sfx": "effets sonores [{file, at, volume}]",
    "mix": "{duck: true, duck_ratio: 8, duck_threshold: 0.03, loudnorm: -14}",
}


def capabilities() -> dict:
    """Tout ce qu'un pilote peut utiliser, sans effet de bord ni réseau."""
    assets: dict[str, list] = {}
    for kind in ("images", "fonts", "audio", "videos", "lottie"):
        d = os.path.join(REPO, "assets", kind)
        assets[kind] = sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))) \
            if os.path.isdir(d) else []
    from . import project as project_mod
    return {
        "moteur": {"nom": "MOTION-DESIGN", "version": render.ENGINE_VERSION,
                   "ffmpeg": ffmpeg.version()},
        "canvas": {k: {"width": v["width"], "height": v["height"], "fps": v["fps"],
                       "usage": v["label"]} for k, v in presets.CANVAS_PRESETS.items()},
        "exports": {k: v["label"] for k, v in presets.EXPORT_PRESETS.items()},
        "zones_sures": presets.SAFE_ZONES,
        "durees_pub": presets.AD_DURATIONS,
        "transitions": presets.XFADE_TRANSITIONS,
        "animations": {"entrees": {a: render.ANIM_HELP.get(a, "") for a in render.ANIMS},
                       "sorties": render.EXITS, "idle": render.IDLES,
                       "easing": easing.EASINGS, "ancres": render.ANCHORS},
        "unites": ["120 (px)", "'120px'", "'50%'", "'8vw'", "'8vh'", "'6vmin'", "'6vmax'"],
        "calques": LAYER_FIELDS,
        "projet": PROJECT_FIELDS,
        "marques": brand.list_brands(),
        "pub": {"templates": ads.templates(), "brief": ads.schema()["fields"]},
        "polices": [f["file"] for f in text.list_fonts() if f["source"] == "assets"],
        "polices_systeme": len([f for f in text.list_fonts() if f["source"] != "assets"]),
        "assets": assets,
        "elements": {"usage": "./md elements chercher <mots> | prendre <source:nom>… | kit <nom> (MCP : md_elements_search, md_elements_get)",
                     "styles": ["3d", "couleur", "plat", "ligne", "plein"],
                     "kits": ["divertissement", "offre", "appareils", "interface"],
                     "destination": "assets/elements/ (+ LICENCES.md)"},
        "projets": [p["name"] for p in project_mod.list_projects()],
        "boucle_pilote": [
            "1. md_cockpit (ce tableau) puis md_guide si besoin",
            "2. md_ad_compose (brief pub) OU écrire un project.json",
            "3. md_lint → corriger errors/warnings",
            "4. md_preview → regarder les images clés, ajuster",
            "5. md_render (preset mp4-social, formats 9x16/1x1/16x9)",
        ],
    }


def guide() -> str:
    path = os.path.join(REPO, "docs", "PILOTE.md")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return json.dumps(capabilities(), ensure_ascii=False, indent=2)
