"""Kits de marque : couleurs, polices, logo réutilisables dans tous les projets.

Un kit vit dans `brands/<nom>.json`. Un projet y fait référence avec
`"brand": "<nom>"` (ou un objet inline) et utilise des jetons :

    "color": "$accent"          → brand.colors.accent
    "font":  "$font.title"      → brand.fonts.title
    "file":  "$logo"            → brand.logo

Les jetons inconnus provoquent une erreur explicite (pas de rendu silencieux).
"""
from __future__ import annotations

import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDS_DIR = os.path.join(REPO, "brands")
TOKEN_RE = re.compile(r"^\$[a-z][a-z0-9_]*(\.[a-z0-9_]+)?$")


def list_brands() -> list[dict]:
    out = []
    if not os.path.isdir(BRANDS_DIR):
        return out
    for f in sorted(os.listdir(BRANDS_DIR)):
        if f.endswith(".json"):
            try:
                data = load(f[:-5])
                out.append({"name": f[:-5], "title": data.get("title", f[:-5]),
                            "colors": data.get("colors", {}), "fonts": data.get("fonts", {}),
                            "logo": data.get("logo")})
            except SystemExit as exc:
                out.append({"name": f[:-5], "error": str(exc)})
    return out


def load(ref) -> dict:
    """Charge un kit (nom → brands/<nom>.json, ou dict inline)."""
    if isinstance(ref, dict):
        return ref
    path = os.path.join(BRANDS_DIR, f"{ref}.json")
    if not os.path.isfile(path):
        avail = ", ".join(b[:-5] for b in os.listdir(BRANDS_DIR) if b.endswith(".json")) \
            if os.path.isdir(BRANDS_DIR) else ""
        raise SystemExit(f"ERREUR : kit de marque '{ref}' introuvable (brands/). Dispo : {avail or 'aucun'}")
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as exc:
            raise SystemExit(f"ERREUR : brands/{ref}.json illisible ({exc})") from exc


def tokens(kit: dict) -> dict[str, str]:
    """Aplatit un kit en jetons : $accent, $color.accent, $font.title, $logo…"""
    out: dict[str, str] = {}
    for k, v in (kit.get("colors") or {}).items():
        out[f"${k}"] = v
        out[f"$color.{k}"] = v
    for k, v in (kit.get("fonts") or {}).items():
        out[f"$font.{k}"] = v
    if kit.get("logo"):
        out["$logo"] = kit["logo"]
    for k, v in (kit.get("assets") or {}).items():
        out[f"$asset.{k}"] = v
    for k, v in (kit.get("texts") or {}).items():
        out[f"$text.{k}"] = v
    return out


def apply(obj, toks: dict[str, str], where: str = ""):
    """Remplace récursivement les chaînes '$jeton' par leur valeur."""
    if isinstance(obj, dict):
        return {k: apply(v, toks, f"{where}.{k}" if where else k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [apply(v, toks, f"{where}[{i}]") for i, v in enumerate(obj)]
    if isinstance(obj, str) and TOKEN_RE.match(obj):
        if obj not in toks:
            raise SystemExit(f"ERREUR : jeton de marque inconnu {obj} ({where}). "
                             f"Dispo : {', '.join(sorted(toks)) or 'aucun (pas de brand)'}")
        return toks[obj]
    return obj


def resolve_project(proj: dict) -> dict:
    """Retourne une copie du projet avec les jetons de marque résolus."""
    ref = proj.get("brand")
    if not ref:
        # Aucun kit : on vérifie quand même qu'aucun jeton n'est utilisé.
        return apply(proj, {}) if _has_tokens(proj) else proj
    kit = load(ref)
    body = {k: v for k, v in proj.items() if k != "brand"}
    out = apply(body, tokens(kit))
    out["brand"] = ref
    return out


def _has_tokens(obj) -> bool:
    if isinstance(obj, dict):
        return any(_has_tokens(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_tokens(v) for v in obj)
    return isinstance(obj, str) and bool(TOKEN_RE.match(obj))
