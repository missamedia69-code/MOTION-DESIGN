"""Gestion des projets : création, chargement, validation, liste."""
from __future__ import annotations

import json
import os
import re
import shutil

from . import presets

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(REPO, "projects")
TEMPLATES_DIR = os.path.join(REPO, "templates")

LAYER_TYPES = {"image", "text", "video", "shape", "audio", "counter"}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "projet"


def project_dir(name: str) -> str:
    return os.path.join(PROJECTS_DIR, slugify(name))


def list_projects() -> list[dict]:
    out = []
    if not os.path.isdir(PROJECTS_DIR):
        return out
    for d in sorted(os.listdir(PROJECTS_DIR)):
        pj = os.path.join(PROJECTS_DIR, d, "project.json")
        if os.path.isfile(pj):
            try:
                with open(pj) as f:
                    data = json.load(f)
                out.append({"name": d, "title": data.get("title", d),
                            "canvas": data.get("canvas", presets.DEFAULT_CANVAS)})
            except Exception:
                out.append({"name": d, "title": "(project.json illisible)", "canvas": "?"})
    return out


def new(name: str, canvas_preset: str = presets.DEFAULT_CANVAS,
        template: str = "base") -> str:
    name = slugify(name)
    dest = project_dir(name)
    if os.path.exists(dest):
        raise SystemExit(f"ERREUR : le projet '{name}' existe déjà (projects/{name}).")
    src = os.path.join(TEMPLATES_DIR, template)
    if not os.path.isdir(src):
        avail = [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]
        raise SystemExit(f"ERREUR : template '{template}' introuvable. Dispo : {', '.join(avail)}")
    shutil.copytree(src, dest)
    pj_path = os.path.join(dest, "project.json")
    with open(pj_path) as f:
        raw = f.read()
    raw = raw.replace("{{NAME}}", name)
    data = json.loads(raw)
    data["name"] = name
    if canvas_preset != presets.DEFAULT_CANVAS or isinstance(data.get("canvas"), str):
        data["canvas"] = canvas_preset
    with open(pj_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Projet créé : projects/{name}/ (canvas {canvas_preset}, template {template})")
    print(f"   → éditer projects/{name}/project.json puis : ./md render {name}")
    return dest


def load(name: str) -> tuple[dict, str]:
    pdir = project_dir(name)
    pj = os.path.join(pdir, "project.json")
    if not os.path.isfile(pj):
        avail = ", ".join(p["name"] for p in list_projects()) or "(aucun)"
        raise SystemExit(f"ERREUR : projet '{name}' introuvable. Projets dispo : {avail}")
    with open(pj) as f:
        data = json.load(f)
    validate(data, pdir)
    return data, pdir


def validate(data: dict, pdir: str) -> None:
    def fail(msg):
        raise SystemExit(f"ERREUR de validation ({data.get('name', '?')}) : {msg}")

    c = data.get("canvas", presets.DEFAULT_CANVAS)
    if isinstance(c, str):
        try:
            presets.canvas(c)
        except KeyError as e:
            fail(str(e))
    scenes = data.get("scenes") or [data]
    for si, sc in enumerate(scenes):
        if "duration" not in sc and "duration" not in (data.get("canvas") if isinstance(data.get("canvas"), dict) else {}):
            if "duration" not in sc:
                fail(f"scène {si} : 'duration' manquante")
        for li, layer in enumerate(sc.get("layers", [])):
            lt = layer.get("type")
            if lt not in LAYER_TYPES:
                fail(f"scène {si} calque {li} : type '{lt}' invalide ({', '.join(sorted(LAYER_TYPES))})")
            if lt in ("image", "video", "audio") and not layer.get("file"):
                fail(f"scène {si} calque {li} : 'file' manquant")
            if lt == "text" and "text" not in layer:
                fail(f"scène {si} calque {li} : 'text' manquant")
            try:
                t_in = float(layer.get("in", 0) or 0)
                t_out = layer.get("out")
                if t_out is not None and float(t_out) <= t_in:
                    fail(f"scène {si} calque {li} : out <= in")
            except (TypeError, ValueError):
                fail(f"scène {si} calque {li} : 'in'/'out' doivent être des nombres")


def save(name: str, data: dict, overwrite: bool = True) -> str:
    """Écrit projects/<name>/project.json (écriture atomique, validation préalable)."""
    name = slugify(name)
    dest = project_dir(name)
    pj = os.path.join(dest, "project.json")
    if os.path.exists(pj) and not overwrite:
        raise SystemExit(f"ERREUR : le projet '{name}' existe déjà (overwrite=false).")
    if not isinstance(data, dict):
        raise SystemExit("ERREUR : project.json doit être un objet JSON.")
    data = dict(data)
    data["name"] = name
    os.makedirs(dest, exist_ok=True)
    validate(data, dest)
    tmp = pj + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, pj)
    return pj
