"""Procédure d'installation d'éléments dans la bibliothèque assets/.

`./md install <fichier|dossier|URL>...`
  • polices   (.ttf/.otf)          → assets/fonts/    + validation Pillow
  • images    (.png/.jpg/.webp/…)  → assets/images/   + SVG converti en PNG
  • vidéos    (.mp4/.mov/.webm/…)  → assets/videos/   + analyse PyAV
  • audio     (.mp3/.wav/…)        → assets/audio/    + analyse PyAV
  • lottie    (.json contenant fr+layers) → assets/lottie/
  • archives  (.zip)               → décompressées puis re-routées
  • URL       → hôtes autorisés uniquement (github.com, codeload, api.github.com,
                pypi.org, files.pythonhosted.org, registry.npmjs.org)
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.parse
import urllib.request
import zipfile

from . import inventory, probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets")

ALLOWED_HOSTS = ("github.com", "codeload.github.com", "api.github.com", "objects.githubusercontent.com",
                 "raw.githubusercontent.com", "pypi.org", "files.pythonhosted.org", "registry.npmjs.org")

ROUTING = {
    "fonts": {".ttf", ".otf"},
    "images": {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif", ".svg"},
    "videos": {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".ogv"},
    "audio": {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".aiff"},
}


def _dest_for(path: str) -> str | None:
    ext = os.path.splitext(path)[1].lower()
    for folder, exts in ROUTING.items():
        if ext in exts:
            return os.path.join(ASSETS, folder)
    if ext == ".json":
        try:
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, dict) and "fr" in data and "layers" in data:
                return os.path.join(ASSETS, "lottie")
        except Exception:
            pass
    return None


def _download(url: str, dest_dir: str) -> str:
    host = urllib.parse.urlparse(url).hostname or ""
    if not any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS):
        raise SystemExit(f"ERREUR : hôte non autorisé : {host}\n  Hôtes autorisés : {', '.join(ALLOWED_HOSTS)}")
    name = os.path.basename(urllib.parse.urlparse(url).path) or "download"
    dest = os.path.join(dest_dir, name)
    print(f"⬇  Téléchargement : {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "MOTION-DESIGN-engine/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return dest


def _convert_svg(path: str) -> str | None:
    """Convertit un SVG en PNG via ImageMagick si disponible."""
    from shutil import which
    conv = which("convert")
    if not conv:
        return None
    import subprocess
    out = os.path.splitext(path)[0] + ".png"
    r = subprocess.run([conv, "-background", "none", path, out], capture_output=True, text=True)
    return out if r.returncode == 0 and os.path.exists(out) else None


def _install_one(path: str, installed: list[str]) -> None:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".zip":
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(path) as z:
                z.extractall(td)
            for root, _, files in os.walk(td):
                for f in files:
                    _install_one(os.path.join(root, f), installed)
        return

    dest_dir = _dest_for(path)
    if not dest_dir:
        print(f"⚠️  Ignoré (type non reconnu) : {os.path.basename(path)}")
        return
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(path))
    if os.path.abspath(path) != os.path.abspath(dest):
        shutil.copy2(path, dest)

    # Validations par type
    folder = os.path.basename(dest_dir)
    if folder == "fonts":
        from PIL import ImageFont
        try:
            ImageFont.truetype(dest, 20)
            print(f"✅ Police installée : assets/fonts/{os.path.basename(dest)}")
        except Exception as e:
            print(f"⚠️  Police illisible ({e}) : {dest}")
    elif folder == "images":
        if ext == ".svg":
            png = _convert_svg(dest)
            if png:
                print(f"✅ Image installée : assets/images/{os.path.basename(dest)} (+ {os.path.basename(png)})")
                installed.append(png)
            else:
                print(f"✅ Image installée (SVG brut, ImageMagick absent) : assets/images/{os.path.basename(dest)}")
        else:
            from PIL import Image
            with Image.open(dest) as im:
                print(f"✅ Image installée : assets/images/{os.path.basename(dest)} ({im.width}×{im.height})")
    elif folder in ("videos", "audio"):
        info = probe.probe(dest)
        if "error" in info:
            print(f"⚠️  Média copié mais illisible ({info['error'][:60]}) : {dest}")
        else:
            det = f"{info.get('width', '?')}×{info.get('height', '?')} · {info.get('duration', '?')}s" \
                if folder == "videos" else f"{info.get('duration', '?')}s"
            print(f"✅ {'Vidéo' if folder == 'videos' else 'Audio'} installé : "
                  f"assets/{folder}/{os.path.basename(dest)} ({det})")
    elif folder == "lottie":
        print(f"✅ Lottie installé : assets/lottie/{os.path.basename(dest)}")

    installed.append(dest)


def install(sources: list[str]) -> None:
    installed: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        for src in sources:
            if src.startswith(("http://", "https://")):
                path = _download(src, td)
            elif os.path.isdir(src):
                for root, _, files in os.walk(src):
                    for f in files:
                        _install_one(os.path.join(root, f), installed)
                continue
            elif os.path.exists(src):
                path = os.path.abspath(src)
            else:
                print(f"⚠️  Source introuvable : {src}")
                continue
            _install_one(path, installed)
    if installed:
        inventory.write_inventory()
        print(f"\n📦 {len(installed)} élément(s) installé(s). Utilisables dans project.json via assets/…")
    else:
        print("Aucun élément installé.")
