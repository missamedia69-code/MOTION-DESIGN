"""Inventaire automatique de la bibliothèque assets/."""
from __future__ import annotations

import os
import time

from . import probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets")
OUT = os.path.join(ASSETS, "INVENTORY.md")


def scan() -> list[dict]:
    items = []
    for root, dirs, files in os.walk(ASSETS):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in sorted(files):
            if f.startswith(".") or f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            info = probe.probe(p)
            info["folder"] = os.path.relpath(root, ASSETS)
            items.append(info)
    return items


def write_inventory() -> str:
    items = scan()
    lines = ["# Inventaire des assets", "",
             f"_Généré automatiquement par `./md inventory` — {time.strftime('%Y-%m-%d %H:%M')}_", ""]
    by_folder: dict[str, list[dict]] = {}
    for it in items:
        by_folder.setdefault(it["folder"], []).append(it)
    for folder in sorted(by_folder):
        lines.append(f"## {folder}/")
        lines.append("")
        lines.append("| Fichier | Type | Détails | Poids |")
        lines.append("|---|---|---|---|")
        for it in by_folder[folder]:
            d = []
            if it.get("width"):
                d.append(f"{it['width']}×{it['height']}")
            if it.get("duration"):
                d.append(f"{it['duration']}s")
            if it.get("fps"):
                d.append(f"{it['fps']} fps")
            if it.get("codec"):
                d.append(it["codec"])
            if it.get("error"):
                d.append(f"⚠️ {it['error'][:40]}")
            lines.append(f"| `{it['file']}` | {it['kind']} | {' · '.join(d) or '—'} | {probe.fmt_size(it['size'])} |")
        lines.append("")
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Inventaire mis à jour : assets/INVENTORY.md ({len(items)} fichiers)")
    return OUT


def print_inventory() -> None:
    items = scan()
    if not items:
        print("assets/ est vide. Installez des éléments : ./md install <fichier|url>")
        return
    print(f"{'FICHIER':<40} {'TYPE':<7} {'DÉTAILS':<32} POIDS")
    print("─" * 92)
    for it in items:
        d = []
        if it.get("width"):
            d.append(f"{it['width']}×{it['height']}")
        if it.get("duration"):
            d.append(f"{it['duration']}s")
        if it.get("codec"):
            d.append(it["codec"])
        print(f"{os.path.join(it['folder'], it['file']):<40} {it['kind']:<7} {' · '.join(d):<32} {probe.fmt_size(it['size'])}")
